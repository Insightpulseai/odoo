# © 2026 InsightPulse AI — License LGPL-3.0-or-later
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ipai_ai_bridge_url = fields.Char(
        string="AI Bridge URL",
        help="Full URL of the IPAI AI provider bridge endpoint. "
             "Example: https://ops.insightpulseai.com/api/ai/gemini\n"
             "Leave empty to disable the Ask AI widget.",
        config_parameter="ipai_ai_widget.bridge_url",
    )
