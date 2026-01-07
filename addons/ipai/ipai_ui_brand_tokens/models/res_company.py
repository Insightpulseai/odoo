# -*- coding: utf-8 -*-
"""
Brand Token Fields for res.company
==================================

Extends res.company with brand token fields that serve as the single
source of truth for both Odoo CSS variables and React JSON API.
"""
from odoo import models, fields, api
import json


class ResCompany(models.Model):
    _inherit = "res.company"

    # =========================================================================
    # BRAND COLOR PALETTE
    # =========================================================================
    brand_primary = fields.Char(
        string="Primary Color",
        default="#000000",  # TBWA Black
        help="Primary brand color (buttons, links, accents). Default: TBWA Black",
    )
    brand_primary_hover = fields.Char(
        string="Primary Hover",
        default="#1A1A1A",
        help="Primary color on hover state",
    )
    brand_accent = fields.Char(
        string="Accent Color",
        default="#FBBF24",  # TBWA Yellow
        help="Accent/highlight color. Default: TBWA Yellow",
    )
    brand_accent_hover = fields.Char(
        string="Accent Hover",
        default="#F59E0B",
        help="Accent color on hover state",
    )

    # =========================================================================
    # SURFACE COLORS
    # =========================================================================
    brand_bg = fields.Char(
        string="Background",
        default="#FFFFFF",
        help="Main background color",
    )
    brand_surface = fields.Char(
        string="Surface",
        default="#F9FAFB",
        help="Card/panel surface color",
    )
    brand_surface_elevated = fields.Char(
        string="Elevated Surface",
        default="#FFFFFF",
        help="Elevated elements (modals, dropdowns)",
    )
    brand_border = fields.Char(
        string="Border Color",
        default="#E5E7EB",
        help="Default border color",
    )

    # =========================================================================
    # TEXT COLORS
    # =========================================================================
    brand_text_primary = fields.Char(
        string="Text Primary",
        default="#111827",
        help="Primary text color",
    )
    brand_text_secondary = fields.Char(
        string="Text Secondary",
        default="#6B7280",
        help="Secondary/muted text color",
    )
    brand_text_on_primary = fields.Char(
        string="Text on Primary",
        default="#FFFFFF",
        help="Text color on primary background",
    )
    brand_text_on_accent = fields.Char(
        string="Text on Accent",
        default="#000000",
        help="Text color on accent background",
    )

    # =========================================================================
    # SEMANTIC COLORS
    # =========================================================================
    brand_success = fields.Char(
        string="Success Color",
        default="#10B981",
        help="Success/positive state color",
    )
    brand_warning = fields.Char(
        string="Warning Color",
        default="#F59E0B",
        help="Warning state color",
    )
    brand_danger = fields.Char(
        string="Danger Color",
        default="#EF4444",
        help="Danger/error state color",
    )
    brand_info = fields.Char(
        string="Info Color",
        default="#3B82F6",
        help="Information state color",
    )

    # =========================================================================
    # SHAPE & TYPOGRAPHY
    # =========================================================================
    brand_radius_sm = fields.Char(
        string="Radius Small",
        default="4px",
        help="Small border radius",
    )
    brand_radius_md = fields.Char(
        string="Radius Medium",
        default="8px",
        help="Medium border radius",
    )
    brand_radius_lg = fields.Char(
        string="Radius Large",
        default="12px",
        help="Large border radius",
    )
    brand_font_family = fields.Char(
        string="Font Family",
        default='"Segoe UI", system-ui, -apple-system, sans-serif',
        help="Primary font family",
    )

    # =========================================================================
    # SHADOWS
    # =========================================================================
    brand_shadow_sm = fields.Char(
        string="Shadow Small",
        default="0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        help="Small shadow",
    )
    brand_shadow_md = fields.Char(
        string="Shadow Medium",
        default="0 4px 6px -1px rgba(0, 0, 0, 0.1)",
        help="Medium shadow",
    )
    brand_shadow_lg = fields.Char(
        string="Shadow Large",
        default="0 10px 15px -3px rgba(0, 0, 0, 0.1)",
        help="Large shadow",
    )

    # =========================================================================
    # BRANDING ASSETS
    # =========================================================================
    brand_logo_svg = fields.Binary(
        string="Logo (SVG)",
        help="Company logo in SVG format for crisp rendering",
    )
    brand_logo_svg_filename = fields.Char(
        string="Logo Filename",
    )
    brand_icon_pack = fields.Selection(
        selection=[
            ("fluent", "Microsoft Fluent"),
            ("material", "Material Design"),
            ("heroicons", "Heroicons"),
            ("lucide", "Lucide"),
        ],
        string="Icon Pack",
        default="fluent",
        help="Icon style to use throughout the UI",
    )

    # =========================================================================
    # THEME PRESET
    # =========================================================================
    brand_preset = fields.Selection(
        selection=[
            ("tbwa", "TBWA (Black/Yellow)"),
            ("fluent_light", "Fluent Light"),
            ("fluent_dark", "Fluent Dark"),
            ("custom", "Custom"),
        ],
        string="Brand Preset",
        default="tbwa",
        help="Quick preset to apply predefined brand tokens",
    )

    # =========================================================================
    # METHODS
    # =========================================================================
    def get_brand_tokens_dict(self):
        """
        Return brand tokens as a dictionary suitable for JSON export.
        This is the canonical token structure consumed by React apps.
        """
        self.ensure_one()
        return {
            "palette": {
                "primary": self.brand_primary or "#000000",
                "primaryHover": self.brand_primary_hover or "#1A1A1A",
                "accent": self.brand_accent or "#FBBF24",
                "accentHover": self.brand_accent_hover or "#F59E0B",
                "success": self.brand_success or "#10B981",
                "warning": self.brand_warning or "#F59E0B",
                "danger": self.brand_danger or "#EF4444",
                "info": self.brand_info or "#3B82F6",
            },
            "surface": {
                "bg": self.brand_bg or "#FFFFFF",
                "card": self.brand_surface or "#F9FAFB",
                "elevated": self.brand_surface_elevated or "#FFFFFF",
                "border": self.brand_border or "#E5E7EB",
            },
            "text": {
                "primary": self.brand_text_primary or "#111827",
                "secondary": self.brand_text_secondary or "#6B7280",
                "onPrimary": self.brand_text_on_primary or "#FFFFFF",
                "onAccent": self.brand_text_on_accent or "#000000",
            },
            "radius": {
                "sm": self.brand_radius_sm or "4px",
                "md": self.brand_radius_md or "8px",
                "lg": self.brand_radius_lg or "12px",
            },
            "shadow": {
                "sm": self.brand_shadow_sm or "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                "md": self.brand_shadow_md or "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                "lg": self.brand_shadow_lg or "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
            },
            "typography": {
                "fontFamily": self.brand_font_family or '"Segoe UI", system-ui, sans-serif',
            },
            "meta": {
                "preset": self.brand_preset or "tbwa",
                "iconPack": self.brand_icon_pack or "fluent",
                "companyId": self.id,
                "companyName": self.name,
            },
        }

    def get_brand_tokens_css_vars(self):
        """
        Return brand tokens as CSS custom properties string.
        Used by the SCSS injection.
        """
        self.ensure_one()
        tokens = self.get_brand_tokens_dict()
        css_vars = []

        # Palette
        css_vars.append(f"--tbwa-primary: {tokens['palette']['primary']};")
        css_vars.append(f"--tbwa-primary-hover: {tokens['palette']['primaryHover']};")
        css_vars.append(f"--tbwa-accent: {tokens['palette']['accent']};")
        css_vars.append(f"--tbwa-accent-hover: {tokens['palette']['accentHover']};")
        css_vars.append(f"--tbwa-success: {tokens['palette']['success']};")
        css_vars.append(f"--tbwa-warning: {tokens['palette']['warning']};")
        css_vars.append(f"--tbwa-danger: {tokens['palette']['danger']};")
        css_vars.append(f"--tbwa-info: {tokens['palette']['info']};")

        # Surface
        css_vars.append(f"--tbwa-bg: {tokens['surface']['bg']};")
        css_vars.append(f"--tbwa-surface: {tokens['surface']['card']};")
        css_vars.append(f"--tbwa-surface-elevated: {tokens['surface']['elevated']};")
        css_vars.append(f"--tbwa-border: {tokens['surface']['border']};")

        # Text
        css_vars.append(f"--tbwa-text-primary: {tokens['text']['primary']};")
        css_vars.append(f"--tbwa-text-secondary: {tokens['text']['secondary']};")
        css_vars.append(f"--tbwa-text-on-primary: {tokens['text']['onPrimary']};")
        css_vars.append(f"--tbwa-text-on-accent: {tokens['text']['onAccent']};")

        # Shape
        css_vars.append(f"--tbwa-radius-sm: {tokens['radius']['sm']};")
        css_vars.append(f"--tbwa-radius-md: {tokens['radius']['md']};")
        css_vars.append(f"--tbwa-radius-lg: {tokens['radius']['lg']};")

        # Shadows
        css_vars.append(f"--tbwa-shadow-sm: {tokens['shadow']['sm']};")
        css_vars.append(f"--tbwa-shadow-md: {tokens['shadow']['md']};")
        css_vars.append(f"--tbwa-shadow-lg: {tokens['shadow']['lg']};")

        # Typography
        css_vars.append(f"--tbwa-font-family: {tokens['typography']['fontFamily']};")

        return "\n  ".join(css_vars)

    @api.model
    def action_reset_to_tbwa_defaults(self):
        """Reset brand tokens to TBWA defaults."""
        for company in self:
            company.write({
                "brand_preset": "tbwa",
                "brand_primary": "#000000",
                "brand_primary_hover": "#1A1A1A",
                "brand_accent": "#FBBF24",
                "brand_accent_hover": "#F59E0B",
                "brand_bg": "#FFFFFF",
                "brand_surface": "#F9FAFB",
                "brand_surface_elevated": "#FFFFFF",
                "brand_border": "#E5E7EB",
                "brand_text_primary": "#111827",
                "brand_text_secondary": "#6B7280",
                "brand_text_on_primary": "#FFFFFF",
                "brand_text_on_accent": "#000000",
                "brand_success": "#10B981",
                "brand_warning": "#F59E0B",
                "brand_danger": "#EF4444",
                "brand_info": "#3B82F6",
                "brand_radius_sm": "4px",
                "brand_radius_md": "8px",
                "brand_radius_lg": "12px",
                "brand_shadow_sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                "brand_shadow_md": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                "brand_shadow_lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                "brand_font_family": '"Segoe UI", system-ui, -apple-system, sans-serif',
                "brand_icon_pack": "fluent",
            })
        return True
