# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import os

from odoo import _, api, models
from odoo.exceptions import UserError


class SlackConnector(models.AbstractModel):
    _name = "ipai.slack.connector"
    _description = "IPAI Slack Outbound Connector"

    @api.model
    def _ipai_slack_enabled(self):
        """Return True if SLACK_WEBHOOK_URL env var is configured."""
        return bool(os.environ.get("SLACK_WEBHOOK_URL", "").strip())

    @api.model
    def _ipai_post_message(self, text, channel=None, blocks=None):
        """POST a message to the configured Slack Incoming Webhook.

        Args:
            text (str): Message text (required).
            channel (str | None): Override destination channel (optional).
                Slack ignores this for Basic Incoming Webhooks; use for
                app-level tokens with chat.postMessage.
            blocks (list | None): Slack Block Kit blocks payload (optional).

        Returns:
            True on success.

        Raises:
            UserError: If SLACK_WEBHOOK_URL is not set, or if the webhook
                call fails (HTTP error or network error).
        """
        url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
        if not url:
            raise UserError(
                _("Slack webhook not configured (SLACK_WEBHOOK_URL missing)")
            )

        payload = {"text": text}
        if channel:
            payload["channel"] = channel
        if blocks:
            payload["blocks"] = blocks

        from ..utils import slack_client

        try:
            slack_client.post_webhook(url, payload)
        except Exception as exc:
            raise UserError(_("Slack notification failed: %s") % exc) from exc

        return True
