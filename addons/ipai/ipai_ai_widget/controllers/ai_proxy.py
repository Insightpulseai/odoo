# © 2026 InsightPulse AI — License LGPL-3.0-or-later
"""
IPAI AI proxy controller.

Routes:
    POST /ipai/ai/ask  — JSON-RPC, auth=user
        Request:  { prompt: str }
        Response: { provider, text, model, trace_id } | { error: str, status: int }

Error codes (greppable):
    BRIDGE_URL_NOT_CONFIGURED — ir.config_parameter ipai_ai_widget.bridge_url is unset
    AI_KEY_NOT_CONFIGURED     — bridge returned 503 (key missing on provider side)
    BRIDGE_TIMEOUT            — bridge did not respond within TIMEOUT_SECONDS
    BRIDGE_ERROR              — any other bridge-side failure
    PROMPT_REQUIRED           — request body missing prompt field
"""
import logging

import requests

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)
TIMEOUT_SECONDS = 30


class IpaiAiProxyController(http.Controller):

    @http.route("/ipai/ai/ask", type="json", auth="user", methods=["POST"], csrf=False)
    def ask_ai(self, prompt=None, **_kwargs):
        if not prompt or not str(prompt).strip():
            return {"error": "PROMPT_REQUIRED", "status": 400}

        bridge_url = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_ai_widget.bridge_url", default="")
        )
        if not bridge_url:
            _logger.warning("ipai_ai_widget: BRIDGE_URL_NOT_CONFIGURED")
            return {"error": "BRIDGE_URL_NOT_CONFIGURED", "status": 503}

        try:
            resp = requests.post(
                bridge_url,
                json={"prompt": str(prompt).strip()},
                timeout=TIMEOUT_SECONDS,
                headers={"Content-Type": "application/json"},
            )
        except requests.Timeout:
            _logger.warning("ipai_ai_widget: BRIDGE_TIMEOUT calling %s", bridge_url)
            return {"error": "BRIDGE_TIMEOUT", "status": 504}
        except requests.RequestException as exc:
            _logger.error("ipai_ai_widget: BRIDGE_ERROR — %s", exc)
            return {"error": "BRIDGE_ERROR", "status": 500}

        if resp.status_code == 503:
            _logger.warning("ipai_ai_widget: AI_KEY_NOT_CONFIGURED (bridge 503)")
            return {"error": "AI_KEY_NOT_CONFIGURED", "status": 503}

        if not resp.ok:
            _logger.error(
                "ipai_ai_widget: BRIDGE_ERROR HTTP %s from %s", resp.status_code, bridge_url
            )
            return {"error": "BRIDGE_ERROR", "status": resp.status_code}

        try:
            data = resp.json()
        except ValueError:
            return {"error": "BRIDGE_ERROR", "status": 500}

        # Enforce contractual response shape
        return {
            "provider": data.get("provider", "unknown"),
            "text": data.get("text", ""),
            "model": data.get("model", ""),
            "trace_id": data.get("trace_id", ""),
        }
