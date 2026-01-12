# Part of IPAI. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    """Settings for custom theme colors."""

    _inherit = "res.config.settings"

    # Primary Colors
    theme_color_primary = fields.Char(
        string="Primary Color",
        related="company_id.theme_color_primary",
        readonly=False,
        help="Main brand color (e.g., #3B82F6)",
    )
    theme_color_primary_hover = fields.Char(
        string="Primary Hover",
        related="company_id.theme_color_primary_hover",
        readonly=False,
        help="Primary color on hover state",
    )
    theme_color_accent = fields.Char(
        string="Accent Color",
        related="company_id.theme_color_accent",
        readonly=False,
        help="Secondary brand color for highlights",
    )
    theme_color_accent_hover = fields.Char(
        string="Accent Hover",
        related="company_id.theme_color_accent_hover",
        readonly=False,
        help="Accent color on hover state",
    )

    # Semantic Colors
    theme_color_success = fields.Char(
        string="Success Color",
        related="company_id.theme_color_success",
        readonly=False,
        help="Color for success states (e.g., #10B981)",
    )
    theme_color_warning = fields.Char(
        string="Warning Color",
        related="company_id.theme_color_warning",
        readonly=False,
        help="Color for warning states (e.g., #F59E0B)",
    )
    theme_color_danger = fields.Char(
        string="Danger Color",
        related="company_id.theme_color_danger",
        readonly=False,
        help="Color for error/danger states (e.g., #EF4444)",
    )
    theme_color_info = fields.Char(
        string="Info Color",
        related="company_id.theme_color_info",
        readonly=False,
        help="Color for informational states (e.g., #3B82F6)",
    )

    # Surface Colors
    theme_color_bg = fields.Char(
        string="Background Color",
        related="company_id.theme_color_bg",
        readonly=False,
        help="Main background color",
    )
    theme_color_surface = fields.Char(
        string="Surface Color",
        related="company_id.theme_color_surface",
        readonly=False,
        help="Card/panel surface color",
    )
    theme_color_surface_elevated = fields.Char(
        string="Elevated Surface",
        related="company_id.theme_color_surface_elevated",
        readonly=False,
        help="Elevated elements (modals, dropdowns)",
    )
    theme_color_border = fields.Char(
        string="Border Color",
        related="company_id.theme_color_border",
        readonly=False,
        help="Default border color",
    )

    # Text Colors
    theme_color_text_primary = fields.Char(
        string="Primary Text",
        related="company_id.theme_color_text_primary",
        readonly=False,
        help="Main text color",
    )
    theme_color_text_secondary = fields.Char(
        string="Secondary Text",
        related="company_id.theme_color_text_secondary",
        readonly=False,
        help="Muted/secondary text color",
    )
    theme_color_text_on_primary = fields.Char(
        string="Text on Primary",
        related="company_id.theme_color_text_on_primary",
        readonly=False,
        help="Text color on primary background",
    )
    theme_color_text_on_accent = fields.Char(
        string="Text on Accent",
        related="company_id.theme_color_text_on_accent",
        readonly=False,
        help="Text color on accent background",
    )

    # Shape
    theme_radius_sm = fields.Char(
        string="Small Radius",
        related="company_id.theme_radius_sm",
        readonly=False,
        help="Small border radius (e.g., 4px)",
    )
    theme_radius_md = fields.Char(
        string="Medium Radius",
        related="company_id.theme_radius_md",
        readonly=False,
        help="Medium border radius (e.g., 8px)",
    )
    theme_radius_lg = fields.Char(
        string="Large Radius",
        related="company_id.theme_radius_lg",
        readonly=False,
        help="Large border radius (e.g., 12px)",
    )

    # Dark Mode
    theme_dark_mode_enabled = fields.Boolean(
        string="Enable Dark Mode",
        related="company_id.theme_dark_mode_enabled",
        readonly=False,
        help="Enable dark mode support",
    )

    @api.model
    def get_theme_css_variables(self):
        """Generate CSS variables from theme settings."""
        company = self.env.company
        variables = []

        # Map field names to CSS variable names
        color_map = {
            "theme_color_primary": "--ipai-color-primary",
            "theme_color_primary_hover": "--ipai-color-primary-hover",
            "theme_color_accent": "--ipai-color-accent",
            "theme_color_accent_hover": "--ipai-color-accent-hover",
            "theme_color_success": "--ipai-color-success",
            "theme_color_warning": "--ipai-color-warning",
            "theme_color_danger": "--ipai-color-danger",
            "theme_color_info": "--ipai-color-info",
            "theme_color_bg": "--ipai-color-bg",
            "theme_color_surface": "--ipai-color-surface",
            "theme_color_surface_elevated": "--ipai-color-surface-elevated",
            "theme_color_border": "--ipai-color-border",
            "theme_color_text_primary": "--ipai-color-text-primary",
            "theme_color_text_secondary": "--ipai-color-text-secondary",
            "theme_color_text_on_primary": "--ipai-color-text-on-primary",
            "theme_color_text_on_accent": "--ipai-color-text-on-accent",
            "theme_radius_sm": "--ipai-radius-sm",
            "theme_radius_md": "--ipai-radius-md",
            "theme_radius_lg": "--ipai-radius-lg",
        }

        for field_name, css_var in color_map.items():
            value = getattr(company, field_name, None)
            if value:
                variables.append(f"  {css_var}: {value};")

        if variables:
            return ":root {\n" + "\n".join(variables) + "\n}"
        return ""
