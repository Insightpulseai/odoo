# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models


class FoundryProviderConfig(models.Model):
    """Singleton configuration for Microsoft Foundry / Azure AI integration.

    Stores non-secret metadata only. API keys and credentials are resolved
    at runtime via environment variables or Azure Key Vault.
    """

    _name = "ipai.foundry.provider.config"
    _description = "Foundry Provider Configuration"
    _rec_name = "name"

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------
    name = fields.Char(
        string="Name",
        default="Default",
        required=True,
    )
    endpoint = fields.Char(
        string="Endpoint URL",
        required=True,
        help="Azure AI Foundry endpoint URL (no secrets).",
    )
    project_name = fields.Char(
        string="Project Name",
        help="Azure AI Foundry project name.",
    )
    model_deployment = fields.Char(
        string="Model Deployment",
        help="Name of the deployed model (e.g. gpt-4o, gpt-4o-mini).",
    )
    auth_mode = fields.Selection(
        selection=[
            ("managed_identity", "Managed Identity"),
            ("api_key", "API Key"),
            ("oauth2", "OAuth2"),
        ],
        string="Auth Mode",
        default="managed_identity",
        required=True,
        help="Authentication mode. Credentials are never stored here — "
             "they are resolved at runtime from env vars / Key Vault.",
    )
    api_version = fields.Char(
        string="API Version",
        default="2024-12-01-preview",
    )
    last_test_date = fields.Datetime(
        string="Last Test Date",
        readonly=True,
    )
    last_test_result = fields.Char(
        string="Last Test Result",
        readonly=True,
    )

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def action_test_connection(self):
        """Test connectivity to the configured Foundry endpoint."""
        self.ensure_one()
        import requests  # noqa: PLC0415 — deferred import

        try:
            resp = requests.get(
                self.endpoint.rstrip("/") + "/openai/models",
                params={"api-version": self.api_version or "2024-12-01-preview"},
                timeout=10,
            )
            if resp.status_code < 400:
                result = _("OK — HTTP %s") % resp.status_code
            else:
                result = _("Error — HTTP %s: %s") % (
                    resp.status_code,
                    resp.text[:200],
                )
        except requests.RequestException as exc:
            result = _("Connection failed: %s") % str(exc)[:200]

        self.write(
            {
                "last_test_date": fields.Datetime.now(),
                "last_test_result": result,
            }
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Foundry Connection Test"),
                "message": result,
                "type": "info" if "OK" in result else "warning",
                "sticky": False,
            },
        }
