# -*- coding: utf-8 -*-

import collections
import json
import logging
import threading
import time
import urllib.error
import urllib.request
import uuid

from werkzeug.wrappers import Response as WerkzeugResponse

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

_GATEWAY_TIMEOUT = 60  # seconds
_MAX_MESSAGE_LENGTH = 8000  # characters
_RATE_LIMIT_WINDOW = 60  # seconds
_RATE_LIMIT_MAX_REQUESTS = 20  # per user per window

# Per-user rate limit state (uid → deque of timestamps)
_rate_limit_lock = threading.Lock()
_rate_limit_buckets = collections.defaultdict(collections.deque)

# System prompt for Pulser (Odoo assistant)
_SYSTEM_PROMPT = (
    "You are Pulser, an AI assistant for Odoo 18 ERP by InsightPulseAI. "
    "You help users with Philippine finance, BIR tax compliance, HR, "
    "inventory, sales, and general ERP questions. "
    "Answer concisely. Use markdown formatting. "
    "If you need to reference Odoo records, mention the model and ID."
)


class CopilotGatewayController(http.Controller):
    """Controller bridging the systray copilot UI to Azure Foundry / OpenAI.

    Supports two backends:
    - Track 1: Azure OpenAI Chat Completions (managed identity or API key)
    - Track 2: Custom gateway endpoint (for Foundry Agent SDK / agent-platform)

    Auth resolution (Track 1):
    1. Managed Identity (DefaultAzureCredential) — production default, keyless
    2. API key (AZURE_FOUNDRY_API_KEY env var) — dev/rollback fallback
    3. Falls back to Track 2 (custom gateway) if neither is available
    """

    # ------------------------------------------------------------------
    # Rate limiting & validation
    # ------------------------------------------------------------------

    def _check_rate_limit(self, uid):
        """Enforce per-user rate limiting. Returns True if allowed."""
        now = time.monotonic()
        with _rate_limit_lock:
            bucket = _rate_limit_buckets[uid]
            # Purge expired entries
            while bucket and bucket[0] < now - _RATE_LIMIT_WINDOW:
                bucket.popleft()
            if len(bucket) >= _RATE_LIMIT_MAX_REQUESTS:
                return False
            bucket.append(now)
            return True

    def _validate_message(self, message):
        """Validate message content. Returns error string or None."""
        if not message or not message.strip():
            return 'Message cannot be empty.'
        if len(message) > _MAX_MESSAGE_LENGTH:
            return 'Message exceeds maximum length of %d characters.' % _MAX_MESSAGE_LENGTH
        return None

    def _validate_context(self, context):
        """Validate context fields. Returns sanitized context dict."""
        ctx = {}
        model = context.get('context_model', '')
        if model:
            # Only allow valid Odoo model name patterns
            if not all(c.isalnum() or c in '._ ' for c in model):
                model = ''
        ctx['context_model'] = model

        res_id = context.get('context_res_id', 0)
        try:
            ctx['context_res_id'] = max(0, int(res_id))
        except (ValueError, TypeError):
            ctx['context_res_id'] = 0

        ctx['surface'] = context.get('surface', 'erp')
        return ctx

    def _check_conversation_access(self, conversation):
        """Check user + company access to a conversation. Returns error or None."""
        if conversation.user_id != request.env.user:
            return 'Access denied to this conversation.'
        if conversation.company_id and conversation.company_id != request.env.company:
            return 'Access denied: conversation belongs to a different company.'
        return None

    def _audit_log(self, event_type, **kwargs):
        """Write an audit log entry. Swallows errors to never block requests."""
        try:
            ip = request.httprequest.remote_addr or ''
            request.env['ipai.copilot.audit'].log_event(
                event_type, ip_address=ip, **kwargs,
            )
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_gateway_url(self):
        """Read gateway URL from ir.config_parameter."""
        return (
            request.env['ir.config_parameter']
            .sudo()
            .get_param('ipai.copilot.gateway_url', 'http://localhost:8088')
        )

    def _is_enabled(self):
        """Check if copilot is enabled via ir.config_parameter."""
        val = (
            request.env['ir.config_parameter']
            .sudo()
            .get_param('ipai.copilot.enabled', 'True')
        )
        return val.lower() in ('true', '1', 'yes')

    def _get_mode(self):
        """Read copilot operating mode."""
        return (
            request.env['ir.config_parameter']
            .sudo()
            .get_param('ipai.copilot.mode', 'PROD-ADVISORY')
        )

    def _get_backend(self):
        """Determine which backend and auth mode to use.

        Auth resolution order:
          1. Managed Identity (DefaultAzureCredential) — production default
          2. API key (AZURE_FOUNDRY_API_KEY env var) — dev/rollback fallback
          3. Custom gateway URL — agent-platform track

        Returns ('openai', endpoint, auth_headers) or ('gateway', url, None).
        """
        import os
        endpoint = os.getenv(
            'AZURE_OPENAI_ENDPOINT',
            'https://ipai-copilot-resource.openai.azure.com',
        )

        # Priority 1: Managed Identity (keyless — recommended for production)
        try:
            from azure.identity import DefaultAzureCredential
            credential = DefaultAzureCredential()
            token = credential.get_token('https://cognitiveservices.azure.com/.default')
            _logger.info('copilot-auth: managed-identity (keyless)')
            return 'openai', endpoint, {'Authorization': 'Bearer ' + token.token}
        except Exception as mi_err:
            _logger.debug('copilot-auth: managed-identity unavailable (%s)', mi_err)

        # Priority 2: API key fallback (dev convenience)
        api_key = os.getenv('AZURE_FOUNDRY_API_KEY', '')
        if api_key:
            _logger.info('copilot-auth: api-key fallback')
            return 'openai', endpoint, {'api-key': api_key}

        # Priority 3: Custom gateway
        _logger.info('copilot-auth: gateway fallback')
        return 'gateway', self._get_gateway_url(), None

    def _call_openai(self, messages, correlation_id):
        """Call Azure OpenAI Chat Completions API.

        Args:
            messages: List of {role, content} dicts.
            correlation_id: Correlation ID for tracing.

        Returns:
            (response_dict, latency_ms) on success.
        """
        _, endpoint, auth_headers = self._get_backend()
        model = (
            request.env['ir.config_parameter']
            .sudo()
            .get_param('ipai.copilot.model', 'gpt-4.1')
        )
        # Azure OpenAI uses /openai/deployments/{model}/chat/completions
        base = endpoint.rstrip('/')
        if '/openai/v1' in base:
            base = base.split('/openai/v1')[0]
        url = (
            f"{base}/openai/deployments/{model}"
            f"/chat/completions?api-version=2024-10-21"
        )

        payload = {
            'model': model,
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 2048,
        }
        body = json.dumps(payload).encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'X-Correlation-Id': correlation_id,
        }
        # Merge auth headers (Bearer token or api-key)
        if auth_headers:
            headers.update(auth_headers)

        req = urllib.request.Request(url, data=body, headers=headers, method='POST')
        start = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=_GATEWAY_TIMEOUT) as resp:
                latency_ms = int((time.monotonic() - start) * 1000)
                data = json.loads(resp.read().decode('utf-8', errors='replace'))
                content = ''
                if data.get('choices'):
                    content = data['choices'][0].get('message', {}).get('content', '')
                return {'content': content, 'request_id': correlation_id}, latency_ms
        except urllib.error.HTTPError as e:
            latency_ms = int((time.monotonic() - start) * 1000)
            error_body = ''
            try:
                error_body = e.read().decode('utf-8', errors='replace')
            except Exception:
                pass
            _logger.warning(
                'OpenAI HTTP %d: %s (latency=%dms)', e.code, error_body[:300], latency_ms,
            )
            raise ValueError('OpenAI returned HTTP %d: %s' % (e.code, e.reason))
        except urllib.error.URLError as e:
            raise ValueError('OpenAI unreachable: %s' % e.reason)
        except Exception as e:
            _logger.exception('OpenAI unexpected error')
            raise ValueError('OpenAI error: %s' % str(e))

    def _call_gateway(self, gateway_url, payload, correlation_id):
        """HTTP POST to the agent-platform gateway (Track 2).

        Returns (response_dict, latency_ms) on success.
        Raises ValueError on failure with a user-friendly message.
        """
        body = json.dumps(payload).encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Correlation-Id': correlation_id,
            'X-Copilot-Mode': self._get_mode(),
        }

        req = urllib.request.Request(
            gateway_url, data=body, headers=headers, method='POST',
        )

        start = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=_GATEWAY_TIMEOUT) as resp:
                latency_ms = int((time.monotonic() - start) * 1000)
                resp_body = resp.read().decode('utf-8', errors='replace')
                try:
                    data = json.loads(resp_body)
                except (json.JSONDecodeError, TypeError):
                    data = {'content': resp_body}
                return data, latency_ms
        except urllib.error.HTTPError as e:
            latency_ms = int((time.monotonic() - start) * 1000)
            error_body = ''
            try:
                error_body = e.read().decode('utf-8', errors='replace')
            except Exception:
                pass
            _logger.warning(
                'Copilot gateway HTTP %d: %s (latency=%dms)',
                e.code, error_body[:200], latency_ms,
            )
            raise ValueError(
                'Gateway returned HTTP %d: %s' % (e.code, e.reason)
            )
        except urllib.error.URLError as e:
            _logger.warning('Copilot gateway unreachable: %s', e.reason)
            raise ValueError(
                'Gateway unreachable at %s — %s' % (gateway_url, e.reason)
            )
        except Exception as e:
            _logger.exception('Copilot gateway unexpected error')
            raise ValueError('Gateway error: %s' % str(e))

    def _dispatch_message(self, message, context, conversation, correlation_id):
        """Route message to the appropriate backend.

        Returns (response_dict, latency_ms).
        """
        backend_type, url, _ = self._get_backend()

        if backend_type == 'openai':
            # Build OpenAI messages array with system prompt + context
            messages = [{'role': 'system', 'content': _SYSTEM_PROMPT}]

            # Add context hint if available
            ctx_model = context.get('context_model') or ''
            ctx_id = context.get('context_res_id') or 0
            if ctx_model:
                messages.append({
                    'role': 'system',
                    'content': 'User is viewing %s (ID: %s) in Odoo.' % (ctx_model, ctx_id),
                })

            # Add conversation history (last 10 messages)
            if conversation:
                history = request.env['ipai.copilot.message'].sudo().search(
                    [('conversation_id', '=', conversation.id)],
                    order='create_date asc',
                    limit=10,
                )
                for msg in history:
                    if msg.role in ('user', 'assistant'):
                        messages.append({'role': msg.role, 'content': msg.content or ''})

            messages.append({'role': 'user', 'content': message})
            return self._call_openai(messages, correlation_id)
        else:
            # Track 2: Custom gateway
            payload = {
                'conversation_id': str(conversation.id) if conversation else '',
                'correlation_id': correlation_id,
                'message': message,
                'user': {
                    'uid': request.env.user.id,
                    'name': request.env.user.name,
                    'login': request.env.user.login,
                },
                'context': context,
                'mode': self._get_mode(),
            }
            return self._call_gateway(url, payload, correlation_id)

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # File upload proxy
    # ------------------------------------------------------------------

    @http.route(
        '/ipai/copilot/upload',
        type='http',
        auth='user',
        methods=['POST'],
        csrf=True,
    )
    def upload_files(self, **kwargs):
        """Accept file uploads from the chat UI and store as ir.attachment.

        Files are saved to ir.attachment (Odoo-native). The attachment IDs
        are returned so the chat endpoint can reference them. The actual
        forwarding to agent-platform happens when the chat message is sent
        with attachment_ids.

        Returns JSON: {"attachment_ids": [1, 2, ...], "files": [...]}
        """
        if not self._is_enabled():
            return WerkzeugResponse(
                json.dumps({'error': True, 'message': 'Copilot is disabled.'}),
                content_type='application/json',
                status=503,
            )

        uid = request.env.uid
        if not self._check_rate_limit(uid):
            return WerkzeugResponse(
                json.dumps({'error': True, 'message': 'Rate limit exceeded.'}),
                content_type='application/json',
                status=429,
            )

        ALLOWED_MIMES = {
            'image/png', 'image/jpeg', 'image/webp', 'image/gif',
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }
        MAX_SIZE = 50 * 1024 * 1024  # 50 MB
        MAX_FILES = 10

        uploaded_files = request.httprequest.files.getlist('files')
        if not uploaded_files:
            return WerkzeugResponse(
                json.dumps({'error': True, 'message': 'No files provided.'}),
                content_type='application/json',
                status=400,
            )
        if len(uploaded_files) > MAX_FILES:
            return WerkzeugResponse(
                json.dumps({'error': True, 'message': 'Too many files (max %d).' % MAX_FILES}),
                content_type='application/json',
                status=400,
            )

        import base64
        attachment_ids = []
        file_info = []

        Attachment = request.env['ir.attachment']
        for f in uploaded_files:
            if f.content_type not in ALLOWED_MIMES:
                continue
            data = f.read()
            if len(data) > MAX_SIZE:
                continue

            att = Attachment.create({
                'name': f.filename,
                'datas': base64.b64encode(data),
                'mimetype': f.content_type,
                'res_model': 'ipai.copilot.conversation',
                'res_id': 0,
            })
            attachment_ids.append(att.id)
            file_info.append({
                'id': att.id,
                'name': f.filename,
                'mimetype': f.content_type,
                'size': len(data),
            })

        self._audit_log('file_upload', user_id=uid,
                        payload_summary='%d files uploaded' % len(attachment_ids))

        return WerkzeugResponse(
            json.dumps({
                'attachment_ids': attachment_ids,
                'files': file_info,
            }),
            content_type='application/json',
            status=200,
        )

    @http.route(
        '/ipai/copilot/chat',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def chat(self, conversation_id=None, message='', context=None):
        """Send a message to the copilot and return the response.

        Args:
            conversation_id: Optional ID of an existing conversation.
            message: The user's message text.
            context: Optional dict with context_model, context_res_id, etc.

        Returns:
            dict with keys: conversation_id, content, role, request_id,
            latency_ms, error (if any).
        """
        if not self._is_enabled():
            return {
                'error': True,
                'message': 'Copilot is disabled. Enable it in Settings.',
            }

        # Rate limiting
        uid = request.env.uid
        if not self._check_rate_limit(uid):
            self._audit_log('rate_limited', user_id=uid)
            return {
                'error': True,
                'message': 'Rate limit exceeded. Please wait before sending more messages.',
            }

        # Input validation
        validation_error = self._validate_message(message)
        if validation_error:
            self._audit_log('validation_error', user_id=uid,
                            error_detail=validation_error)
            return {
                'error': True,
                'message': validation_error,
            }

        context = self._validate_context(context or {})
        Conversation = request.env['ipai.copilot.conversation']
        Message = request.env['ipai.copilot.message']

        # Get or create conversation
        if conversation_id:
            conversation = Conversation.browse(conversation_id).exists()
            if not conversation:
                return {
                    'error': True,
                    'message': 'Conversation not found.',
                }
            # Security: user + company access check
            access_error = self._check_conversation_access(conversation)
            if access_error:
                self._audit_log('access_denied', user_id=uid,
                                conversation_id=conversation.id,
                                error_detail=access_error)
                return {
                    'error': True,
                    'message': access_error,
                }
        else:
            conv_vals = {
                'name': (message or '')[:80] or 'New Conversation',
            }
            if context.get('context_model'):
                conv_vals['context_model'] = context['context_model']
            if context.get('context_res_id'):
                conv_vals['context_res_id'] = int(context['context_res_id'])
            conversation = Conversation.create(conv_vals)

        # Persist user message
        user_msg = Message.create({
            'conversation_id': conversation.id,
            'role': 'user',
            'content': message.strip(),
        })

        # Dispatch to backend (OpenAI or custom gateway)
        correlation_id = conversation.gateway_correlation_id or str(uuid.uuid4())
        ctx = {
            'context_model': context.get('context_model') or conversation.context_model or '',
            'context_res_id': context.get('context_res_id') or conversation.context_res_id or 0,
            'surface': context.get('surface', 'erp'),
        }

        self._audit_log('chat_request', user_id=uid,
                        conversation_id=conversation.id,
                        correlation_id=correlation_id,
                        payload_summary=message[:200])

        try:
            resp_data, latency_ms = self._dispatch_message(
                message.strip(), ctx, conversation, correlation_id
            )
        except ValueError as e:
            # Persist error as system message for audit trail
            Message.create({
                'conversation_id': conversation.id,
                'role': 'system',
                'content': 'Gateway error: %s' % str(e),
            })
            self._audit_log('chat_error', user_id=uid,
                            conversation_id=conversation.id,
                            correlation_id=correlation_id,
                            error_detail=str(e)[:500])
            return {
                'error': True,
                'message': str(e),
                'conversation_id': conversation.id,
            }

        # Extract response content
        assistant_content = (
            resp_data.get('content')
            or resp_data.get('message')
            or resp_data.get('response')
            or 'No response content received.'
        )
        tool_calls = resp_data.get('tool_calls')
        request_id = resp_data.get('request_id', correlation_id)

        # Persist assistant message
        assistant_msg = Message.create({
            'conversation_id': conversation.id,
            'role': 'assistant',
            'content': assistant_content,
            'tool_calls': tool_calls,
            'latency_ms': latency_ms,
            'request_id': request_id,
        })

        self._audit_log('chat_response', user_id=uid,
                        conversation_id=conversation.id,
                        correlation_id=correlation_id,
                        latency_ms=latency_ms)

        return {
            'conversation_id': conversation.id,
            'content': assistant_content,
            'role': 'assistant',
            'request_id': request_id,
            'latency_ms': latency_ms,
            'tool_calls': tool_calls,
        }

    @http.route(
        '/ipai/copilot/stream',
        type='http',
        auth='user',
        methods=['POST'],
        csrf=True,
    )
    def stream_chat(self, **kwargs):
        """Stream a copilot response via Server-Sent Events.

        Accepts form-encoded or JSON body with: message, conversation_id,
        context_model, context_res_id, surface, csrf_token.

        Returns text/event-stream with data chunks as they arrive from
        the gateway. Falls back to a single-event response if the gateway
        does not support streaming.
        """
        if not self._is_enabled():
            return WerkzeugResponse(
                'data: {"error": true, "message": "Copilot is disabled."}\n\n',
                content_type='text/event-stream',
                status=200,
            )

        # Rate limiting
        uid = request.env.uid
        if not self._check_rate_limit(uid):
            self._audit_log('rate_limited', user_id=uid)
            return WerkzeugResponse(
                'data: {"error": true, "message": "Rate limit exceeded."}\n\n',
                content_type='text/event-stream',
                status=429,
            )

        # Parse input — accept both JSON body and form params
        try:
            body = json.loads(request.httprequest.get_data(as_text=True))
        except (json.JSONDecodeError, TypeError):
            body = {}
        message = body.get('message') or kwargs.get('message', '')
        conversation_id = body.get('conversation_id') or kwargs.get('conversation_id')
        raw_context = {
            'context_model': body.get('context_model') or kwargs.get('context_model', ''),
            'context_res_id': body.get('context_res_id') or kwargs.get('context_res_id', 0),
            'surface': body.get('surface') or kwargs.get('surface', 'erp'),
        }
        context = self._validate_context(raw_context)

        message = (message or '').strip()
        validation_error = self._validate_message(message)
        if validation_error:
            self._audit_log('validation_error', user_id=uid,
                            error_detail=validation_error)
            return WerkzeugResponse(
                'data: %s\n\n' % json.dumps({'error': True, 'message': validation_error}),
                content_type='text/event-stream',
                status=200,
            )

        Conversation = request.env['ipai.copilot.conversation']
        Message = request.env['ipai.copilot.message']

        # Get or create conversation
        if conversation_id:
            try:
                conversation_id = int(conversation_id)
            except (ValueError, TypeError):
                conversation_id = None

        if conversation_id:
            conversation = Conversation.browse(conversation_id).exists()
            if not conversation:
                return WerkzeugResponse(
                    'data: {"error": true, "message": "Conversation not found."}\n\n',
                    content_type='text/event-stream',
                    status=200,
                )
            access_error = self._check_conversation_access(conversation)
            if access_error:
                self._audit_log('access_denied', user_id=uid,
                                conversation_id=conversation.id,
                                error_detail=access_error)
                return WerkzeugResponse(
                    'data: %s\n\n' % json.dumps({'error': True, 'message': access_error}),
                    content_type='text/event-stream',
                    status=200,
                )
        else:
            conv_vals = {
                'name': message[:80] or 'New Conversation',
            }
            if context.get('context_model'):
                conv_vals['context_model'] = context['context_model']
            if context.get('context_res_id'):
                conv_vals['context_res_id'] = int(context['context_res_id'])
            conversation = Conversation.create(conv_vals)

        # Persist user message before streaming
        Message.create({
            'conversation_id': conversation.id,
            'role': 'user',
            'content': message,
        })

        correlation_id = conversation.gateway_correlation_id or str(uuid.uuid4())
        gateway_url = self._get_gateway_url()
        payload = {
            'conversation_id': str(conversation.id),
            'correlation_id': correlation_id,
            'message': message,
            'user': {
                'uid': request.env.user.id,
                'name': request.env.user.name,
                'login': request.env.user.login,
            },
            'context': {
                'model': context.get('context_model') or conversation.context_model or '',
                'res_id': context.get('context_res_id') or conversation.context_res_id or 0,
                'surface': context.get('surface', 'erp'),
            },
            'mode': self._get_mode(),
            'stream': True,
        }

        self._audit_log('stream_request', user_id=uid,
                        conversation_id=conversation.id,
                        correlation_id=correlation_id,
                        payload_summary=message[:200])

        # Capture env references before generator (request context may expire)
        env = request.env
        conv_id = conversation.id
        audit_uid = uid

        def generate():
            """SSE generator that proxies gateway streaming response."""
            full_content = ''
            start = time.monotonic()
            error_occurred = False
            disconnected = False

            try:
                import requests as http_requests
            except ImportError:
                # Fall back to urllib if requests not available
                http_requests = None

            try:
                # Send initial event with conversation_id
                yield 'data: %s\n\n' % json.dumps({
                    'type': 'start',
                    'conversation_id': conv_id,
                })

                if http_requests:
                    resp = http_requests.post(
                        gateway_url,
                        json=payload,
                        stream=True,
                        timeout=60,
                        headers={
                            'Content-Type': 'application/json',
                            'Accept': 'text/event-stream',
                            'X-Correlation-Id': correlation_id,
                            'X-Copilot-Mode': payload['mode'],
                        },
                    )
                    resp.raise_for_status()

                    for line in resp.iter_lines(decode_unicode=True):
                        if not line:
                            continue
                        # Handle SSE format from gateway
                        if line.startswith('data: '):
                            chunk_data = line[6:]
                            try:
                                chunk = json.loads(chunk_data)
                                token = chunk.get('content') or chunk.get('token') or chunk.get('delta', '')
                            except (json.JSONDecodeError, TypeError):
                                token = chunk_data
                            if token:
                                full_content += token
                                yield 'data: %s\n\n' % json.dumps({
                                    'type': 'chunk',
                                    'content': token,
                                    'full_content': full_content,
                                })
                        elif not line.startswith(':'):
                            # Non-SSE response — treat entire line as content
                            full_content += line
                            yield 'data: %s\n\n' % json.dumps({
                                'type': 'chunk',
                                'content': line,
                                'full_content': full_content,
                            })
                else:
                    # Fallback: non-streaming via urllib
                    try:
                        data, latency_ms = self._call_gateway(
                            gateway_url, payload, correlation_id
                        )
                        full_content = (
                            data.get('content')
                            or data.get('message')
                            or data.get('response')
                            or 'No response content received.'
                        )
                        yield 'data: %s\n\n' % json.dumps({
                            'type': 'chunk',
                            'content': full_content,
                            'full_content': full_content,
                        })
                    except ValueError as e:
                        error_occurred = True
                        yield 'data: %s\n\n' % json.dumps({
                            'type': 'error',
                            'message': str(e),
                        })

            except GeneratorExit:
                # Client disconnected mid-stream
                disconnected = True
                _logger.info('Client disconnected during stream (conv=%s)', conv_id)
            except Exception as e:
                error_occurred = True
                _logger.warning('Copilot stream error: %s', e)
                yield 'data: %s\n\n' % json.dumps({
                    'type': 'error',
                    'message': 'Stream error: %s' % str(e),
                })

            latency_ms = int((time.monotonic() - start) * 1000)

            # Persist assistant message after stream completes
            # On disconnect with partial content, still persist what we have
            if full_content and not error_occurred:
                try:
                    with env.registry.cursor() as cr:
                        new_env = env(cr=cr)
                        new_env['ipai.copilot.message'].create({
                            'conversation_id': conv_id,
                            'role': 'assistant',
                            'content': full_content,
                            'latency_ms': latency_ms,
                            'request_id': correlation_id,
                        })
                        # Audit log within same cursor
                        event = 'stream_disconnect' if disconnected else 'stream_complete'
                        new_env['ipai.copilot.audit'].log_event(
                            event,
                            user_id=audit_uid,
                            conversation_id=conv_id,
                            correlation_id=correlation_id,
                            latency_ms=latency_ms,
                        )
                except Exception as e:
                    _logger.warning('Failed to persist streamed response: %s', e)
            elif error_occurred:
                try:
                    with env.registry.cursor() as cr:
                        new_env = env(cr=cr)
                        new_env['ipai.copilot.audit'].log_event(
                            'stream_error',
                            user_id=audit_uid,
                            conversation_id=conv_id,
                            correlation_id=correlation_id,
                            latency_ms=latency_ms,
                        )
                except Exception:
                    pass

            if not disconnected:
                # Send done event
                yield 'data: %s\n\n' % json.dumps({
                    'type': 'done',
                    'latency_ms': latency_ms,
                    'conversation_id': conv_id,
                })

        return WerkzeugResponse(
            generate(),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
            },
        )

    @http.route(
        '/ipai/copilot/conversations/create',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def create_conversation(self, name='', context_model='', context_res_id=0):
        """Create a new conversation.

        Returns:
            dict with conversation_id, name, gateway_correlation_id.
        """
        if not self._is_enabled():
            return {
                'error': True,
                'message': 'Copilot is disabled.',
            }

        vals = {
            'name': name or 'New Conversation',
        }
        if context_model:
            vals['context_model'] = context_model
        if context_res_id:
            vals['context_res_id'] = int(context_res_id)

        conversation = request.env['ipai.copilot.conversation'].create(vals)
        return {
            'conversation_id': conversation.id,
            'name': conversation.name,
            'gateway_correlation_id': conversation.gateway_correlation_id,
        }

    @http.route(
        '/ipai/copilot/conversations/list',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def list_conversations(self, state='active', limit=20, offset=0):
        """Return current user's conversations.

        Returns:
            dict with conversations list and total count.
        """
        if not self._is_enabled():
            return {
                'error': True,
                'message': 'Copilot is disabled.',
            }

        Conversation = request.env['ipai.copilot.conversation']
        domain = [
            ('user_id', '=', request.env.user.id),
        ]
        if state:
            domain.append(('state', '=', state))

        total = Conversation.search_count(domain)
        conversations = Conversation.search(
            domain, limit=limit, offset=offset,
        )

        return {
            'conversations': [
                {
                    'id': c.id,
                    'name': c.name,
                    'state': c.state,
                    'message_count': c.message_count,
                    'context_model': c.context_model or '',
                    'context_res_id': c.context_res_id or 0,
                    'create_date': str(c.create_date),
                    'write_date': str(c.write_date),
                }
                for c in conversations
            ],
            'total': total,
        }
