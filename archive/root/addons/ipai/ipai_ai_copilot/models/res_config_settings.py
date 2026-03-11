# © 2026 InsightPulse AI — License LGPL-3.0-or-later
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # ── Copilot bridge (legacy Supabase Edge Function path) ──────────────
    ipai_copilot_bridge_url = fields.Char(
        string="Copilot Bridge URL",
        help="Full URL of the copilot AI bridge endpoint (Supabase Edge Function). "
             "If empty, falls back to Azure OpenAI direct, then provider-direct.",
        config_parameter="ipai_ai_copilot.bridge_url",
    )
    ipai_copilot_bridge_token = fields.Char(
        string="Copilot Bridge Token",
        help="Optional bearer token for server-to-server auth to the copilot bridge.",
        config_parameter="ipai_ai_copilot.bridge_token",
    )

    # ── Azure OpenAI configuration ──────────────────────────────────────
    ipai_azure_openai_base_url = fields.Char(
        string="Azure OpenAI Base URL",
        help="Azure OpenAI endpoint URL (e.g. https://your-resource.openai.azure.com). "
             "Seeded from AZURE_OPENAI_BASE_URL env var at module install.",
        config_parameter="ipai_ask_ai_azure.base_url",
    )
    ipai_azure_openai_api_key = fields.Char(
        string="Azure OpenAI API Key",
        help="Azure OpenAI API key. Seeded from AZURE_OPENAI_API_KEY env var at module install.",
        config_parameter="ipai_ask_ai_azure.api_key",
    )
    ipai_azure_openai_deployment = fields.Char(
        string="Azure OpenAI Deployment",
        help="Azure deployment name (NOT the base model name). "
             "Seeded from AZURE_OPENAI_DEPLOYMENT env var at module install.",
        config_parameter="ipai_ask_ai_azure.model",
    )
    ipai_azure_openai_api_mode = fields.Selection(
        [
            ("responses", "Responses API (default)"),
            ("chat_completions", "Chat Completions API"),
        ],
        string="Azure API Mode",
        help="Which Azure OpenAI API to use. "
             "'responses' uses /openai/v1/responses, "
             "'chat_completions' uses /openai/v1/chat/completions.",
        config_parameter="ipai_ask_ai_azure.api_mode",
        default="responses",
    )

    @api.constrains(
        "ipai_azure_openai_base_url",
        "ipai_azure_openai_api_key",
        "ipai_azure_openai_deployment",
    )
    def _check_azure_deployment_name(self):
        """Validate that deployment name is non-empty when Azure is configured."""
        for rec in self:
            has_url = bool(rec.ipai_azure_openai_base_url)
            has_key = bool(rec.ipai_azure_openai_api_key)
            has_deployment = bool(rec.ipai_azure_openai_deployment)
            # If any Azure field is set, deployment must also be set
            if (has_url or has_key) and not has_deployment:
                raise ValidationError(
                    "Azure OpenAI Deployment name is required when Base URL "
                    "or API Key is configured. The deployment name must match "
                    "your Azure resource — do not use the base model family name."
                )
