# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ipai_kapa_base_url = fields.Char(
        string="Kapa Base URL",
        config_parameter="ipai.kapa.base_url",
        help="Base URL for the Kapa API (default: https://api.kapa.ai)",
    )
    ipai_kapa_api_key = fields.Char(
        string="Kapa API Key",
        config_parameter="ipai.kapa.api_key",
        help="API key for authentication with the Kapa service.",
    )
    ipai_kapa_project_id = fields.Char(
        string="Kapa Project ID",
        config_parameter="ipai.kapa.project_id",
        help="Project ID for the Kapa service.",
    )
