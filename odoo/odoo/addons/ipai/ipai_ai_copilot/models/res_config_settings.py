# © 2026 InsightPulse AI — License LGPL-3.0-or-later
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ipai_copilot_bridge_url = fields.Char(
        string="Copilot Bridge URL",
        help="Full URL of the copilot AI bridge endpoint (Supabase Edge Function). "
             "If empty, falls back to the widget bridge URL, then Azure, then provider-direct.",
        config_parameter="ipai_ai_copilot.bridge_url",
    )
    ipai_copilot_bridge_token = fields.Char(
        string="Copilot Bridge Token",
        help="Optional bearer token for server-to-server auth to the copilot bridge.",
        config_parameter="ipai_ai_copilot.bridge_token",
    )
