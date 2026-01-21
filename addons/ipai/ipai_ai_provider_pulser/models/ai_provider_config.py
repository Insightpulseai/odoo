# -*- coding: utf-8 -*-
"""
IPAI AI Provider Configuration Model.

Stores provider-specific configurations in database.
"""
from odoo import api, fields, models


class IpaiAiProviderConfig(models.Model):
    """Configuration for AI providers."""

    _name = "ipai.ai.provider.config"
    _description = "AI Provider Configuration"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Provider type
    provider_type = fields.Selection(
        [
            ("openai", "OpenAI"),
            ("anthropic", "Anthropic"),
            ("azure", "Azure OpenAI"),
            ("pulser", "Pulser Gateway"),
            ("custom", "Custom Endpoint"),
        ],
        required=True,
        default="openai",
    )

    # Connection settings
    endpoint = fields.Char(string="API Endpoint")
    api_key = fields.Char(string="API Key")
    organization_id = fields.Char(string="Organization ID")

    # Model settings
    default_model = fields.Char(default="gpt-4")
    available_models = fields.Text(
        help="One model per line",
        default="gpt-4\ngpt-4-turbo\ngpt-3.5-turbo",
    )

    # Rate limiting
    rate_limit_rpm = fields.Integer(
        string="Rate Limit (requests/min)",
        default=60,
    )
    rate_limit_tpm = fields.Integer(
        string="Rate Limit (tokens/min)",
        default=90000,
    )

    # Defaults
    default_temperature = fields.Float(default=0.7)
    default_max_tokens = fields.Integer(default=1000)

    # Fallback
    fallback_provider_id = fields.Many2one(
        "ipai.ai.provider.config",
        string="Fallback Provider",
        help="Provider to use if this one fails",
    )

    # Usage tracking
    total_requests = fields.Integer(readonly=True)
    total_tokens = fields.Integer(readonly=True)
    last_used = fields.Datetime(readonly=True)

    _sql_constraints = [
        ("code_unique", "unique(code)", "Provider code must be unique."),
    ]

    def get_models_list(self):
        """Return list of available models."""
        self.ensure_one()
        if not self.available_models:
            return []
        return [m.strip() for m in self.available_models.split("\n") if m.strip()]

    def update_usage(self, tokens=0):
        """Update usage statistics."""
        self.write(
            {
                "total_requests": self.total_requests + 1,
                "total_tokens": self.total_tokens + tokens,
                "last_used": fields.Datetime.now(),
            }
        )

    @api.model
    def get_default_provider(self):
        """Get the default active provider configuration."""
        return self.search([("active", "=", True)], order="sequence", limit=1)

    @api.model
    def sync_from_params(self):
        """
        Sync provider configurations from system parameters.

        This allows backward compatibility with existing ir.config_parameter settings.
        """
        ICP = self.env["ir.config_parameter"].sudo()

        providers = ["openai", "anthropic", "azure", "pulser"]
        for provider in providers:
            api_key = ICP.get_param(f"ipai_ai.{provider}_api_key", "")
            endpoint = ICP.get_param(f"ipai_ai.{provider}_endpoint", "")

            if api_key or endpoint:
                existing = self.search([("code", "=", provider)], limit=1)
                vals = {
                    "name": provider.title(),
                    "code": provider,
                    "provider_type": provider,
                    "api_key": api_key,
                    "endpoint": endpoint,
                }
                if existing:
                    existing.write(vals)
                else:
                    self.create(vals)
