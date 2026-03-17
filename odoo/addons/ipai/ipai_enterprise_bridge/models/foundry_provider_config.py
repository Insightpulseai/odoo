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
    def _resolve_auth_headers(self):
        """Build auth headers based on configured auth_mode.

        Returns (headers_dict, missing_hint_or_None).
        """
        import os  # noqa: PLC0415

        if self.auth_mode == "api_key":
            key = os.getenv("AZURE_AI_FOUNDRY_API_KEY")
            if key:
                return {"api-key": key}, None
            return {}, "AZURE_AI_FOUNDRY_API_KEY"

        # managed_identity or oauth2 — both use Bearer token
        # Try azure-identity SDK first (managed_identity), then env var fallback
        if self.auth_mode == "managed_identity":
            try:
                from azure.identity import DefaultAzureCredential  # noqa: PLC0415
                cred = DefaultAzureCredential()
                token = cred.get_token(
                    "https://cognitiveservices.azure.com/.default"
                )
                return {"Authorization": "Bearer " + token.token}, None
            except Exception:
                pass  # fall through to env var

        bearer = os.getenv("AZURE_AI_FOUNDRY_BEARER_TOKEN")
        if bearer:
            return {"Authorization": "Bearer " + bearer}, None
        env_hint = (
            "azure-identity SDK or AZURE_AI_FOUNDRY_BEARER_TOKEN"
            if self.auth_mode == "managed_identity"
            else "AZURE_AI_FOUNDRY_BEARER_TOKEN"
        )
        return {}, env_hint

    @staticmethod
    def _extract_resource_base(endpoint):
        """Extract the resource-level base URL from a Foundry project URL.

        Azure AI Foundry project URLs look like:
          https://<resource>.services.ai.azure.com/api/projects/<project>
        The OpenAI-compatible API lives at the resource level:
          https://<resource>.services.ai.azure.com/openai/models
        """
        from urllib.parse import urlparse  # noqa: PLC0415

        parsed = urlparse(endpoint.rstrip("/"))
        # Strip /api/projects/<name> suffix if present
        path = parsed.path
        idx = path.find("/api/projects")
        if idx >= 0:
            path = path[:idx]
        return f"{parsed.scheme}://{parsed.netloc}{path}"

    def action_test_connection(self):
        """Test connectivity to the configured Foundry endpoint."""
        self.ensure_one()
        import requests  # noqa: PLC0415

        headers, missing = self._resolve_auth_headers()
        base = self._extract_resource_base(self.endpoint)

        try:
            resp = requests.get(
                base.rstrip("/") + "/openai/models",
                params={"api-version": self.api_version or "2024-12-01-preview"},
                headers=headers,
                timeout=10,
            )
            if resp.status_code < 400:
                result = _("OK — HTTP %s (auth_mode=%s)") % (
                    resp.status_code, self.auth_mode,
                )
            elif resp.status_code == 401 and missing:
                result = _(
                    "HTTP 401 — auth_mode=%s but credentials not found. "
                    "Set %s in the container env."
                ) % (self.auth_mode, missing)
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
