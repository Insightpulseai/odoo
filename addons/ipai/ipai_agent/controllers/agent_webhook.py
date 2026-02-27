# -*- coding: utf-8 -*-
"""
POST /ipai/agent/callback

Receives async completion callbacks from Supabase Edge Functions / MCP.

Security
--------
Every request must carry:
  x-signature : HMAC-SHA256(body + x-timestamp, HMAC_SECRET)
  x-timestamp : Unix epoch string (seconds)

The HMAC secret is read from ir.config_parameter key
``ipai.agent.hmac_secret`` — never hardcoded.

Timestamp window: ±300 seconds to prevent replay attacks.

Expected JSON body
------------------
{
  "run_id"         : "AGT/2026/0042",
  "external_run_id": "supabase-edge-xxx",
  "state"          : "succeeded",   # or "failed"
  "tool_calls"     : [...],
  "output"         : {...},
  "evidence_log"   : "...",
  "error_message"  : null
}
"""

import hashlib
import hmac
import json
import logging
import time

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

TIMESTAMP_WINDOW = 300  # seconds — reject requests outside ±5 min window


class IpaiAgentWebhook(http.Controller):

    @http.route("/ipai/agent/callback", type="json", auth="none", methods=["POST"], csrf=False)
    def agent_callback(self, **kwargs):
        """Receive and process an agent run completion callback."""
        body_bytes = request.httprequest.get_data()

        # ── Signature verification ────────────────────────────────────────
        signature = request.httprequest.headers.get("x-signature", "")
        timestamp_str = request.httprequest.headers.get("x-timestamp", "")

        env = request.env(user=1)  # SUPERUSER for lookup only
        hmac_secret = env["ir.config_parameter"].get_param("ipai.agent.hmac_secret", "")

        if not hmac_secret:
            _logger.error("/ipai/agent/callback: hmac_secret not configured")
            return {"ok": False, "error": "not configured"}

        if not self._verify_signature(body_bytes, timestamp_str, signature, hmac_secret):
            _logger.warning("/ipai/agent/callback: signature verification failed")
            return {"ok": False, "error": "invalid signature"}

        # ── Parse body ────────────────────────────────────────────────────
        try:
            data = json.loads(body_bytes)
        except json.JSONDecodeError as exc:
            _logger.error("/ipai/agent/callback: invalid JSON — %s", exc)
            return {"ok": False, "error": "invalid json"}

        run_name = data.get("run_id")
        if not run_name:
            return {"ok": False, "error": "missing run_id"}

        # ── Require event_id + timestamp in payload body ──────────────────
        if not data.get("event_id"):
            _logger.warning(
                "/ipai/agent/callback: missing event_id in payload for run %s", run_name
            )
            return {"ok": False, "error": "missing event_id"}

        if not data.get("timestamp"):
            _logger.warning(
                "/ipai/agent/callback: missing timestamp in payload for run %s", run_name
            )
            return {"ok": False, "error": "missing timestamp"}

        # ── Apply event with idempotency guard ────────────────────────────
        run = env["ipai.agent.run"].search([("name", "=", run_name)], limit=1)
        if not run:
            _logger.warning("/ipai/agent/callback: run not found: %s", run_name)
            return {"ok": False, "error": "run not found"}

        applied = run._apply_external_event(data)
        if not applied:
            _logger.info(
                "/ipai/agent/callback: duplicate event for run %s — NOOP", run_name
            )
            return {"ok": True, "noop": True}

        _logger.info(
            "/ipai/agent/callback: run %s updated → %s",
            run_name, data.get("state", "succeeded"),
        )
        return {"ok": True}

    @staticmethod
    def _verify_signature(body_bytes: bytes, timestamp_str: str, signature: str, secret: str) -> bool:
        """
        Verify HMAC-SHA256(body_bytes + timestamp_str.encode(), secret).
        Also rejects requests with a timestamp outside TIMESTAMP_WINDOW.
        """
        if not timestamp_str or not signature:
            return False
        try:
            ts = int(timestamp_str)
        except ValueError:
            return False

        if abs(time.time() - ts) > TIMESTAMP_WINDOW:
            _logger.warning("Callback timestamp %s is outside ±%ss window", ts, TIMESTAMP_WINDOW)
            return False

        expected = hmac.new(
            secret.encode(),
            body_bytes + timestamp_str.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
