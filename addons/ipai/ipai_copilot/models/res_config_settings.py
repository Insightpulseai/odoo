from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ipai_copilot_api_url = fields.Char(config_parameter="ipai.copilot.api_url")
    ipai_copilot_api_key = fields.Char(config_parameter="ipai.copilot.api_key")
