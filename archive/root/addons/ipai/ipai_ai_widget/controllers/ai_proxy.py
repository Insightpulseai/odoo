# © 2026 InsightPulse AI — License LGPL-3.0-or-later
"""
IPAI AI proxy controller.

Routes:
    POST /ipai/ai/ask      — JSON-RPC, auth=user (internal users only)
        Request:  { prompt, record_model?, record_id?, thread_id?, preset_key?,
                    selected_text?, chatter_text? }
        Response: { provider, text, model, trace_id, thread_id } on success
                  { error: <CODE>, status: <int> }    on failure

    POST /ipai/ai/presets   — JSON-RPC, auth=user
        Response: [{ key, label, icon, requires_selection, output_mode }]

Error codes (also in ask_ai_widget.js ERROR_MESSAGES):
    BRIDGE_URL_NOT_CONFIGURED — ir.config_parameter ipai_ai_widget.bridge_url is unset
    AI_KEY_NOT_CONFIGURED     — bridge returned 503 (GEMINI_API_KEY missing on bridge)
    BRIDGE_TIMEOUT            — bridge did not respond within TIMEOUT_SECONDS
    BRIDGE_ERROR              — any other bridge-side failure
    PROMPT_REQUIRED           — request body missing or empty prompt

Security boundary:
    - Provider API keys never pass through this controller or the browser.
    - The bridge_token (optional bearer) is read server-side from ir.config_parameter.
    - Audit rows are written without prompt/response content.
"""
import logging
import time
import uuid

from odoo import http
from odoo.http import request

from ._bridge_helper import call_azure_direct, call_bridge, get_bridge_config, has_azure_config

_logger = logging.getLogger(__name__)


class IpaiAiProxyController(http.Controller):

    @http.route("/ipai/ai/ping", type="json", auth="user", methods=["POST"], csrf=False)
    def ping(self, **_kwargs):
        """Runtime self-check endpoint. Verifies bridge config, models, and presets.

        Returns a diagnostic dict for the frontend to assert mount correctness:
            { ok: bool, bridge_url: bool, presets: int, thread_model: bool,
              message_model: bool, user: str }
        """
        env = request.env
        bridge_url, _token = get_bridge_config(env)

        # Check models exist
        thread_ok = "ipai.ai.thread" in env
        message_ok = "ipai.ai.message" in env
        preset_ok = "ipai.ai.preset" in env

        preset_count = 0
        if preset_ok:
            preset_count = env["ipai.ai.preset"].sudo().search_count(
                [("active", "=", True)]
            )

        return {
            "ok": bool(bridge_url) and thread_ok and message_ok and preset_ok,
            "bridge_url": bool(bridge_url),
            "presets": preset_count,
            "thread_model": thread_ok,
            "message_model": message_ok,
            "preset_model": preset_ok,
            "user": env.user.login,
        }

    @http.route("/ipai/ai/ask", type="json", auth="user", methods=["POST"], csrf=False)
    def ask_ai(
        self,
        prompt=None,
        record_model=None,
        record_id=None,
        thread_id=None,
        preset_key=None,
        selected_text=None,
        chatter_text=None,
        **_kwargs,
    ):
        trace_id = str(uuid.uuid4())
        t_start = time.monotonic()

        # ── Resolve prompt from preset template or raw input ─────────
        prompt_str = str(prompt or "").strip()

        if preset_key:
            preset = (
                request.env["ipai.ai.preset"]
                .sudo()
                .search([("key", "=", preset_key), ("active", "=", True)], limit=1)
            )
            if preset:
                prompt_str = preset.prompt_template.format(
                    record_model=record_model or "record",
                    chatter_text=chatter_text or "(no chatter text)",
                    selected_text=selected_text or "(no selection)",
                    target_language="English",
                )

        def _audit(outcome, error_code=None):
            """Write a metadata-only audit log row (no prompt/response content)."""
            latency_ms = int((time.monotonic() - t_start) * 1000)
            try:
                request.env["ipai.ai.audit.log"].sudo().create(
                    {
                        "user_id": request.env.user.id,
                        "record_model": record_model or False,
                        "record_id": int(record_id) if record_id else 0,
                        "trace_id": trace_id,
                        "outcome": outcome,
                        "latency_ms": latency_ms,
                        "error_code": error_code or False,
                        "prompt_len": len(prompt_str),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                _logger.warning(
                    "ipai_ai_widget: audit log write failed (trace=%s): %s",
                    trace_id,
                    exc,
                )

        if not prompt_str:
            _audit("prompt_required", "PROMPT_REQUIRED")
            return {"error": "PROMPT_REQUIRED", "status": 400}

        # ── Bridge config ────────────────────────────────────────────
        bridge_url, bridge_token = get_bridge_config(request.env)

        # ── Thread context (multi-turn) ──────────────────────────────
        Thread = request.env["ipai.ai.thread"]
        Message = request.env["ipai.ai.message"]
        thread = None
        history = []

        if thread_id:
            thread = Thread.browse(int(thread_id))
            if not thread.exists() or thread.user_id != request.env.user:
                thread = None

        if thread is None:
            thread = Thread._get_or_create(
                request.env.user.id,
                record_model or False,
                int(record_id) if record_id else 0,
            )

        if thread:
            history = thread._get_messages(limit=20)

        if bridge_url:
            # ── Primary: IPAI bridge ──────────────────────────────────
            payload = {
                "prompt": prompt_str,
                "context": {
                    "record_model": record_model or None,
                    "record_id": int(record_id) if record_id else None,
                    "user_id": request.env.user.id,
                    "trace_id": trace_id,
                },
            }
            if history:
                payload["history"] = history

            data, error_code = call_bridge(bridge_url, bridge_token, payload)

            if error_code:
                outcome_map = {
                    "BRIDGE_TIMEOUT": "bridge_timeout",
                    "AI_KEY_NOT_CONFIGURED": "ai_key_not_configured",
                    "BRIDGE_ERROR": "bridge_error",
                }
                _audit(outcome_map.get(error_code, "bridge_error"), error_code)
                status_map = {
                    "BRIDGE_TIMEOUT": 504,
                    "AI_KEY_NOT_CONFIGURED": 503,
                    "BRIDGE_ERROR": 500,
                }
                return {"error": error_code, "status": status_map.get(error_code, 500)}

        elif has_azure_config(request.env):
            # ── Fallback: Azure OpenAI direct ─────────────────────────
            data, error_code = call_azure_direct(prompt_str, request.env)
            if error_code:
                _audit("azure_error", error_code)
                return {"error": error_code, "status": 500}

        else:
            _logger.warning(
                "ipai_ai_widget: BRIDGE_URL_NOT_CONFIGURED (trace=%s)", trace_id
            )
            _audit("bridge_url_not_configured", "BRIDGE_URL_NOT_CONFIGURED")
            return {"error": "BRIDGE_URL_NOT_CONFIGURED", "status": 503}

        # ── Persist to thread ────────────────────────────────────────
        if thread:
            Message.sudo().create(
                {
                    "thread_id": thread.id,
                    "role": "user",
                    "content": prompt_str,
                    "preset_key": preset_key or False,
                    "trace_id": trace_id,
                }
            )
            ai_text = data.get("text", "")
            if ai_text:
                Message.sudo().create(
                    {
                        "thread_id": thread.id,
                        "role": "assistant",
                        "content": ai_text,
                        "trace_id": trace_id,
                    }
                )

        _audit("success")
        return {
            "provider": data.get("provider", "unknown"),
            "text": data.get("text", ""),
            "model": data.get("model", ""),
            "trace_id": trace_id,
            "thread_id": thread.id if thread else False,
        }

    @http.route(
        "/ipai/ai/presets", type="json", auth="user", methods=["POST"], csrf=False
    )
    def list_presets(self, **_kwargs):
        """Return active preset definitions for the frontend."""
        presets = (
            request.env["ipai.ai.preset"]
            .sudo()
            .search([("active", "=", True)], order="sequence, id")
        )
        return [
            {
                "key": p.key,
                "label": p.label,
                "icon": p.icon,
                "requires_selection": p.requires_selection,
                "output_mode": p.output_mode,
            }
            for p in presets
        ]
