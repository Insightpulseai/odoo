# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Settings panel for Google Workspace Add-on configuration."""

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    gws_enabled = fields.Boolean(
        string="Google Workspace Add-ons",
        config_parameter="ipai_gws.enabled",
    )
    gws_project_number = fields.Char(
        string="Google Cloud Project Number",
        config_parameter="ipai_gws.project_number",
        help="Google Cloud project number used for ID token audience validation.",
    )
