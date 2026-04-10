# -*- coding: utf-8 -*-

import base64
import hmac
import json
import logging
import os
import time

from werkzeug.wrappers import Response as WerkzeugResponse

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
    # File upload endpoint
    # ------------------------------------------------------------------

    @http.route(
        ["/api/pulser/upload", "/ipai/copilot/upload"],
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def upload_files(self, **kwargs):
        """Accept file uploads from the chat UI, store as ir.attachment.

        Returns JSON: {"attachment_ids": [...], "files": [...]}
        """
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

        attachment_ids = []
        file_info = []

        Attachment = request.env['ir.attachment']
        for f in uploaded_files:
            if f.content_type not in ALLOWED_MIMES:
                _logger.warning('Upload rejected: unsupported MIME %s', f.content_type)
                continue
            data = f.read()
            if len(data) > MAX_SIZE:
                _logger.warning('Upload rejected: file too large %s (%d bytes)', f.filename, len(data))
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

        _logger.info('Copilot upload: %d files stored as ir.attachment', len(attachment_ids))

        return WerkzeugResponse(
            json.dumps({
                'attachment_ids': attachment_ids,
                'files': file_info,
            }),
            content_type='application/json',
            status=200,
        )

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
             context=None, attachment_ids=None, **kw):
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
            attachment_ids=attachment_ids,
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
                     conversation_id=None, attachment_ids=None):
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
        context_envelope["source"] = source
        context_envelope["user_id"] = user_id or env.uid
        context_envelope["company_id"] = env.company.id

        # Resolve attached files and inject metadata into context
        attachment_context = ""
        if attachment_ids:
            attachments = env["ir.attachment"].browse(attachment_ids).exists()
            if attachments:
                file_descriptions = []
                for att in attachments:
                    size_kb = round(att.file_size / 1024, 1) if att.file_size else 0
                    file_descriptions.append(
                        "%s (%s, %s KB)" % (att.name, att.mimetype, size_kb)
                    )
                context_envelope["attachment_ids"] = attachment_ids
                context_envelope["attachment_files"] = [
                    {"id": a.id, "name": a.name, "mimetype": a.mimetype,
                     "size": a.file_size}
                    for a in attachments
                ]
                context_envelope["has_attachments"] = True
                context_envelope["attachment_mimes"] = [
                    a.mimetype for a in attachments
                ]
                attachment_context = (
                    "[Attached files: %s] " % "; ".join(file_descriptions)
                )

        # Classify intent via skill router
        router = env["ipai.copilot.skill.router"]
        intent = router.classify_intent(prompt, context_envelope)
        skill_id = intent.get("skill_id", "general")
        skill_confidence = intent.get("confidence", "low")

        # Add skill metadata to context for tool scoping
        context_envelope["skill_id"] = skill_id
        context_envelope["skill_confidence"] = skill_confidence
        context_envelope["permitted_tools"] = service.get_permitted_tools(skill_id)
        context_envelope["skill_instructions"] = (
            router.get_skill_instructions(skill_id)
        )

        # Build context hint if record info provided
        context_prefix = ""
        if record_model and record_id:
            context_prefix = (
                "[Context: viewing %s record #%s] "
                % (record_model, record_id)
            )

        user_message = attachment_context + context_prefix + prompt

        # Deterministic extraction short-circuit: if the skill router
        # classified as document_extract and attachments are present,
        # call Document Intelligence directly — no Foundry needed.
        if skill_id == "document_extract" and attachment_ids:
            response_text = self._handle_extraction(
                env, attachment_ids, context_envelope,
            )
            if response_text:
                latency_ms = int((time.time() - start) * 1000)
                self._write_audit(
                    env=env, user_id=user_id, prompt=prompt,
                    response=response_text, source=source,
                    surface=surface, context_envelope=context_envelope,
                    skill_id=skill_id, skill_confidence=skill_confidence,
                    tools_invoked=["extract_document"],
                    knowledge_source="odoo",
                    write_queued=False, disposition="answered",
                    latency_ms=latency_ms,
                )
                return {
                    "content": response_text,
                    "blocked": False,
                    "reason": "",
                    "conversation_id": conversation_id,
                    "skill": skill_id,
                    "activities": context_envelope.get("_activities", []),
                }

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
                       "search_databricks_docs", "query_knowledge_base")
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

    def _handle_extraction(self, env, attachment_ids, context_envelope):
        """Extract document data via Document Intelligence (deterministic).

        Auto-selects the DI model based on context:
          - prebuilt-invoice for finance/accounting records
          - prebuilt-receipt for expense context
          - prebuilt-read for everything else

        Returns formatted response text, or None on failure.
        """
        service = env["ipai.doc.intelligence.service"]
        attachments = env["ir.attachment"].browse(attachment_ids).exists()
        if not attachments:
            return None

        # Auto-select DI model from context
        record_model = context_envelope.get("record_model", "")
        surface = context_envelope.get("surface", "")
        mimes = context_envelope.get("attachment_mimes", [])

        if record_model in ("account.move", "account.move.line"):
            model_id = "prebuilt-invoice"
        elif record_model in ("hr.expense",):
            model_id = "prebuilt-receipt"
        elif surface == "analytics":
            model_id = "prebuilt-read"
        else:
            # Default: try invoice for PDFs (most common upload), read for rest
            has_pdf = any(m == "application/pdf" for m in mimes)
            model_id = "prebuilt-invoice" if has_pdf else "prebuilt-read"

        parts = []
        for att in attachments:
            result = service.analyze_document(att.id, model_id)
            if result.get("status") != "success":
                parts.append(
                    "**%s**: Extraction failed — %s"
                    % (att.name, result.get("message", "unknown error"))
                )
                continue

            analyze_result = result.get("result", {})
            documents = analyze_result.get("documents", [])

            if documents:
                # Structured extraction (invoice/receipt)
                doc = documents[0]
                fields = doc.get("fields", {})
                confidence = doc.get("confidence", 0.0)
                lines = ["**%s** (confidence: %.0f%%)" % (att.name, confidence * 100)]
                for key, val in fields.items():
                    display_val = (
                        val.get("valueString")
                        or val.get("valueNumber")
                        or val.get("valueDate")
                        or val.get("content", "")
                    )
                    if display_val:
                        lines.append("- **%s**: %s" % (key, display_val))
                parts.append("\n".join(lines))
            else:
                # General read — return raw text
                content = analyze_result.get("content", "")
                if content:
                    parts.append(
                        "**%s**:\n\n%s" % (att.name, content[:3000])
                    )
                else:
                    parts.append(
                        "**%s**: No text extracted." % att.name
                    )

        return "\n\n---\n\n".join(parts) if parts else None

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
        settings = request.env["ipai.foundry.service"]._get_settings()
        return settings.get("enabled", False)

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
