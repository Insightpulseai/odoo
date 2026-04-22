# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ipai_pulser_chat_enabled = fields.Boolean(
        string="Pulser Chat Enabled",
        config_parameter="ipai.pulser_chat.enabled",
        help="Show the Pulser chat shell in the Odoo systray.",
    )
    ipai_pulser_chat_backend_url = fields.Char(
        string="Pulser Chat Backend URL",
        config_parameter="ipai.pulser_chat.backend_url",
        help="External Pulser chat endpoint URL used by the thin Odoo shell.",
    )
    ipai_pulser_chat_timeout_seconds = fields.Integer(
        string="Pulser Chat Timeout (seconds)",
        config_parameter="ipai.pulser_chat.timeout_seconds",
        default=30,
        help="Timeout for the Odoo-to-Pulser proxy request.",
    )
