# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ipai_copilot_api_url = fields.Char(
        string="Copilot API URL",
        config_parameter="ipai_copilot.api_url",
        help="URL of the Supabase Edge Function (e.g. http://localhost:54321/functions/v1/ipai-copilot)",
        default="http://localhost:54321/functions/v1/ipai-copilot",
    )
    ipai_copilot_api_key = fields.Char(
        string="Copilot API Key",
        config_parameter="ipai_copilot.api_key",
        help="API Key for the Copilot service (optional for local/stub)",
    )
