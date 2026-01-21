# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class IntegrationWebhookController(http.Controller):
    """Controller for receiving incoming webhooks from external integrations."""

    @http.route(
        "/integrations/<string:connector_code>/webhook",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def receive_webhook(self, connector_code, **kwargs):
        """
        Generic webhook receiver endpoint.

        The actual webhook processing is delegated to the
        connector-specific modules (ipai_mattermost_connector, etc.)
        """
        # Find the connector
        connector = (
            request.env["ipai.integration.connector"]
            .sudo()
            .search(
                [
                    ("code", "=", connector_code),
                    ("state", "=", "active"),
                ],
                limit=1,
            )
        )

        if not connector:
            _logger.warning(
                "Webhook received for unknown connector: %s", connector_code
            )
            return {"status": "error", "message": "Unknown connector"}

        # Log the incoming webhook
        request.env["ipai.integration.audit"].sudo().log(
            connector.id,
            "webhook_received",
            f"Incoming webhook from {connector_code}",
            request_method="POST",
            request_payload=json.dumps(request.jsonrequest or {}),
        )

        # Find matching webhook configuration
        # Signature validation is handled by connector-specific code

        return {"status": "ok", "connector": connector_code}

    @http.route(
        "/integrations/<string:connector_code>/webhook/<string:webhook_id>",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def receive_webhook_specific(self, connector_code, webhook_id, **kwargs):
        """
        Receive webhook at a specific endpoint.

        This allows multiple webhook endpoints per connector.
        """
        webhook = (
            request.env["ipai.integration.webhook"]
            .sudo()
            .search(
                [
                    ("connector_id.code", "=", connector_code),
                    ("id", "=", int(webhook_id)),
                    ("direction", "=", "incoming"),
                    ("active", "=", True),
                ],
                limit=1,
            )
        )

        if not webhook:
            _logger.warning(
                "Webhook received for unknown endpoint: %s/%s",
                connector_code,
                webhook_id,
            )
            return {"status": "error", "message": "Unknown webhook endpoint"}

        # Validate signature if required
        signature = request.httprequest.headers.get("X-Signature")
        if webhook.signing_secret and signature:
            payload = json.dumps(request.jsonrequest or {})
            if not webhook.verify_signature(payload, signature):
                _logger.warning("Invalid webhook signature for %s", webhook_id)
                return {"status": "error", "message": "Invalid signature"}

        # Update stats
        webhook.sudo().write(
            {
                "last_triggered": request.env.cr.now(),
                "success_count": webhook.success_count + 1,
            }
        )

        # Log
        request.env["ipai.integration.audit"].sudo().log(
            webhook.connector_id.id,
            "webhook_received",
            f"Webhook received at {webhook.name}",
            request_method="POST",
        )

        return {"status": "ok", "webhook": webhook.name}

    @http.route(
        "/integrations/slash/<string:bot_username>/<string:command>",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def handle_slash_command(self, bot_username, command, **kwargs):
        """
        Handle incoming slash commands from chat integrations.
        """
        # Find the bot and command
        bot_command = (
            request.env["ipai.integration.bot.command"]
            .sudo()
            .search(
                [
                    ("bot_id.bot_username", "=", bot_username),
                    ("command", "=", f"/{command}"),
                    ("active", "=", True),
                ],
                limit=1,
            )
        )

        if not bot_command:
            return {
                "response_type": "ephemeral",
                "text": f"Unknown command: /{command}",
            }

        # Delegate to handler model if specified
        if bot_command.handler_model and bot_command.handler_method:
            handler = request.env[bot_command.handler_model].sudo()
            if hasattr(handler, bot_command.handler_method):
                method = getattr(handler, bot_command.handler_method)
                return method(bot_command, request.jsonrequest)

        return {
            "response_type": bot_command.response_type,
            "text": f"Command /{command} received but no handler configured.",
        }
