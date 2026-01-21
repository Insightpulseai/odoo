# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IntegrationConnector(models.Model):
    """Base model for external integration connectors."""

    _name = "ipai.integration.connector"
    _description = "Integration Connector"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(
        required=True,
        help="Unique code for the connector (e.g., mattermost, focalboard, n8n)",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    connector_type = fields.Selection(
        [
            ("mattermost", "Mattermost"),
            ("focalboard", "Focalboard"),
            ("n8n", "n8n"),
            ("custom", "Custom"),
        ],
        required=True,
    )

    # Connection settings
    base_url = fields.Char(
        string="Base URL",
        help="Base URL of the external service (e.g., https://chat.insightpulseai.net)",
    )
    api_version = fields.Char(default="v4", help="API version to use")

    # Authentication
    auth_type = fields.Selection(
        [
            ("token", "Personal Access Token"),
            ("oauth", "OAuth 2.0"),
            ("basic", "Basic Auth"),
            ("none", "None"),
        ],
        default="token",
    )

    # Status
    state = fields.Selection(
        [
            ("draft", "Not Configured"),
            ("testing", "Testing"),
            ("active", "Active"),
            ("error", "Error"),
        ],
        default="draft",
        readonly=True,
    )
    last_ping = fields.Datetime(readonly=True)
    last_error = fields.Text(readonly=True)

    # Related records
    webhook_ids = fields.One2many(
        "ipai.integration.webhook", "connector_id", string="Webhooks"
    )
    bot_ids = fields.One2many("ipai.integration.bot", "connector_id", string="Bots")
    oauth_app_ids = fields.One2many(
        "ipai.integration.oauth", "connector_id", string="OAuth Apps"
    )
    audit_ids = fields.One2many(
        "ipai.integration.audit", "connector_id", string="Audit Logs"
    )

    _sql_constraints = [
        ("code_uniq", "unique(code)", "Connector code must be unique!"),
    ]

    def action_test_connection(self):
        """Test the connection to the external service."""
        self.ensure_one()
        self._log_audit("test_connection", "Testing connection...")
        # Actual implementation in connector-specific modules
        return True

    def action_activate(self):
        """Activate the connector after successful test."""
        self.ensure_one()
        self.write({"state": "active"})
        self._log_audit("activate", "Connector activated")

    def _log_audit(self, action, message, level="info"):
        """Create an audit log entry."""
        self.env["ipai.integration.audit"].create(
            {
                "connector_id": self.id,
                "action": action,
                "message": message,
                "level": level,
            }
        )
