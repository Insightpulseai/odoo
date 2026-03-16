# -*- coding: utf-8 -*-

import hmac
import logging
import os

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class CopilotController(http.Controller):

    @http.route(
        "/ipai/copilot/chat",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=True,
    )
    def chat(self, prompt=None, record_model=None, record_id=None,
             surface=None, **kw):
        """Chat endpoint for Odoo-authenticated consumers.

        Accepts JSON-RPC body: {"prompt": "...", "record_model": "...",
        "record_id": 123, "surface": "erp"}
        Returns: {"content": "...", "blocked": false, "reason": ""}
        """
        return self._handle_chat(
            prompt=prompt,
            record_model=record_model,
            record_id=record_id,
            source="api",
            user_id=request.env.uid,
            surface=surface or "erp",
        )

    @http.route(
        "/ipai/copilot/chat/service",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def chat_service(self, prompt=None, record_model=None,
                     record_id=None, surface=None, **kw):
        """Service-to-service endpoint for external apps (docs widget).

        Authenticates via IPAI_COPILOT_SERVICE_KEY header.
        Audit records are logged with source='widget'.
        """
        # Validate service key
        expected_key = os.environ.get("IPAI_COPILOT_SERVICE_KEY", "")
        if not expected_key:
            _logger.warning(
                "Service endpoint called but IPAI_COPILOT_SERVICE_KEY "
                "not configured"
            )
            return {
                "content": "",
                "blocked": True,
                "reason": "Service key not configured on server",
            }

        provided_key = (
            request.httprequest.headers.get("X-Copilot-Service-Key", "")
        )
        if not provided_key or not hmac.compare_digest(
            expected_key, provided_key
        ):
            return {
                "content": "",
                "blocked": True,
                "reason": "Invalid service key",
            }

        # Use SUPERUSER for env since auth=none has no user session
        return self._handle_chat(
            prompt=prompt,
            record_model=record_model,
            record_id=record_id,
            source="widget",
            user_id=None,
            sudo=True,
            surface=surface or "web",
        )

    def _handle_chat(self, prompt, record_model, record_id, source,
                     user_id, sudo=False, surface="erp"):
        """Shared chat handler for both authenticated and service routes."""
        if not prompt:
            return {"content": "", "blocked": True, "reason": "Empty prompt"}

        env = request.env
        if sudo:
            env = env(su=True)

        service = env["ipai.foundry.service"]
        settings = service._get_settings()

        if not settings["enabled"]:
            return {
                "content": "",
                "blocked": True,
                "reason": "Copilot is disabled",
            }

        # Build context envelope from authenticated user
        context_envelope = service._build_context_envelope(
            user_id=user_id or env.uid,
            record_model=record_model,
            record_id=record_id,
            surface=surface,
        )

        # Build context hint if record info provided
        context_prefix = ""
        if record_model and record_id:
            context_prefix = (
                "[Context: viewing %s record #%s] "
                % (record_model, record_id)
            )

        user_message = context_prefix + prompt

        response_text = service.chat_completion(
            user_message=user_message,
            user_id=user_id,
            context_envelope=context_envelope,
        )

        # Audit is already written inside chat_completion; avoid duplicate.
        # Only write here if chat_completion was not reached (e.g. disabled).

        return {
            "content": response_text or "",
            "blocked": not bool(response_text),
            "reason": "" if response_text else "No response from Foundry",
        }
