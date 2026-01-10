{
    "name": "IPAI AIUX Theme",
    "version": "18.0.0.1.0",
    "category": "Theme/Backend",
    "summary": "AIUX backend theme scaffold (sidebar tokens + widget hooks)",
    "description": """
IPAI AIUX Theme
===============

Provides AIUX design system integration for Odoo 18 backend:

* CSS custom properties (tokens) aligned with @insightpulse/design-tokens
* Collapsible sidebar styling hooks
* Widget mount points for Ask AI components
* Dark mode support preparation

This is a scaffold module - full UI implementation follows.

Mode Types (canonical):
- minimize: Collapsed pill state
- popup: Floating chat window
- sidepanel: Full side panel (NOT fullscreen)
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "depends": ["web"],
    "data": [
        "views/assets.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_theme_aiux/static/src/scss/aiux_tokens.scss",
        ],
    },
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": False,
}
