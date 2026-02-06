# -*- coding: utf-8 -*-
{
    "name": "DEPRECATED: IPAI Web Theme - TBWA",
    "version": "19.0.1.0.0",
    "category": "Themes/Backend",
    "summary": "DEPRECATED - Use ipai_design_system_apps_sdk instead. Do not install.",
    "description": """
IPAI Web Theme - TBWA
=====================

Applies TBWA brand styling to Odoo CE 18 backend by consuming design tokens
from ipai_ui_brand_tokens module.

This is **Adapter A** in the token architecture:
- Consumes tokens from ipai_ui_brand_tokens
- Sets CSS vars + SCSS overrides
- Styles Odoo UI components with TBWA black/yellow palette

Styled Components
-----------------
- Primary buttons (black background, yellow accent)
- Topbar and left menu
- Kanban cards and list views
- Form buttons and status badges
- Chatter and mail styling
- Focus/hover states

Philosophy
----------
Keep overrides surgical and targeted:
- Use CSS variables (not hard-coded colors)
- Minimal SCSS that references --tbwa-* vars
- Don't fight Odoo's default styling unnecessarily

Installation Order
------------------
1. ipai_ui_brand_tokens (required dependency)
2. ipai_web_theme_tbwa (this module)
3. ipai_web_icons_fluent (optional)
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "web",
        "mail",
        "ipai_ui_brand_tokens",
    ],
    "data": [
        "views/assets.xml",
        "views/webclient_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_web_theme_tbwa/static/src/scss/theme.scss",
            "ipai_web_theme_tbwa/static/src/scss/components/buttons.scss",
            "ipai_web_theme_tbwa/static/src/scss/components/navbar.scss",
            "ipai_web_theme_tbwa/static/src/scss/components/kanban.scss",
            "ipai_web_theme_tbwa/static/src/scss/components/list.scss",
            "ipai_web_theme_tbwa/static/src/scss/components/form.scss",
            "ipai_web_theme_tbwa/static/src/scss/components/chatter.scss",
            "ipai_web_theme_tbwa/static/src/scss/components/footer.scss",
        ],
        "web.assets_frontend": [
            "ipai_web_theme_tbwa/static/src/scss/components/login.scss",
            "ipai_web_theme_tbwa/static/src/scss/components/footer.scss",
        ],
    },
    "installable": False,
    "application": False,
    "auto_install": False,
}
