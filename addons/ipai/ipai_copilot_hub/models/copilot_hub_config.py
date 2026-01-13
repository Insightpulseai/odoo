# -*- coding: utf-8 -*-
"""
Copilot Hub Configuration Model

Provides a transient model for hub settings and a mixin for
retrieving the hub URL from system parameters.
"""
from odoo import api, fields, models


class CopilotHubSettings(models.TransientModel):
    """Settings wizard for Copilot Hub configuration."""

    _name = "copilot.hub.settings"
    _description = "Copilot Hub Settings"
    _inherit = "res.config.settings"

    hub_url = fields.Char(
        string="Hub URL",
        config_parameter="ipai.copilot.hub_url",
        default="https://ops.insightpulseai.net",
        help="URL of the external Fluent UI Ops Control Room application",
    )

    hub_embed_mode = fields.Selection(
        [
            ("iframe", "Iframe (default)"),
            ("popup", "Popup Window"),
            ("redirect", "Full Redirect"),
        ],
        string="Embed Mode",
        config_parameter="ipai.copilot.hub_embed_mode",
        default="iframe",
        help="How to display the external hub application",
    )

    hub_show_toolbar = fields.Boolean(
        string="Show Toolbar",
        config_parameter="ipai.copilot.hub_show_toolbar",
        default=True,
        help="Display Odoo toolbar above the embedded hub",
    )


class CopilotHubMixin(models.AbstractModel):
    """Mixin to provide hub URL retrieval functionality."""

    _name = "copilot.hub.mixin"
    _description = "Copilot Hub Mixin"

    @api.model
    def get_hub_url(self):
        """Get the configured hub URL from system parameters."""
        ICP = self.env["ir.config_parameter"].sudo()
        return ICP.get_param(
            "ipai.copilot.hub_url",
            default="https://ops.insightpulseai.net",
        )

    @api.model
    def get_hub_config(self):
        """Get full hub configuration."""
        ICP = self.env["ir.config_parameter"].sudo()
        return {
            "url": ICP.get_param(
                "ipai.copilot.hub_url",
                default="https://ops.insightpulseai.net",
            ),
            "embed_mode": ICP.get_param(
                "ipai.copilot.hub_embed_mode",
                default="iframe",
            ),
            "show_toolbar": ICP.get_param(
                "ipai.copilot.hub_show_toolbar",
                default="True",
            ) == "True",
        }
