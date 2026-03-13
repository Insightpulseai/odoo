# Part of IPAI. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Settings for IPAI Platform Theme."""

    _inherit = "res.config.settings"

    ipai_theme_variant = fields.Selection(
        related="company_id.ipai_theme_variant",
        readonly=False,
        string="Theme Variant",
    )
