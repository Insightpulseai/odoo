# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # ChatGPT configuration
    ai_use_chatgpt = fields.Boolean(
        string="Use your own ChatGPT account",
        config_parameter="ipai_ask_ai.chatgpt_enabled",
        default=False,
        help="Enable ChatGPT integration with your own OpenAI API key",
    )
    ai_chatgpt_key = fields.Char(
        string="ChatGPT API Key",
        config_parameter="ipai_ask_ai.chatgpt_key",
        groups="base.group_system",
        help="Your OpenAI API key (starts with sk-)",
    )

    # Google Gemini configuration (direct)
    ai_use_gemini = fields.Boolean(
        string="Use your own Google Gemini account",
        config_parameter="ipai_ask_ai.gemini_enabled",
        default=False,
        help="Enable Google Gemini integration with your own API key",
    )
    ai_gemini_key = fields.Char(
        string="Google Gemini API Key",
        config_parameter="ipai_ask_ai.gemini_key",
        groups="base.group_system",
        help="Your Google Gemini API key (starts with AIza)",
    )

    # IPAI Copilot (Supabase Edge Function) configuration
    ipai_copilot_api_url = fields.Char(
        string="Copilot API URL",
        config_parameter="ipai_copilot.api_url",
        help="URL of the Supabase Edge Function (e.g. http://localhost:54321/functions/v1/ipai-copilot)",
        default="http://localhost:54321/functions/v1/ipai-copilot",
    )
    ipai_copilot_api_key = fields.Char(
        string="Copilot API Key",
        config_parameter="ipai_copilot.api_key",
        groups="base.group_system",
        help="API key for the Copilot service (optional for local/stub).",
    )

    # Optional: Gemini via IPAI service (separate from direct Gemini above)
    ipai_gemini_api_key = fields.Char(
        string="Gemini API Key (IPAI Service)",
        config_parameter="ipai_gemini.api_key",
        groups="base.group_system",
        help="API Key for Gemini (can also be set via GEMINI_API_KEY env var)",
    )
    ipai_gemini_model = fields.Char(
        string="Gemini Model",
        config_parameter="ipai_gemini.model",
        default="gemini-2.5-flash",
        help="Model name (e.g. gemini-pro, gemini-1.5-flash, gemini-2.5-flash)",
    )
