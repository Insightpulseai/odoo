# -*- coding: utf-8 -*-
"""
IPAI AI Connectors - Webhook Controller
========================================

Provides the inbound webhook endpoint for external integrations.

Endpoint: POST /ipai_ai_connectors/event

Security:
---------
- Token authentication via IPAI_CONNECTORS_TOKEN env var
- CSRF disabled for external webhooks
- Public route (no Odoo session required)

Usage:
------
curl -X POST https://your-odoo.com/ipai_ai_connectors/event \\
  -H 'Content-Type: application/json' \\
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "token": "your_secret_token",
      "source": "n8n",
      "event_type": "workflow.completed",
      "ref": "workflow_123",
      "payload": {"status": "success"}
    },
    "id": 1
  }'
"""
import os
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class IPAIAIConnectorsController(http.Controller):
    """Controller for inbound integration webhooks."""

    @http.route(
        "/ipai_ai_connectors/event",
        type="json",
        auth="public",
        csrf=False,
        methods=["POST"],
    )
    def event(
        self,
        token=None,
        source=None,
        event_type=None,
        ref=None,
        payload=None,
        company_id=None,
    ):
        """
        Receive and store an integration event.

        Args:
            token: Authentication token (required)
            source: Event source (n8n, github, slack, custom)
            event_type: Event type identifier
            ref: Optional external reference ID
            payload: Optional event payload dict
            company_id: Optional company ID for multi-tenant

        Returns:
            dict: {ok: bool, event_id: int, error: str}
        """
        # Validate token
        expected_token = os.environ.get("IPAI_CONNECTORS_TOKEN", "").strip()
        if not expected_token:
            _logger.error("IPAI_CONNECTORS_TOKEN not configured")
            return {"ok": False, "error": "Connector not configured"}

        if not token or token != expected_token:
            _logger.warning(
                "Invalid connector token from %s",
                request.httprequest.remote_addr,
            )
            return {"ok": False, "error": "Invalid token"}

        # Validate required fields
        if not source:
            return {"ok": False, "error": "Missing 'source' parameter"}
        if not event_type:
            return {"ok": False, "error": "Missing 'event_type' parameter"}

        # Create event
        try:
            Event = request.env["ipai.ai.event"]
            event = Event.create_from_webhook(
                source=source,
                event_type=event_type,
                ref=ref,
                payload=payload,
                company_id=company_id,
            )

            return {
                "ok": True,
                "event_id": event.id,
            }

        except Exception as e:
            _logger.exception("Error creating event")
            return {
                "ok": False,
                "error": f"Failed to create event: {str(e)[:200]}",
            }

    @http.route(
        "/ipai_ai_connectors/health",
        type="json",
        auth="public",
        csrf=False,
        methods=["GET", "POST"],
    )
    def health(self):
        """
        Health check endpoint for monitoring.

        Returns:
            dict: {status: "ok", module: "ipai_ai_connectors"}
        """
        return {
            "status": "ok",
            "module": "ipai_ai_connectors",
            "version": "18.0.1.0.0",
        }
