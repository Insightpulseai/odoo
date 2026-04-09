# -*- coding: utf-8 -*-

import hmac
import json
import logging
import os
import time

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PulserController(http.Controller):
    """Pulser for Odoo — chat and conversation controller.

    Public API surface uses /api/pulser/* naming.
    Legacy /ipai/copilot/* routes are preserved for backward compatibility
    with existing systray JS and external consumers.
    """

    # ------------------------------------------------------------------
    # Chat endpoints (Pulser-branded primary + legacy aliases)
    # ------------------------------------------------------------------

    @http.route(
        ["/api/pulser/chat", "/ipai/copilot/chat"],
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
                  "conversation_id": N, "skill": "..."}
        """
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
        ["/api/pulser/chat/service", "/ipai/copilot/chat/service"],
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def chat_service(self, prompt=None, record_model=None,
                     record_id=None, surface=None, **kw):
        """Service-to-service endpoint for external apps.

        Authenticates via PULSER_SERVICE_KEY (or legacy IPAI_COPILOT_SERVICE_KEY).
        Audit records are logged with source='widget'.
        """
        expected_key = (
            os.environ.get("PULSER_SERVICE_KEY")
            or os.environ.get("IPAI_COPILOT_SERVICE_KEY", "")
        )
        if not expected_key:
            _logger.warning(
                "Service endpoint called but PULSER_SERVICE_KEY not configured"
            )
            return {
                "content": "",
                "blocked": True,
                "reason": "Service key not configured on server",
            }

        provided_key = (
            request.httprequest.headers.get("X-Pulser-Service-Key")
            or request.httprequest.headers.get("X-Copilot-Service-Key", "")
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
        """Shared chat handler: classify → context → Foundry → audit.

        Full audit trail: skill, confidence, tools, knowledge source,
        disposition, latency.
        """
        start = time.time()

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
                "reason": "Pulser is disabled",
            }

        # Build context envelope from authenticated user
        context_envelope = service._build_context_envelope(
            user_id=user_id or env.uid,
            record_model=record_model,
            record_id=record_id,
            surface=surface,
        )

        # Classify intent via skill router
        router = env["ipai.copilot.skill.router"]
        intent = router.classify_intent(prompt, context_envelope)
        skill_id = intent.get("skill_id", "general")
        skill_confidence = intent.get("confidence", "low")

        # Add skill metadata to context for tool scoping
        context_envelope["skill_id"] = skill_id
        context_envelope["skill_confidence"] = skill_confidence

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

        latency_ms = int((time.time() - start) * 1000)

        # Determine response disposition
        if not response_text:
            disposition = "fallback"
        elif response_text.startswith("I'm Pulser"):
            disposition = "fallback"
        else:
            disposition = "answered"

        # Determine knowledge source from context (set by foundry_service)
        tools_invoked = context_envelope.get("_tools_invoked", [])
        knowledge_source = self._classify_knowledge_source(tools_invoked)
        write_queued = "propose_action" in tools_invoked

        if write_queued:
            disposition = "queued"

        # Write full audit record
        self._write_audit(
            env=env,
            user_id=user_id,
            prompt=prompt,
            response=response_text,
            source=source,
            surface=surface,
            context_envelope=context_envelope,
            skill_id=skill_id,
            skill_confidence=skill_confidence,
            tools_invoked=tools_invoked,
            knowledge_source=knowledge_source,
            write_queued=write_queued,
            disposition=disposition,
            latency_ms=latency_ms,
            foundry_mode=context_envelope.get("_foundry_mode", ""),
        )

        # Extract activities for the UI timeline (strip internal prefix)
        activities = context_envelope.get("_activities", [])

        return {
            "content": response_text or "",
            "blocked": not bool(response_text),
            "reason": "" if response_text else "No response from Pulser",
            "conversation_id": conversation_id,
            "skill": skill_id,
            "activities": activities,
        }

    def _classify_knowledge_source(self, tools_invoked):
        """Classify the primary knowledge source from tools used."""
        if not tools_invoked:
            return "none"

        has_odoo = any(
            t in tools_invoked
            for t in ("read_record", "search_records", "propose_action")
        )
        has_search = any(
            t in tools_invoked
            for t in ("search_odoo_docs", "search_azure_docs",
                       "search_spec_bundles", "search_org_docs",
                       "search_databricks_docs")
        )
        has_fabric = "query_fabric_data" in tools_invoked

        sources = sum([has_odoo, has_search, has_fabric])
        if sources > 1:
            return "mixed"
        if has_fabric:
            return "fabric"
        if has_search:
            return "search"
        if has_odoo:
            return "odoo"
        return "none"

    def _write_audit(self, env, user_id, prompt, response, source,
                     surface, context_envelope, skill_id,
                     skill_confidence, tools_invoked, knowledge_source,
                     write_queued, disposition, latency_ms,
                     foundry_mode=""):
        """Write a comprehensive audit record. Non-blocking."""
        try:
            valid_sources = ("discuss", "api", "widget")
            valid_surfaces = ("web", "erp", "copilot", "analytics", "ops")
            valid_confidences = ("high", "medium", "low")
            valid_dispositions = (
                "answered", "blocked", "queued", "fallback", "error",
            )
            valid_modes = ("sdk", "http", "simple", "offline")

            env["ipai.copilot.audit"].sudo().create({
                "user_id": user_id or env.uid,
                "prompt": prompt,
                "response_excerpt": (response or "")[:500],
                "source": source if source in valid_sources else "api",
                "surface": surface if surface in valid_surfaces else "erp",
                "context_envelope": json.dumps(
                    {k: v for k, v in (context_envelope or {}).items()
                     if not k.startswith("_")},
                    default=str,
                ),
                "company_id": env.company.id,
                "skill_id": (skill_id or "")[:64],
                "skill_confidence": (
                    skill_confidence
                    if skill_confidence in valid_confidences
                    else False
                ),
                "tools_invoked": (
                    ",".join(tools_invoked)[:256]
                    if tools_invoked else ""
                ),
                "knowledge_source": (
                    knowledge_source
                    if knowledge_source in (
                        "odoo", "search", "fabric", "mixed", "none",
                    )
                    else "none"
                ),
                "write_proposal_queued": write_queued,
                "response_disposition": (
                    disposition
                    if disposition in valid_dispositions
                    else "answered"
                ),
                "foundry_mode": (
                    foundry_mode
                    if foundry_mode in valid_modes
                    else False
                ),
                "latency_ms": latency_ms,
            })
        except Exception:
            _logger.debug("Audit record creation failed", exc_info=True)

    # ------------------------------------------------------------------
    # Conversation CRUD (used by systray)
    # ------------------------------------------------------------------

    def _is_enabled(self):
        """Check if Pulser is enabled via ir.config_parameter."""
        return request.env["ir.config_parameter"].sudo().get_param(
            "ipai_copilot.enabled", "False"
        ).lower() in ("true", "1")

    @http.route(
        ["/api/pulser/conversations/create",
         "/ipai/copilot/conversations/create"],
        type="json",
        auth="user",
        methods=["POST"],
    )
    def create_conversation(self, name="", context_model="",
                            context_res_id=0):
        """Create a new conversation."""
        if not self._is_enabled():
            return {"error": True, "message": "Pulser is disabled."}

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
        ["/api/pulser/conversations/list",
         "/ipai/copilot/conversations/list"],
        type="json",
        auth="user",
        methods=["POST"],
    )
    def list_conversations(self, state="active", limit=20, offset=0):
        """Return current user's conversations."""
        if not self._is_enabled():
            return {"error": True, "message": "Pulser is disabled."}

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
