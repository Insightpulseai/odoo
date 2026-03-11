# (c) 2026 InsightPulse AI — License LGPL-3.0-or-later
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ipai_ask_ai_azure_endpoint = fields.Char(
        string="Azure OpenAI Endpoint",
        config_parameter="ipai_ask_ai_azure.endpoint",
    )
    ipai_ask_ai_azure_api_key = fields.Char(
        string="Azure OpenAI API Key",
        config_parameter="ipai_ask_ai_azure.api_key",
    )
    ipai_ask_ai_azure_model = fields.Char(
        string="Azure OpenAI Model/Deployment",
        config_parameter="ipai_ask_ai_azure.model",
    )
    ipai_ask_ai_azure_api_version = fields.Char(
        string="Azure OpenAI API Version",
        config_parameter="ipai_ask_ai_azure.api_version",
        default="preview",
    )
