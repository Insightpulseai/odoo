# Part of IPAI. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    """Extend company with custom theme color fields."""

    _inherit = "res.company"

    # Primary Colors - no defaults, fully customizable
    theme_color_primary = fields.Char(
        string="Primary Color",
        help="Main brand color (hex format, e.g., #3B82F6)",
    )
    theme_color_primary_hover = fields.Char(
        string="Primary Hover",
        help="Primary color on hover state",
    )
    theme_color_accent = fields.Char(
        string="Accent Color",
        help="Secondary brand color for highlights",
    )
    theme_color_accent_hover = fields.Char(
        string="Accent Hover",
        help="Accent color on hover state",
    )

    # Semantic Colors - no defaults
    theme_color_success = fields.Char(
        string="Success Color",
        help="Color for success states",
    )
    theme_color_warning = fields.Char(
        string="Warning Color",
        help="Color for warning states",
    )
    theme_color_danger = fields.Char(
        string="Danger Color",
        help="Color for error/danger states",
    )
    theme_color_info = fields.Char(
        string="Info Color",
        help="Color for informational states",
    )

    # Surface Colors - no defaults
    theme_color_bg = fields.Char(
        string="Background Color",
        help="Main background color",
    )
    theme_color_surface = fields.Char(
        string="Surface Color",
        help="Card/panel surface color",
    )
    theme_color_surface_elevated = fields.Char(
        string="Elevated Surface",
        help="Elevated elements (modals, dropdowns)",
    )
    theme_color_border = fields.Char(
        string="Border Color",
        help="Default border color",
    )

    # Text Colors - no defaults
    theme_color_text_primary = fields.Char(
        string="Primary Text",
        help="Main text color",
    )
    theme_color_text_secondary = fields.Char(
        string="Secondary Text",
        help="Muted/secondary text color",
    )
    theme_color_text_on_primary = fields.Char(
        string="Text on Primary",
        help="Text color on primary background",
    )
    theme_color_text_on_accent = fields.Char(
        string="Text on Accent",
        help="Text color on accent background",
    )

    # Shape - no defaults
    theme_radius_sm = fields.Char(
        string="Small Radius",
        help="Small border radius (e.g., 4px)",
    )
    theme_radius_md = fields.Char(
        string="Medium Radius",
        help="Medium border radius (e.g., 8px)",
    )
    theme_radius_lg = fields.Char(
        string="Large Radius",
        help="Large border radius (e.g., 12px)",
    )

    # Dark Mode
    theme_dark_mode_enabled = fields.Boolean(
        string="Enable Dark Mode",
        default=False,
        help="Enable dark mode support",
    )
