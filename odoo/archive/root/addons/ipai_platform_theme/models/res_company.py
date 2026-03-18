# Part of IPAI. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    """Extend company with theme variant selection."""

    _inherit = "res.company"

    ipai_theme_variant = fields.Selection(
        [
            ("tbwa", "TBWA (Yellow + Black)"),
            ("neutral", "Neutral (Gray)"),
            ("dark", "Dark Mode"),
        ],
        string="Theme Variant",
        default="tbwa",
        help="Select the visual theme for the IPAI platform",
    )
