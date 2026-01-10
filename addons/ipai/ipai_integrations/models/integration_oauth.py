# -*- coding: utf-8 -*-
import secrets
from odoo import api, fields, models


class IntegrationOAuth(models.Model):
    """OAuth application configuration for integrations."""

    _name = "ipai.integration.oauth"
    _description = "Integration OAuth App"
    _order = "name"

    name = fields.Char(required=True)
    connector_id = fields.Many2one(
        "ipai.integration.connector",
        required=True,
        ondelete="cascade"
    )
    active = fields.Boolean(default=True)

    # OAuth credentials
    client_id = fields.Char(readonly=True)
    client_secret = fields.Char(
        groups="ipai_integrations.group_integration_admin"
    )

    # URLs
    redirect_uris = fields.Text(
        help="Allowed redirect URIs (one per line)"
    )
    homepage_url = fields.Char()
    icon = fields.Binary(attachment=True)

    # OAuth settings
    grant_types = fields.Selection([
        ("authorization_code", "Authorization Code"),
        ("client_credentials", "Client Credentials"),
        ("both", "Both"),
    ], default="authorization_code")

    token_expiry = fields.Integer(
        default=3600,
        help="Access token expiry in seconds"
    )
    refresh_token_expiry = fields.Integer(
        default=86400 * 30,
        help="Refresh token expiry in seconds"
    )

    # Scopes
    scope_read = fields.Boolean(default=True)
    scope_write = fields.Boolean(default=False)
    scope_admin = fields.Boolean(default=False)

    # Status
    state = fields.Selection([
        ("draft", "Draft"),
        ("active", "Active"),
        ("revoked", "Revoked"),
    ], default="draft")

    # Stats
    token_count = fields.Integer(
        compute="_compute_token_count",
        string="Active Tokens"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("client_id"):
                vals["client_id"] = secrets.token_urlsafe(24)
            if not vals.get("client_secret"):
                vals["client_secret"] = secrets.token_urlsafe(32)
        return super().create(vals_list)

    def _compute_token_count(self):
        for rec in self:
            rec.token_count = 0  # Placeholder - implement token tracking

    def action_regenerate_secret(self):
        """Regenerate client secret."""
        self.ensure_one()
        self.client_secret = secrets.token_urlsafe(32)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Secret Regenerated",
                "message": "Client secret has been regenerated. Update your application.",
                "type": "warning",
            }
        }

    def action_revoke(self):
        """Revoke the OAuth application."""
        self.ensure_one()
        self.state = "revoked"
