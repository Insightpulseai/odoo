"""
Odoo Copilot — Slack Events API inbound controller.

Thin relay: verifies Slack signing secret, handles url_verification challenge,
forwards message events to n8n webhook. All AI logic, retries, callback routing,
and conversation orchestration stay in n8n.
"""

import hashlib
import hmac
import json
import logging
import os
import time

import requests
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class SlackEventsController(http.Controller):

    @http.route(
        "/ipai/slack/events",
        type="json",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def slack_events(self, **kw):
        """Handle Slack Events API callbacks."""
        body = request.jsonrequest

        # Handle Slack URL verification challenge
        if body.get("type") == "url_verification":
            return {"challenge": body.get("challenge", "")}

        # Verify Slack signing secret
        if not self._verify_slack_signature():
            _logger.warning("Slack signature verification failed")
            return {"error": "invalid_signature"}

        event = body.get("event", {})
        event_type = event.get("type")

        # Only handle message events (not bot messages)
        if event_type == "message" and not event.get("bot_id"):
            self._forward_to_n8n(
                platform="slack",
                platform_user_id=event.get("user", ""),
                message=event.get("text", ""),
                channel=event.get("channel", ""),
                ts=event.get("ts", ""),
            )

        return {"ok": True}

    def _verify_slack_signature(self):
        """Verify request came from Slack using signing secret."""
        signing_secret = os.environ.get("SLACK_SIGNING_SECRET", "")
        if not signing_secret:
            _logger.warning("SLACK_SIGNING_SECRET not set, skipping verification")
            return True  # Allow in dev when not configured

        timestamp = request.httprequest.headers.get("X-Slack-Request-Timestamp", "")
        sig_header = request.httprequest.headers.get("X-Slack-Signature", "")

        if not timestamp or not sig_header:
            return False

        # Reject requests older than 5 minutes
        if abs(time.time() - int(timestamp)) > 300:
            return False

        raw_body = request.httprequest.get_data(as_text=True)
        sig_basestring = f"v0:{timestamp}:{raw_body}"
        computed = "v0=" + hmac.new(
            signing_secret.encode(), sig_basestring.encode(), hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed, sig_header)

    def _forward_to_n8n(self, platform, platform_user_id, message, channel, ts):
        """Forward message to n8n AI Agent Router webhook."""
        n8n_url = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_ai_copilot.n8n_agent_router_url", "")
        )
        if not n8n_url:
            _logger.warning("n8n agent router URL not configured (ipai_ai_copilot.n8n_agent_router_url)")
            return

        callback_url = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_slack_connector.callback_url", "")
        )

        payload = {
            "platform": platform,
            "platform_user_id": platform_user_id,
            "message": message,
            "channel": channel,
            "ts": ts,
            "callback_url": callback_url,
        }

        try:
            requests.post(n8n_url, json=payload, timeout=5)
        except requests.RequestException as exc:
            _logger.error("Failed to forward to n8n: %s", exc)
