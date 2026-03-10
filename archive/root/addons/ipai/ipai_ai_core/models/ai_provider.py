# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiAiProvider(models.Model):
    _name = "ipai.ai.provider"
    _description = "AI Provider"
    _order = "is_default desc, name"

    name = fields.Char(required=True)
    provider_type = fields.Selection(
        [
            ("openai", "OpenAI"),
            ("anthropic", "Anthropic"),
            ("google", "Google"),
            ("ollama", "Ollama"),
            ("supabase_edge", "Supabase Edge"),
        ],
        required=True,
        default="openai",
    )
    api_key_param = fields.Char(
        string="API Key Parameter",
        help="ir.config_parameter key that stores the API key for this provider",
    )
    base_url = fields.Char(string="Base URL")
    model_name = fields.Char(string="Model Name")
    max_tokens = fields.Integer(default=4096)
    temperature = fields.Float(default=0.7)
    is_default = fields.Boolean(default=False)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    # Stats (readonly)
    total_requests = fields.Integer(readonly=True, default=0)
    avg_latency_ms = fields.Float(
        string="Avg Latency (ms)", readonly=True, default=0.0
    )
    total_tokens = fields.Integer(readonly=True, default=0)

    def update_stats(self, latency_ms, tokens):
        """Update provider usage statistics with a running average for latency.

        Args:
            latency_ms: Latency of the most recent request in milliseconds.
            tokens: Number of tokens consumed by the most recent request.
        """
        for rec in self:
            new_total = rec.total_requests + 1
            # Running average: ((old_avg * old_count) + new_value) / new_count
            new_avg = (
                (rec.avg_latency_ms * rec.total_requests) + latency_ms
            ) / new_total
            rec.write(
                {
                    "total_requests": new_total,
                    "avg_latency_ms": new_avg,
                    "total_tokens": rec.total_tokens + tokens,
                }
            )

    @api.onchange("is_default")
    def _onchange_is_default(self):
        """Warn user that setting default will unset others in same company."""
        if self.is_default:
            return {
                "warning": {
                    "title": "Default Provider",
                    "message": (
                        "Setting this provider as default will unset any other "
                        "default provider for the same company on save."
                    ),
                }
            }

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.is_default:
                self._unset_other_defaults(rec)
        return records

    def write(self, vals):
        res = super().write(vals)
        if vals.get("is_default"):
            for rec in self:
                self._unset_other_defaults(rec)
        return res

    def _unset_other_defaults(self, record):
        """Ensure only one default provider per company."""
        domain = [
            ("is_default", "=", True),
            ("id", "!=", record.id),
        ]
        if record.company_id:
            domain.append(("company_id", "=", record.company_id.id))
        else:
            domain.append(("company_id", "=", False))
        others = self.sudo().search(domain)
        if others:
            others.write({"is_default": False})
