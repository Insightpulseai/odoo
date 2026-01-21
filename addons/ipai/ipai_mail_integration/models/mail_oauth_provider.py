# -*- coding: utf-8 -*-
"""
IPAI Mail OAuth Provider

CE-safe replacement for EE mail_plugin OAuth integration.
This model does NOT inherit from any EE models.
"""

import logging
import requests
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IpaiMailOAuthProvider(models.Model):
    """Mail OAuth Provider for Gmail/Outlook integration."""

    _name = "ipai.mail.oauth.provider"
    _description = "IPAI Mail OAuth Provider"
    _order = "sequence, name"

    name = fields.Char(required=True, string="Provider Name")
    sequence = fields.Integer(default=10)

    provider_type = fields.Selection(
        [
            ("google", "Google (Gmail)"),
            ("microsoft", "Microsoft (Outlook 365)"),
        ],
        required=True,
        string="Provider Type",
    )

    # OAuth Configuration
    client_id = fields.Char(string="Client ID")
    tenant_id = fields.Char(
        string="Tenant ID",
        help="Microsoft tenant ID (use 'common' for multi-tenant)",
    )

    # Endpoints (auto-filled based on provider_type)
    auth_endpoint = fields.Char(string="Auth Endpoint", compute="_compute_endpoints", store=True)
    token_endpoint = fields.Char(string="Token Endpoint", compute="_compute_endpoints", store=True)
    api_endpoint = fields.Char(string="API Endpoint", compute="_compute_endpoints", store=True)

    # Scope
    scope = fields.Text(
        string="OAuth Scope",
        default="openid email profile",
        help="Space-separated OAuth scopes",
    )

    # State
    state = fields.Selection(
        [
            ("draft", "Not Connected"),
            ("authorized", "Authorized"),
            ("error", "Error"),
        ],
        default="draft",
        string="Status",
    )
    error_message = fields.Text(string="Error Message")

    active = fields.Boolean(default=True)

    @api.depends("provider_type", "tenant_id")
    def _compute_endpoints(self):
        """Compute OAuth endpoints based on provider type."""
        for rec in self:
            if rec.provider_type == "google":
                rec.auth_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
                rec.token_endpoint = "https://oauth2.googleapis.com/token"
                rec.api_endpoint = "https://gmail.googleapis.com/gmail/v1"
            elif rec.provider_type == "microsoft":
                tenant = rec.tenant_id or "common"
                rec.auth_endpoint = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
                rec.token_endpoint = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
                rec.api_endpoint = "https://graph.microsoft.com/v1.0"
            else:
                rec.auth_endpoint = False
                rec.token_endpoint = False
                rec.api_endpoint = False

    def action_test_connection(self):
        """Test OAuth connection."""
        self.ensure_one()

        if not self.client_id:
            raise UserError("Client ID is required")

        # For now, just validate endpoints are reachable
        try:
            response = requests.get(
                self.auth_endpoint,
                timeout=10,
            )
            if response.status_code in (200, 302, 400):
                self.write({"state": "authorized", "error_message": False})
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "Connection Test",
                        "message": f"{self.name} endpoint is reachable",
                        "type": "success",
                    },
                }
        except requests.RequestException as e:
            self.write({"state": "error", "error_message": str(e)})
            raise UserError(f"Connection failed: {e}")

    def get_authorization_url(self, redirect_uri, state=None):
        """Generate OAuth authorization URL."""
        self.ensure_one()

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": self.scope,
            "access_type": "offline",
        }

        if state:
            params["state"] = state

        if self.provider_type == "google":
            params["prompt"] = "consent"
        elif self.provider_type == "microsoft":
            params["response_mode"] = "query"

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.auth_endpoint}?{query_string}"
