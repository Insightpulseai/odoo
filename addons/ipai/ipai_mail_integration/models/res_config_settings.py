# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Add mail integration settings."""

    _inherit = "res.config.settings"

    ipai_mail_gateway_id = fields.Many2one(
        "ipai.mail.gateway",
        string="Default Mail Gateway",
        config_parameter="ipai_mail.default_gateway_id",
    )
    ipai_mail_track_opens = fields.Boolean(
        string="Track Email Opens",
        config_parameter="ipai_mail.track_opens",
        default=True,
    )
    ipai_mail_track_clicks = fields.Boolean(
        string="Track Email Clicks",
        config_parameter="ipai_mail.track_clicks",
        default=True,
    )
