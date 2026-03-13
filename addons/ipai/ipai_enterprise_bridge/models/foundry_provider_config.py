# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


# Regex for validating Foundry project endpoint shape:
#   https://<resource>.services.ai.azure.com/api/projects/<project>
# Also accepts resource-level:
#   https://<resource>.services.ai.azure.com
# And cognitiveservices (Document Intelligence):
#   https://<resource>.cognitiveservices.azure.com
_ENDPOINT_PATTERN = re.compile(
    r"^https://[\w-]+\."
    r"(services\.ai\.azure\.com(/api/projects/[\w-]+)?|"
    r"openai\.azure\.com|"
    r"cognitiveservices\.azure\.com|"
    r"search\.windows\.net)"
    r"/?$"
)


class FoundryProviderConfig(models.Model):
    """Singleton configuration for Microsoft Foundry / Azure AI integration.

    Stores non-secret metadata only. API keys and credentials are resolved
    at runtime via environment variables or Azure Key Vault.

    Endpoint URL families:
      - Foundry project: https://<resource>.services.ai.azure.com/api/projects/<project>
      - Azure OpenAI:    https://<resource>.openai.azure.com
      - Doc Intelligence: https://<resource>.cognitiveservices.azure.com
      - AI Search:       https://<service>.search.windows.net

    Auth audiences vary by family -- see auth_audience field.
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
        help="Azure AI endpoint URL. Expected shapes:\n"
             "  Foundry project: https://<resource>.services.ai.azure.com/api/projects/<project>\n"
             "  Foundry resource: https://<resource>.services.ai.azure.com\n"
             "  Azure OpenAI: https://<resource>.openai.azure.com\n"
             "  Doc Intelligence: https://<resource>.cognitiveservices.azure.com\n"
             "No secrets -- credentials are resolved at runtime from env vars / Key Vault.",
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
    auth_audience = fields.Selection(
        selection=[
            (
                "https://cognitiveservices.azure.com/.default",
                "Cognitive Services (Azure OpenAI, Doc Intelligence)",
            ),
            (
                "https://ai.azure.com/.default",
                "AI Foundry (project-scoped APIs)",
            ),
            (
                "https://search.azure.com/.default",
                "Azure AI Search",
            ),
        ],
        string="Auth Audience",
        default="https://cognitiveservices.azure.com/.default",
        required=True,
        help="OAuth2 token audience for the target API family. "
             "Foundry project APIs use ai.azure.com/.default. "
             "Azure OpenAI and Document Intelligence use "
             "cognitiveservices.azure.com/.default. "
             "Azure AI Search uses search.azure.com/.default.",
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
    # Constraints
    # ------------------------------------------------------------------
    @api.constrains("endpoint")
    def _validate_endpoint_shape(self):
        """Validate that the endpoint URL matches a known Azure AI family."""
        for rec in self:
            if not rec.endpoint:
                continue
            url = rec.endpoint.strip()
            if not _ENDPOINT_PATTERN.match(url):
                raise ValidationError(_(
                    "Endpoint URL does not match a known Azure AI family.\n"
                    "Expected one of:\n"
                    "  https://<resource>.services.ai.azure.com/api/projects/<project>\n"
                    "  https://<resource>.services.ai.azure.com\n"
                    "  https://<resource>.openai.azure.com\n"
                    "  https://<resource>.cognitiveservices.azure.com\n"
                    "  https://<service>.search.windows.net\n"
                    "Got: %s"
                ) % url)

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

        Uses the configured auth_audience for token scope.
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
        audience = self.auth_audience or "https://cognitiveservices.azure.com/.default"
        if self.auth_mode == "managed_identity":
            try:
                from azure.identity import DefaultAzureCredential  # noqa: PLC0415
                cred = DefaultAzureCredential()
                token = cred.get_token(audience)
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
        The resource-level base is:
          https://<resource>.services.ai.azure.com
        """
        from urllib.parse import urlparse  # noqa: PLC0415

        parsed = urlparse(endpoint.rstrip("/"))
        # Strip /api/projects/<name> suffix if present
        path = parsed.path
        idx = path.find("/api/projects")
        if idx >= 0:
            path = path[:idx]
        return f"{parsed.scheme}://{parsed.netloc}{path}"

    def _build_test_url(self):
        """Build the correct test URL based on endpoint shape.

        For Foundry project endpoints (/api/projects/<project>):
          Test the project endpoint directly with a GET.
        For resource-level endpoints (.services.ai.azure.com):
          Test the resource root with a GET.
        For Azure OpenAI endpoints (.openai.azure.com):
          Test /openai/models.
        For Document Intelligence (.cognitiveservices.azure.com):
          Test /info.
        """
        endpoint = self.endpoint.rstrip("/")
        if "/api/projects/" in endpoint:
            # Foundry project endpoint -- test the project root directly
            return endpoint
        if ".services.ai.azure.com" in endpoint:
            # Foundry resource-level -- test root
            return endpoint
        if ".openai.azure.com" in endpoint:
            # Azure OpenAI -- test models listing
            version = self.api_version or "2024-12-01-preview"
            return "%s/openai/models?api-version=%s" % (endpoint, version)
        if ".cognitiveservices.azure.com" in endpoint:
            # Document Intelligence -- test info endpoint
            return "%s/info" % endpoint
        # Fallback: test the endpoint as-is
        return endpoint

    def action_test_connection(self):
        """Test connectivity to the configured endpoint.

        Probes the correct URL based on the endpoint family:
          - Foundry project: GET the project endpoint directly
          - Azure OpenAI: GET /openai/models
          - Document Intelligence: GET /info
          - Other: GET the endpoint root
        """
        self.ensure_one()
        import requests  # noqa: PLC0415

        headers, missing = self._resolve_auth_headers()
        test_url = self._build_test_url()

        try:
            resp = requests.get(
                test_url,
                headers=headers,
                timeout=10,
            )
            if resp.status_code < 400:
                result = _("OK — HTTP %s (auth_mode=%s, audience=%s)") % (
                    resp.status_code,
                    self.auth_mode,
                    self.auth_audience or "default",
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
