# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IpaiSmsProvider(models.Model):
    """SMS Provider configuration for external SMS services."""

    _name = "ipai.sms.provider"
    _description = "SMS Provider"
    _order = "sequence, name"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    provider_type = fields.Selection(
        [
            ("twilio", "Twilio"),
            ("infobip", "Infobip"),
            ("nexmo", "Vonage/Nexmo"),
            ("custom", "Custom HTTP API"),
        ],
        string="Provider Type",
        required=True,
        default="twilio",
    )

    # API Configuration
    base_url = fields.Char(
        string="API Base URL", help="Base URL for the SMS provider API"
    )

    account_sid = fields.Char(
        string="Account SID / API User", help="Account identifier for the provider"
    )

    # Secrets stored via system params
    auth_param_key = fields.Char(
        string="Auth Token Parameter",
        help="System parameter key containing the auth token (e.g., ipai.sms.twilio_token)",
    )

    sender_id = fields.Char(
        string="Sender ID / From Number",
        help="Default sender phone number or alphanumeric ID",
    )

    timeout = fields.Integer(
        string="Timeout (seconds)", default=30, help="Request timeout"
    )

    max_retries = fields.Integer(
        string="Max Retries",
        default=3,
    )

    # Webhook configuration
    webhook_enabled = fields.Boolean(
        string="Enable Webhooks", default=True, help="Enable delivery receipt webhooks"
    )

    notes = fields.Text(string="Notes")

    message_ids = fields.One2many("ipai.sms.message", "provider_id", string="Messages")
    message_count = fields.Integer(compute="_compute_message_count")

    @api.depends("message_ids")
    def _compute_message_count(self):
        for rec in self:
            rec.message_count = len(rec.message_ids)

    def get_auth_token(self):
        """Retrieve auth token from system parameters."""
        self.ensure_one()
        if self.auth_param_key:
            return (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(self.auth_param_key, default="")
            )
        return ""

    def test_connection(self):
        """Test provider connection."""
        self.ensure_one()
        _logger.info("Testing SMS provider: %s (%s)", self.name, self.provider_type)
        # Placeholder - implement per provider
        return {"success": True, "message": "Connection test not implemented"}

    @api.model
    def get_default_provider(self):
        """Get the default active provider."""
        return self.search([("active", "=", True)], limit=1, order="sequence")
