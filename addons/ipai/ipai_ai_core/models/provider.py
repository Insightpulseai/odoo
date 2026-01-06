# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiAiProvider(models.Model):
    _name = "ipai.ai.provider"
    _description = "IPAI AI Provider"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    provider_type = fields.Selection(
        [
            ("kapa", "Kapa-style RAG"),
            ("openai", "OpenAI"),
            ("anthropic", "Anthropic Claude"),
            ("ollama", "Ollama (Local)"),
        ],
        required=True,
        default="kapa",
    )

    active = fields.Boolean(default=True)

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    is_default = fields.Boolean(default=False)

    # Statistics
    total_requests = fields.Integer(readonly=True, default=0)
    total_tokens = fields.Integer(readonly=True, default=0)
    avg_latency_ms = fields.Float(readonly=True, default=0.0)

    @api.constrains("is_default", "company_id")
    def _check_single_default(self):
        for rec in self:
            if rec.is_default:
                others = self.search(
                    [
                        ("id", "!=", rec.id),
                        ("company_id", "=", rec.company_id.id),
                        ("is_default", "=", True),
                    ],
                    limit=1,
                )
                if others:
                    others.is_default = False

    @api.model
    def get_default(self, company_id=None):
        """Get the default active provider for a company."""
        company = (
            self.env["res.company"].browse(company_id)
            if company_id
            else self.env.company
        )
        rec = self.search(
            [
                ("company_id", "=", company.id),
                ("is_default", "=", True),
                ("active", "=", True),
            ],
            limit=1,
        )
        if rec:
            return rec
        return self.search(
            [("company_id", "=", company.id), ("active", "=", True)],
            limit=1,
        )

    def update_stats(self, latency_ms, tokens=0):
        """Update provider statistics after a request."""
        for rec in self:
            total = rec.total_requests + 1
            avg = (rec.avg_latency_ms * rec.total_requests + latency_ms) / total
            rec.write(
                {
                    "total_requests": total,
                    "total_tokens": rec.total_tokens + tokens,
                    "avg_latency_ms": avg,
                }
            )
