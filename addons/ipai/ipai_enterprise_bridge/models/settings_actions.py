# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, models


class ResConfigSettingsActions(models.TransientModel):
    """Action methods for General Settings — split out for clarity.

    These methods live on ``res.config.settings`` via ``_inherit`` and are
    invoked from buttons in the settings XML view.
    """

    _inherit = "res.config.settings"

    # ------------------------------------------------------------------
    # Helper — singleton lookup
    # ------------------------------------------------------------------
    def _get_or_create_singleton(self, model_name, defaults=None):
        """Return the first record of *model_name*, creating one if none exists."""
        record = self.env[model_name].search([], limit=1)
        if not record:
            record = self.env[model_name].create(defaults or {})
        return record

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def action_open_api_keys(self):
        """Open the API Keys management view."""
        return {
            "type": "ir.actions.act_url",
            "url": "/odoo/settings/api-keys",
            "target": "self",
        }

    def action_open_foundry_provider(self):
        """Open Foundry provider configuration."""
        config = self._get_or_create_singleton(
            "ipai.foundry.provider.config",
            {"name": "Default", "endpoint": ""},
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Foundry Configuration"),
            "res_model": "ipai.foundry.provider.config",
            "view_mode": "form",
            "target": "new",
            "res_id": config.id,
        }

    def action_open_doc_digitization_provider(self):
        """Open Document Digitization configuration."""
        config = self._get_or_create_singleton(
            "ipai.doc.digitization.config",
            {"name": "Default"},
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Document Digitization Configuration"),
            "res_model": "ipai.doc.digitization.config",
            "view_mode": "form",
            "target": "new",
            "res_id": config.id,
        }

    def action_apply_google_oauth(self):
        """Create or update the Google Workspace auth.oauth.provider record."""
        self.ensure_one()
        ICP = self.env["ir.config_parameter"].sudo()
        enabled = ICP.get_param("ipai.oauth.google.enabled", "False") == "True"
        client_id = ICP.get_param("ipai.oauth.google.client_id", "")
        domain = ICP.get_param("ipai.oauth.google.workspace_domain", "w9studio.net")

        if not client_id:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Google OAuth"),
                    "message": _("Client ID is empty. Configure it before enabling the provider."),
                    "type": "warning",
                    "sticky": False,
                },
            }

        Provider = self.env["auth.oauth.provider"].sudo()
        google = Provider.search([("name", "=like", "Google Workspace%")], limit=1)

        # Always compute auth_endpoint from constant base + domain.
        # This is idempotent: repeated calls never double-append ?hd=.
        _GOOGLE_AUTH_BASE = "https://accounts.google.com/o/oauth2/v2/auth"
        auth_endpoint = _GOOGLE_AUTH_BASE
        if domain:
            auth_endpoint = f"{_GOOGLE_AUTH_BASE}?hd={domain}"

        vals = {
            "name": "Google Workspace (W9 Studio)",
            "enabled": enabled,
            "client_id": client_id,
            "auth_endpoint": auth_endpoint,
            "validation_endpoint": "https://www.googleapis.com/oauth2/v3/tokeninfo",
            "scope": "openid email profile",
            "data_endpoint": "https://www.googleapis.com/oauth2/v1/userinfo?access_token=",
            "css_class": "fa fa-fw fa-google",
            "body": "Log in with Google",
            "sequence": 20,
        }

        if google:
            google.write(vals)
        else:
            Provider.create(vals)

        msg = _("Google Workspace provider updated.") if google else _("Google Workspace provider created.")
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {"title": _("Google OAuth"), "message": msg, "type": "success", "sticky": False},
        }

    def action_test_foundry_connection(self):
        """Test the Foundry endpoint connection from Settings."""
        config = self.env["ipai.foundry.provider.config"].search([], limit=1)
        if not config:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Foundry Connection Test"),
                    "message": _("No Foundry configuration found. Configure it first."),
                    "type": "warning",
                    "sticky": False,
                },
            }
        return config.action_test_connection()

    def action_test_doc_digitization_connection(self):
        """Test the OCR / Document Intelligence endpoint from Settings."""
        config = self.env["ipai.doc.digitization.config"].search([], limit=1)
        if not config:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Document Digitization Test"),
                    "message": _("No Document Digitization configuration found. Configure it first."),
                    "type": "warning",
                    "sticky": False,
                },
            }
        return config.action_test_connection()
