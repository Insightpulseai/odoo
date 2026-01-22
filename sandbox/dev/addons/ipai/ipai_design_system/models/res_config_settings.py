# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ipai_active_theme = fields.Selection(
        [
            ("fluent2", "Fluent 2"),
            ("tbwa", "TBWA Corporate"),
            ("tbwa_backend", "TBWA Backend"),
            ("copilot", "Copilot Interface"),
            ("aiux", "AI/UX Hybrid"),
        ],
        string="Active Theme",
        default="fluent2",
        config_parameter="ipai_design_system.active_theme",
    )

    ipai_enable_chatgpt_sdk = fields.Boolean(
        string="Enable ChatGPT SDK Theme",
        config_parameter="ipai_design_system.chatgpt_sdk",
        default=False,
    )

    ipai_fluent_icons_enabled = fields.Boolean(
        string="Fluent Icon Set",
        config_parameter="ipai_design_system.fluent_icons",
        default=True,
    )
