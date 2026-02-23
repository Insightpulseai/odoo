# -*- coding: utf-8 -*-
{
    "name": "IPAI Design System",
    "summary": "Unified design system for IPAI platform - Fluent 2, TBWA, Copilot themes",
    "version": "18.0.1.0.0",
    "category": "Technical",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "AGPL-3",
    "depends": [
        "base",
        "web",
        "web_editor",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/brand_tokens.xml",
        "data/theme_presets.xml",
        "views/design_system_config_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # Design tokens (foundation layer)
            "ipai_design_system/static/src/scss/_tokens.scss",

            # Theme SCSS (order: base → brand → variant)
            "ipai_design_system/static/src/scss/_fluent2.scss",
            "ipai_design_system/static/src/scss/_tbwa.scss",
            "ipai_design_system/static/src/scss/_copilot.scss",
            "ipai_design_system/static/src/scss/_aiux.scss",
            "ipai_design_system/static/src/scss/main.scss",

            # JavaScript components
            "ipai_design_system/static/src/js/**/*.js",
        ],
        "web.assets_frontend": [
            # Frontend-specific assets
            "ipai_design_system/static/src/scss/main.scss",
        ],
    },
    "external_dependencies": {
        "python": [],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
