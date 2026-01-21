# -*- coding: utf-8 -*-
import hashlib
import hmac
import secrets
from odoo import api, fields, models


class IntegrationWebhook(models.Model):
    """Webhook configuration for integrations."""

    _name = "ipai.integration.webhook"
    _description = "Integration Webhook"
    _order = "name"

    name = fields.Char(required=True)
    connector_id = fields.Many2one(
        "ipai.integration.connector", required=True, ondelete="cascade"
    )
    active = fields.Boolean(default=True)

    direction = fields.Selection(
        [
            ("incoming", "Incoming (receive from external)"),
            ("outgoing", "Outgoing (send to external)"),
        ],
        required=True,
        default="incoming",
    )

    # Incoming webhook settings
    endpoint_path = fields.Char(
        help="Local endpoint path (e.g., /integrations/mattermost/webhook)"
    )
    signing_secret = fields.Char(
        help="Secret for validating incoming webhook signatures"
    )

    # Outgoing webhook settings
    target_url = fields.Char(help="External URL to send webhooks to")
    trigger_model = fields.Char(help="Odoo model that triggers this webhook")
    trigger_events = fields.Selection(
        [
            ("create", "On Create"),
            ("write", "On Update"),
            ("unlink", "On Delete"),
            ("all", "All Events"),
        ],
        default="all",
    )

    # Payload settings
    payload_template = fields.Text(
        help="JSON template for webhook payload (Jinja2 syntax)"
    )
    content_type = fields.Selection(
        [
            ("application/json", "JSON"),
            ("application/x-www-form-urlencoded", "Form URL Encoded"),
        ],
        default="application/json",
    )

    # Security
    include_signature = fields.Boolean(
        default=True, help="Include HMAC signature in outgoing webhooks"
    )

    # Stats
    last_triggered = fields.Datetime(readonly=True)
    success_count = fields.Integer(readonly=True)
    failure_count = fields.Integer(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("signing_secret"):
                vals["signing_secret"] = secrets.token_urlsafe(32)
        return super().create(vals_list)

    def action_regenerate_secret(self):
        """Generate a new signing secret."""
        self.ensure_one()
        self.signing_secret = secrets.token_urlsafe(32)
        return True

    def verify_signature(self, payload, signature):
        """Verify incoming webhook signature."""
        self.ensure_one()
        if not self.signing_secret:
            return False
        expected = hmac.new(
            self.signing_secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def generate_signature(self, payload):
        """Generate signature for outgoing webhook."""
        self.ensure_one()
        if not self.signing_secret:
            return None
        return hmac.new(
            self.signing_secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()
