# © 2026 InsightPulse AI — License LGPL-3.0-or-later
"""
IPAI AI proxy controller.

Routes:
    POST /ipai/ai/ask  — JSON-RPC, auth=user (internal users only)
        Request:  { prompt, record_model?, record_id? }
        Response: { provider, text, model, trace_id } on success
                  { error: <CODE>, status: <int> }    on failure

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

import requests

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)
TIMEOUT_SECONDS = 30


class IpaiAiProxyController(http.Controller):

    @http.route("/ipai/ai/ask", type="json", auth="user", methods=["POST"], csrf=False)
    def ask_ai(self, prompt=None, record_model=None, record_id=None, **_kwargs):
        trace_id = str(uuid.uuid4())
        t_start = time.monotonic()
        prompt_str = str(prompt or "").strip()

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
                    "ipai_ai_widget: audit log write failed (trace=%s): %s", trace_id, exc
                )

        if not prompt_str:
            _audit("prompt_required", "PROMPT_REQUIRED")
            return {"error": "PROMPT_REQUIRED", "status": 400}

        params = request.env["ir.config_parameter"].sudo()
        bridge_url = params.get_param("ipai_ai_widget.bridge_url", default="")
        bridge_token = params.get_param("ipai_ai_widget.bridge_token", default="")

        if not bridge_url:
            _logger.warning(
                "ipai_ai_widget: BRIDGE_URL_NOT_CONFIGURED (trace=%s)", trace_id
            )
            _audit("bridge_url_not_configured", "BRIDGE_URL_NOT_CONFIGURED")
            return {"error": "BRIDGE_URL_NOT_CONFIGURED", "status": 503}

        headers = {"Content-Type": "application/json"}
        if bridge_token:
            headers["Authorization"] = f"Bearer {bridge_token}"

        payload = {
            "prompt": prompt_str,
            "context": {
                "record_model": record_model or None,
                "record_id": int(record_id) if record_id else None,
                "user_id": request.env.user.id,
                "trace_id": trace_id,
            },
        }

        try:
            resp = requests.post(
                bridge_url,
                json=payload,
                timeout=TIMEOUT_SECONDS,
                headers=headers,
            )
        except requests.Timeout:
            _logger.warning(
                "ipai_ai_widget: BRIDGE_TIMEOUT calling %s (trace=%s)", bridge_url, trace_id
            )
            _audit("bridge_timeout", "BRIDGE_TIMEOUT")
            return {"error": "BRIDGE_TIMEOUT", "status": 504}
        except requests.RequestException as exc:
            _logger.error(
                "ipai_ai_widget: BRIDGE_ERROR — %s (trace=%s)", exc, trace_id
            )
            _audit("bridge_error", "BRIDGE_ERROR")
            return {"error": "BRIDGE_ERROR", "status": 500}

        if resp.status_code == 503:
            _logger.warning(
                "ipai_ai_widget: AI_KEY_NOT_CONFIGURED (bridge 503, trace=%s)", trace_id
            )
            _audit("ai_key_not_configured", "AI_KEY_NOT_CONFIGURED")
            return {"error": "AI_KEY_NOT_CONFIGURED", "status": 503}

        if not resp.ok:
            _logger.error(
                "ipai_ai_widget: BRIDGE_ERROR HTTP %s (trace=%s)", resp.status_code, trace_id
            )
            _audit("bridge_error", "BRIDGE_ERROR")
            return {"error": "BRIDGE_ERROR", "status": resp.status_code}

        try:
            data = resp.json()
        except ValueError:
            _audit("bridge_error", "BRIDGE_ERROR")
            return {"error": "BRIDGE_ERROR", "status": 500}

        _audit("success")
        return {
            "provider": data.get("provider", "unknown"),
            "text": data.get("text", ""),
            "model": data.get("model", ""),
            "trace_id": trace_id,
        }
