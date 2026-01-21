# -*- coding: utf-8 -*-
"""
Mail Gateway - Direct SMTP/Mailgun Integration

Provides direct email sending without IAP dependencies.
"""
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IpaiMailGateway(models.Model):
    """Configuration for direct mail gateways."""

    _name = "ipai.mail.gateway"
    _description = "IPAI Mail Gateway"

    name = fields.Char(
        string="Gateway Name",
        required=True,
    )
    gateway_type = fields.Selection(
        [
            ("smtp", "SMTP"),
            ("mailgun", "Mailgun API"),
            ("sendgrid", "SendGrid API"),
            ("ses", "Amazon SES"),
        ],
        string="Gateway Type",
        required=True,
        default="smtp",
    )
    is_active = fields.Boolean(
        string="Active",
        default=True,
    )
    is_default = fields.Boolean(
        string="Default Gateway",
        default=False,
    )

    # SMTP Configuration
    smtp_host = fields.Char(
        string="SMTP Host",
    )
    smtp_port = fields.Integer(
        string="SMTP Port",
        default=587,
    )
    smtp_user = fields.Char(
        string="SMTP User",
    )
    smtp_password = fields.Char(
        string="SMTP Password",
    )
    smtp_encryption = fields.Selection(
        [
            ("none", "None"),
            ("starttls", "STARTTLS"),
            ("ssl", "SSL/TLS"),
        ],
        string="Encryption",
        default="starttls",
    )

    # API Gateway Configuration
    api_key = fields.Char(
        string="API Key",
    )
    api_domain = fields.Char(
        string="API Domain",
        help="Domain for API-based gateways (e.g., Mailgun domain)",
    )
    api_endpoint = fields.Char(
        string="API Endpoint",
        help="Custom API endpoint if not using default",
    )

    # OAuth Configuration
    oauth_enabled = fields.Boolean(
        string="OAuth Enabled",
        default=False,
    )
    oauth_client_id = fields.Char(
        string="OAuth Client ID",
    )
    oauth_client_secret = fields.Char(
        string="OAuth Client Secret",
    )
    oauth_token = fields.Char(
        string="OAuth Token",
    )
    oauth_refresh_token = fields.Char(
        string="OAuth Refresh Token",
    )

    # Tracking
    track_opens = fields.Boolean(
        string="Track Opens",
        default=True,
    )
    track_clicks = fields.Boolean(
        string="Track Clicks",
        default=True,
    )

    _sql_constraints = [
        (
            "unique_default_gateway",
            "EXCLUDE (is_default WITH =) WHERE (is_default = TRUE AND is_active = TRUE)",
            "Only one active gateway can be the default.",
        ),
    ]

    @api.model
    def get_default_gateway(self):
        """Get the default active gateway.

        Returns:
            recordset: Default gateway or first active gateway
        """
        gateway = self.search(
            [("is_default", "=", True), ("is_active", "=", True)],
            limit=1,
        )
        if not gateway:
            gateway = self.search([("is_active", "=", True)], limit=1)
        return gateway

    def test_connection(self):
        """Test the gateway connection.

        Returns:
            dict: Result with success status and message
        """
        self.ensure_one()
        try:
            if self.gateway_type == "smtp":
                return self._test_smtp_connection()
            elif self.gateway_type == "mailgun":
                return self._test_mailgun_connection()
            else:
                return {
                    "success": False,
                    "message": f"Test not implemented for {self.gateway_type}",
                }
        except Exception as e:
            _logger.exception("Gateway connection test failed")
            return {"success": False, "message": str(e)}

    def _test_smtp_connection(self):
        """Test SMTP connection."""
        import smtplib

        try:
            if self.smtp_encryption == "ssl":
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
                if self.smtp_encryption == "starttls":
                    server.starttls()

            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)

            server.quit()
            return {"success": True, "message": "SMTP connection successful"}
        except Exception as e:
            return {"success": False, "message": f"SMTP error: {e}"}

    def _test_mailgun_connection(self):
        """Test Mailgun API connection."""
        import requests

        if not self.api_key or not self.api_domain:
            return {"success": False, "message": "API key and domain required"}

        endpoint = self.api_endpoint or "https://api.mailgun.net/v3"
        url = f"{endpoint}/{self.api_domain}/messages"

        try:
            response = requests.get(
                f"{endpoint}/domains/{self.api_domain}",
                auth=("api", self.api_key),
                timeout=10,
            )
            if response.status_code == 200:
                return {"success": True, "message": "Mailgun connection successful"}
            else:
                return {
                    "success": False,
                    "message": f"Mailgun error: {response.status_code}",
                }
        except Exception as e:
            return {"success": False, "message": f"Mailgun error: {e}"}


class IpaiMailLog(models.Model):
    """Log of sent emails for tracking."""

    _name = "ipai.mail.log"
    _description = "IPAI Mail Log"
    _order = "create_date desc"

    gateway_id = fields.Many2one(
        "ipai.mail.gateway",
        string="Gateway",
        ondelete="set null",
    )
    message_id = fields.Char(
        string="Message ID",
        index=True,
    )
    recipient = fields.Char(
        string="Recipient",
        required=True,
    )
    subject = fields.Char(
        string="Subject",
    )
    status = fields.Selection(
        [
            ("sent", "Sent"),
            ("delivered", "Delivered"),
            ("opened", "Opened"),
            ("clicked", "Clicked"),
            ("bounced", "Bounced"),
            ("complained", "Complained"),
            ("failed", "Failed"),
        ],
        string="Status",
        default="sent",
    )
    opened_at = fields.Datetime(
        string="Opened At",
    )
    clicked_at = fields.Datetime(
        string="Clicked At",
    )
    error_message = fields.Text(
        string="Error Message",
    )
