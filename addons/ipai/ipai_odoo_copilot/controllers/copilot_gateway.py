# -*- coding: utf-8 -*-

import json
import logging
import time
import urllib.error
import urllib.request
import uuid

from werkzeug.wrappers import Response as WerkzeugResponse

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

_GATEWAY_TIMEOUT = 30  # seconds


class CopilotGatewayController(http.Controller):
    """JSON-RPC controller bridging the systray UI to the agent-platform gateway.

    All routes require authenticated user session (auth='user', type='json').
    Gateway URL is read from ir.config_parameter at runtime — never hardcoded.
    """

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

    def _call_gateway(self, gateway_url, payload, correlation_id):
        """HTTP POST to the agent-platform gateway.

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
            gateway_url,
            data=body,
            headers=headers,
            method='POST',
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

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------

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

        if not (message or '').strip():
            return {
                'error': True,
                'message': 'Message cannot be empty.',
            }

        context = context or {}
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
            # Security: ensure the conversation belongs to current user
            if conversation.user_id != request.env.user:
                return {
                    'error': True,
                    'message': 'Access denied to this conversation.',
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

        # Build gateway payload
        correlation_id = conversation.gateway_correlation_id or str(uuid.uuid4())
        gateway_url = self._get_gateway_url()
        payload = {
            'conversation_id': str(conversation.id),
            'correlation_id': correlation_id,
            'message': message.strip(),
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
        }

        # Call gateway
        try:
            resp_data, latency_ms = self._call_gateway(
                gateway_url, payload, correlation_id
            )
        except ValueError as e:
            # Persist error as system message for audit trail
            Message.create({
                'conversation_id': conversation.id,
                'role': 'system',
                'content': 'Gateway error: %s' % str(e),
            })
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
        context_model, context_res_id, surface.

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

        # Parse input — accept both JSON body and form params
        try:
            body = json.loads(request.httprequest.get_data(as_text=True))
        except (json.JSONDecodeError, TypeError):
            body = {}
        message = body.get('message') or kwargs.get('message', '')
        conversation_id = body.get('conversation_id') or kwargs.get('conversation_id')
        context = {
            'context_model': body.get('context_model') or kwargs.get('context_model', ''),
            'context_res_id': body.get('context_res_id') or kwargs.get('context_res_id', 0),
            'surface': body.get('surface') or kwargs.get('surface', 'erp'),
        }

        message = (message or '').strip()
        if not message:
            return WerkzeugResponse(
                'data: {"error": true, "message": "Message cannot be empty."}\n\n',
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
            if not conversation or conversation.user_id != request.env.user:
                return WerkzeugResponse(
                    'data: {"error": true, "message": "Conversation not found or access denied."}\n\n',
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

        # Capture env references before generator (request context may expire)
        env = request.env
        conv_id = conversation.id

        def generate():
            """SSE generator that proxies gateway streaming response."""
            full_content = ''
            start = time.monotonic()
            error_occurred = False

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

            except Exception as e:
                error_occurred = True
                _logger.warning('Copilot stream error: %s', e)
                yield 'data: %s\n\n' % json.dumps({
                    'type': 'error',
                    'message': 'Stream error: %s' % str(e),
                })

            latency_ms = int((time.monotonic() - start) * 1000)

            # Persist assistant message after stream completes
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
                except Exception as e:
                    _logger.warning('Failed to persist streamed response: %s', e)

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
