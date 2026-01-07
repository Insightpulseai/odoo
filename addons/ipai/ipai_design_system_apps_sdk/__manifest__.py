{
    "name": "IPAI Design System - Apps SDK UI",
    "version": "18.0.1.0.0",
    "category": "Tools/UI",
    "summary": "ChatGPT Apps SDK UI design tokens for all IPAI apps",
    "description": """
IPAI Design System - Apps SDK UI
================================

This module injects the ChatGPT Apps SDK UI design system into all Odoo
backend applications, providing a consistent platform-wide visual language.

Features:
---------
* Apps SDK UI CSS tokens and utilities
* TBWA accent color bridge
* Platform component classes (ipai-btn-primary, ipai-card, ipai-input)
* Scoped styling via .ipai-appsdk root class
* Optional portal/website support

Usage:
------
1. Install this module first before other IPAI modules
2. In your IPAI app templates, wrap UI with <div class="ipai-app">
3. Use platform component classes for consistent styling

Token Variables:
----------------
* --ipai-accent: Primary accent color (TBWA yellow)
* --ipai-bg: Background color
* --ipai-surface: Surface/card background
* --ipai-border: Border color
* --ipai-text: Primary text color
* --ipai-muted: Muted/secondary text

Component Classes:
------------------
* .ipai-btn-primary: Primary action button
* .ipai-card: Card container
* .ipai-input: Text input field
* .ipai-dialog: Modal dialog styling
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": ["web"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "ipai_design_system_apps_sdk/static/src/vendor/apps-sdk-ui-platform.css",
            "ipai_design_system_apps_sdk/static/src/scss/platform_overrides.scss",
            "ipai_design_system_apps_sdk/static/src/js/platform_boot.js",
        ],
        "web.assets_frontend": [
            "ipai_design_system_apps_sdk/static/src/vendor/apps-sdk-ui-platform.css",
            "ipai_design_system_apps_sdk/static/src/scss/platform_overrides.scss",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}
