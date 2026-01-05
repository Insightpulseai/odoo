# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ChatGPT configuration
    ai_use_chatgpt = fields.Boolean(
        'Use your own ChatGPT account',
        config_parameter='ipai_ask_ai.chatgpt_enabled',
        default=False,
        help='Enable ChatGPT integration with your own OpenAI API key'
    )
    ai_chatgpt_key = fields.Char(
        'ChatGPT API Key',
        config_parameter='ipai_ask_ai.chatgpt_key',
        groups='base.group_system',
        help='Your OpenAI API key (starts with sk-)'
    )

    # Google Gemini configuration
    ai_use_gemini = fields.Boolean(
        'Use your own Google Gemini account',
        config_parameter='ipai_ask_ai.gemini_enabled',
        default=False,
        help='Enable Google Gemini integration with your own API key'
    )
    ai_gemini_key = fields.Char(
        'Google Gemini API Key',
        config_parameter='ipai_ask_ai.gemini_key',
        groups='base.group_system',
        help='Your Google Gemini API key (starts with AIza)'
    )
