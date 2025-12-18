# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ipai_enable_finance_project_analytics = fields.Boolean(
        string="Enable IPAI Finance Project Analytics",
        config_parameter="ipai_finance_project_hybrid.enable_finance_analytics",
        default=True,
    )
