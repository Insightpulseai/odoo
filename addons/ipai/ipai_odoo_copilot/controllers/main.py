# -*- coding: utf-8 -*-

import hmac
import logging
import os

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class CopilotController(http.Controller):

    # ------------------------------------------------------------------
    # Chat endpoints
    # ------------------------------------------------------------------

    @http.route(
        "/ipai/copilot/chat",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=True,
    )
    def chat(self, prompt=None, message=None, record_model=None,
             record_id=None, surface=None, conversation_id=None,
             context=None, **kw):
        """Chat endpoint for Odoo-authenticated consumers.

        Accepts both formats:
          - systray UI: {"message": "...", "conversation_id": N, "context": {...}}
          - API:        {"prompt": "...", "record_model": "...", "record_id": 123}

        Returns: {"content": "...", "blocked": false, "reason": "",
                  "conversation_id": N}
        """
        # Normalize: accept 'message' (from UI) or 'prompt' (from API)
        text = prompt or message
        ctx = context or {}
        return self._handle_chat(
            prompt=text,
            record_model=record_model or ctx.get("context_model"),
            record_id=record_id or ctx.get("context_res_id"),
            source="api",
            user_id=request.env.uid,
            surface=surface or ctx.get("surface") or "erp",
            conversation_id=conversation_id,
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

        # Use sudo env — resolve a bot user for audit trail
        bot_partner = request.env(su=True).ref(
            "ipai_odoo_copilot.partner_copilot", raise_if_not_found=False
        )
        bot_user_id = None
        if bot_partner:
            bot_user = request.env(su=True)["res.users"].search(
                [("partner_id", "=", bot_partner.id)], limit=1
            )
            bot_user_id = bot_user.id if bot_user else None

        return self._handle_chat(
            prompt=prompt,
            record_model=record_model,
            record_id=record_id,
            source="widget",
            user_id=bot_user_id,
            sudo=True,
            surface=surface or "web",
        )

    def _handle_chat(self, prompt, record_model, record_id, source,
                     user_id, sudo=False, surface="erp",
                     conversation_id=None):
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

        return {
            "content": response_text or "",
            "blocked": not bool(response_text),
            "reason": "" if response_text else "No response from Foundry",
            "conversation_id": conversation_id,
        }

    # ------------------------------------------------------------------
    # Conversation CRUD (used by systray copilot_service.js)
    # ------------------------------------------------------------------

    def _is_enabled(self):
        """Check if copilot is enabled via ir.config_parameter."""
        return request.env["ir.config_parameter"].sudo().get_param(
            "ipai_copilot.enabled", "False"
        ).lower() in ("true", "1")

    @http.route(
        "/ipai/copilot/conversations/create",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def create_conversation(self, name="", context_model="",
                            context_res_id=0):
        """Create a new conversation."""
        if not self._is_enabled():
            return {"error": True, "message": "Copilot is disabled."}

        vals = {"name": name or "New Conversation"}
        if context_model:
            vals["context_model"] = context_model
        if context_res_id:
            vals["context_res_id"] = int(context_res_id)

        conversation = request.env["ipai.copilot.conversation"].create(vals)
        return {
            "conversation_id": conversation.id,
            "name": conversation.name,
            "gateway_correlation_id": conversation.gateway_correlation_id,
        }

    @http.route(
        "/ipai/copilot/conversations/list",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def list_conversations(self, state="active", limit=20, offset=0):
        """Return current user's conversations."""
        if not self._is_enabled():
            return {"error": True, "message": "Copilot is disabled."}

        Conversation = request.env["ipai.copilot.conversation"]
        domain = [("user_id", "=", request.env.user.id)]
        if state:
            domain.append(("state", "=", state))

        total = Conversation.search_count(domain)
        conversations = Conversation.search(
            domain, limit=limit, offset=offset,
        )

        return {
            "conversations": [
                {
                    "id": c.id,
                    "name": c.name,
                    "state": c.state,
                    "message_count": c.message_count,
                    "context_model": c.context_model or "",
                    "context_res_id": c.context_res_id or 0,
                    "create_date": str(c.create_date),
                    "write_date": str(c.write_date),
                }
                for c in conversations
            ],
            "total": total,
        }
