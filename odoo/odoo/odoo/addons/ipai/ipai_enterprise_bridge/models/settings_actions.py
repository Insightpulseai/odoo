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
