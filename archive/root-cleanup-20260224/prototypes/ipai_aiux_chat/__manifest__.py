{
    "name": "IPAI AIUX Chat",
    "version": "18.0.0.1.0",
    "category": "Productivity",
    "summary": "AIUX OWL chat widget scaffold (Ask AI integration)",
    "description": """
IPAI AIUX Chat Widget
=====================

Provides the AIUX chat widget for Odoo 18 backend:

* OWL component for Ask AI interaction
* Three display modes:
  - minimize: Collapsed pill (tooltip on hover)
  - popup: Floating chat window (400x500px)
  - sidepanel: Docked side panel (resizable)
* Context-aware (model/res_id/view_type binding)
* Session persistence across mode switches

IMPORTANT: Use 'sidepanel' NOT 'fullscreen' for the docked mode.

This is a scaffold module - full widget implementation follows.
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "depends": ["web", "ipai_theme_aiux"],
    "data": [
        "views/assets.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_aiux_chat/static/src/js/aiux_chat_service.js",
            "ipai_aiux_chat/static/src/xml/aiux_chat_templates.xml",
        ],
    },
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": False,
}
