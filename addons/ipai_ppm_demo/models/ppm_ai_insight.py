# ipai_ppm_demo/models/ppm_ai_insight.py
from odoo import fields, models


class PpmAiInsight(models.Model):
    _name = "ppm.ai.insight"
    _description = "PPM AI Insight Sample"

    name = fields.Char(required=True)
    prompt = fields.Text()
    insight_summary = fields.Text()
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium",
    )
