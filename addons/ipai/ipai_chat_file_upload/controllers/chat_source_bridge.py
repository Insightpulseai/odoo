# -*- coding: utf-8 -*-
import base64
import hashlib
import json
import logging
import os

from odoo import http
from odoo.http import request

from ..models.chat_source import MIME_TO_TYPE

_logger = logging.getLogger(__name__)

# Service key for inbound callbacks from agent-platform
_SERVICE_KEY_ENV = 'IPAI_CHAT_SOURCE_SERVICE_KEY'


def _check_service_key(req):
    """Validate inbound service-to-service callback auth."""
    expected = os.environ.get(_SERVICE_KEY_ENV, '')
    if not expected:
        _logger.warning(
            'Chat source callback: %s not configured', _SERVICE_KEY_ENV
        )
        return False
    provided = req.httprequest.headers.get('X-Service-Key', '')
    return provided and provided == expected


class ChatSourceBridgeController(http.Controller):
    """Thin bridge between Odoo chat sources and agent-platform."""

    # ------------------------------------------------------------------
    # Upload: User uploads a file, creates source in draft
    # ------------------------------------------------------------------
    @http.route(
        '/ipai/chat/upload',
        type='http',
        auth='user',
        methods=['POST'],
        csrf=False,
    )
    def upload_source(self, **kwargs):
        session_id = int(kwargs.get('session_id', 0))
        if not session_id:
            return request.make_json_response(
                {'error': 'session_id is required'}, status=400
            )

        session = request.env['ipai.chat.session'].browse(session_id)
        if not session.exists():
            return request.make_json_response(
                {'error': 'Session not found'}, status=404
            )

        files = request.httprequest.files.getlist('files')
        if not files:
            return request.make_json_response(
                {'error': 'No files provided'}, status=400
            )

        created = []
        errors = []
        for f in files:
            mime = f.content_type or ''
            source_type = MIME_TO_TYPE.get(mime)
            if not source_type:
                errors.append({
                    'filename': f.filename,
                    'error': f'Unsupported file type: {mime}',
                })
                continue

            raw = f.read()
            if len(raw) > 50 * 1024 * 1024:
                errors.append({
                    'filename': f.filename,
                    'error': 'File exceeds 50 MB limit',
                })
                continue

            attachment = request.env['ir.attachment'].create({
                'name': f.filename,
                'datas': base64.b64encode(raw),
                'res_model': 'ipai.chat.source',
                'mimetype': mime,
            })

            source = request.env['ipai.chat.source'].create({
                'name': f.filename,
                'session_id': session_id,
                'attachment_id': attachment.id,
                'source_type': source_type,
                'checksum': hashlib.sha256(raw).hexdigest(),
                'file_size': len(raw),
            })
            # Auto-submit for local extraction
            try:
                source.action_submit_for_processing()
            except Exception as e:
                _logger.warning('Auto-extraction failed for %s: %s', f.filename, e)
            created.append({
                'id': source.id,
                'name': source.name,
                'source_type': source_type,
                'status': source.status,
                'token_estimate': source.token_estimate or 0,
            })

        return request.make_json_response({
            'sources': created,
            'errors': errors,
        })

    # ------------------------------------------------------------------
    # Upload URL: Register a URL source
    # ------------------------------------------------------------------
    @http.route(
        '/ipai/chat/upload-url',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def upload_url_source(self, session_id, url, name=None):
        session = request.env['ipai.chat.session'].browse(session_id)
        if not session.exists():
            return {'error': 'Session not found'}

        source = request.env['ipai.chat.source'].create({
            'name': name or url,
            'session_id': session_id,
            'source_type': 'url',
            'url': url,
        })
        return {
            'id': source.id,
            'name': source.name,
            'source_type': 'url',
            'status': 'draft',
        }

    # ------------------------------------------------------------------
    # Submit: Move source(s) from draft → processing
    # ------------------------------------------------------------------
    @http.route(
        '/ipai/chat/source/submit',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def submit_sources(self, source_ids):
        sources = request.env['ipai.chat.source'].browse(source_ids)
        results = []
        for src in sources.exists():
            try:
                src.action_submit_for_processing()
                results.append({'id': src.id, 'status': 'processing'})
            except Exception as e:
                results.append({'id': src.id, 'error': str(e)})
        return {'results': results}

    # ------------------------------------------------------------------
    # Retry: Retry failed source
    # ------------------------------------------------------------------
    @http.route(
        '/ipai/chat/source/retry',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def retry_source(self, source_id):
        source = request.env['ipai.chat.source'].browse(source_id)
        if not source.exists():
            return {'error': 'Source not found'}
        try:
            source.action_retry()
            return {'id': source.id, 'status': 'processing'}
        except Exception as e:
            return {'id': source.id, 'error': str(e)}

    # ------------------------------------------------------------------
    # Callback: agent-platform → Odoo status update (service auth)
    # ------------------------------------------------------------------
    @http.route(
        '/ipai/chat/source/cb',
        type='json',
        auth='none',
        methods=['POST'],
    )
    def source_callback(self, **kwargs):
        if not _check_service_key(request):
            return {'error': 'Unauthorized'}, 401

        source_id = kwargs.get('source_id')
        if not source_id:
            return {'error': 'source_id is required'}

        source = (
            request.env['ipai.chat.source']
            .sudo()
            .browse(int(source_id))
        )
        if not source.exists():
            return {'error': f'Source {source_id} not found'}

        try:
            source.apply_callback(kwargs)
            return {
                'id': source.id,
                'status': source.status,
            }
        except Exception as e:
            _logger.exception('Source callback failed for %s', source_id)
            return {'error': str(e)}

    # ------------------------------------------------------------------
    # Chat: Send message with source-grounded context
    # ------------------------------------------------------------------
    @http.route(
        '/ipai/chat/send',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def send_message(self, session_id, message, source_ids=None,
                     restrict_to_sources=False):
        session = request.env['ipai.chat.session'].browse(session_id)
        if not session.exists():
            return {'error': 'Session not found'}

        # Determine eligible sources
        if restrict_to_sources and source_ids:
            eligible = request.env['ipai.chat.source'].browse(
                source_ids
            ).filtered(lambda s: s.is_eligible())
        else:
            eligible = session.get_eligible_sources()

        eligible_ids = eligible.ids

        # Store user message
        user_msg = request.env['ipai.chat.message'].create({
            'session_id': session_id,
            'role': 'user',
            'content': message,
            'source_ids_snapshot': json.dumps(eligible_ids),
        })

        # Build grounded context from extracted text
        source_context_parts = []
        for src in eligible:
            if src.extracted_text:
                # Truncate to ~8k chars per source to stay within limits
                text = src.extracted_text[:8000]
                source_context_parts.append(
                    f'--- Source: {src.name} (type: {src.source_type}) ---\n'
                    f'{text}\n'
                    f'--- End: {src.name} ---'
                )

        # Try Foundry-backed chat via ipai_odoo_copilot
        assistant_content = None
        foundry_used = False
        if source_context_parts:
            grounded_prompt = (
                'The user has uploaded the following source documents. '
                'Use them to answer the question.\n\n'
                + '\n\n'.join(source_context_parts)
                + f'\n\nUser question: {message}'
            )
        else:
            grounded_prompt = message

        try:
            foundry_svc = request.env['ipai.foundry.service']
            foundry_result = foundry_svc.chat_completion(
                prompt=grounded_prompt,
                user=request.env.user,
                context_model=None,
                context_res_id=None,
            )
            if foundry_result and foundry_result.get('content'):
                assistant_content = foundry_result['content']
                foundry_used = True
        except Exception as e:
            _logger.warning('Foundry chat failed, using fallback: %s', e)

        if not assistant_content:
            if source_context_parts:
                assistant_content = (
                    f'I have {len(eligible_ids)} source(s) loaded '
                    f'({sum(s.token_estimate or 0 for s in eligible)} '
                    f'tokens total). Foundry is not currently available '
                    f'to process your question. Please try again later.'
                )
            else:
                assistant_content = (
                    'No indexed sources available for this session. '
                    'Upload a file first to enable grounded chat.'
                )

        # Store assistant response
        provenance = json.dumps([
            {'id': s.id, 'name': s.name, 'tokens': s.token_estimate or 0}
            for s in eligible
        ]) if eligible else None

        assistant_msg = request.env['ipai.chat.message'].create({
            'session_id': session_id,
            'role': 'assistant',
            'content': assistant_content,
            'source_ids_snapshot': json.dumps(eligible_ids),
            'provenance_summary': provenance,
        })

        return {
            'user_message_id': user_msg.id,
            'assistant_message_id': assistant_msg.id,
            'content': assistant_content,
            'eligible_source_count': len(eligible_ids),
            'foundry_used': foundry_used,
        }
