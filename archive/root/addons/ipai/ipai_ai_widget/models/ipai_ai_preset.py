# © 2026 InsightPulse AI — License LGPL-3.0-or-later
"""
ipai.ai.preset — Preset action definitions (Summarize, Improve, Translate, Draft).
"""
from odoo import fields, models

_OUTPUT_MODES = [
    ("insert", "Insert"),
    ("replace", "Replace"),
    ("preview", "Preview"),
]


class IpaiAiPreset(models.Model):
    _name = "ipai.ai.preset"
    _description = "AI Preset Action"
    _order = "sequence, id"

    key = fields.Char(string="Key", required=True)
    label = fields.Char(string="Label", required=True)
    icon = fields.Char(string="Icon", help="Font Awesome icon class")
    prompt_template = fields.Text(string="Prompt Template", required=True)
    requires_selection = fields.Boolean(string="Requires Selection", default=False)
    output_mode = fields.Selection(
        _OUTPUT_MODES,
        string="Output Mode",
        default="preview",
    )
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("key_unique", "UNIQUE(key)", "Preset key must be unique"),
    ]
