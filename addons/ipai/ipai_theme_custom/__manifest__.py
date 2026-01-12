# Part of IPAI. See LICENSE file for full copyright and licensing details.

{
    "name": "IPAI Custom Theme Colors",
    "version": "18.0.1.0.0",
    "category": "Theme",
    "summary": "Customizable theme with configurable colors via CSS variables",
    "description": """
IPAI Custom Theme Colors
========================

A color-agnostic theme module that provides:

* Configurable color palette via Settings
* CSS variables for all color tokens (no hardcoded colors)
* Support for primary, accent, semantic, surface, and text colors
* Easy customization without code changes
* Dark mode support

Configuration
-------------
Go to Settings > General Settings > Theme Colors to customize:

* Primary and accent colors
* Success, warning, danger, info semantic colors
* Background and surface colors
* Text colors
* Border radius and shadow settings

All colors are stored per-company and injected as CSS custom properties.
    """,
    "author": "IPAI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/theme_preview_template.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_theme_custom/static/src/scss/variables.scss",
            "ipai_theme_custom/static/src/scss/theme.scss",
            "ipai_theme_custom/static/src/scss/components.scss",
        ],
        "web.assets_frontend": [
            "ipai_theme_custom/static/src/scss/variables.scss",
            "ipai_theme_custom/static/src/scss/theme.scss",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}
