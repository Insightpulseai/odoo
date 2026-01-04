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
    ipai_gemini_api_key = fields.Char(
        string='Google Gemini API Key',
        config_parameter='ipai_ask_ai.gemini_api_key',
        help='API Key for Google Gemini AI service (used for generic queries)'
    )
    ipai_gemini_model = fields.Char(
        string='Gemini Model',
        config_parameter='ipai_ask_ai.gemini_model',
        help='Gemini model to use (e.g., gemini-2.5-flash, gemini-3.0-flash)',
        default='gemini-2.5-flash'
    )
