# Copyright 2026 InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fluent Web 365 Copilot",
    "summary": "SAP Joule / Microsoft 365 Copilot–style AI assistant prototype for Odoo",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "author": "InsightPulse AI, Odoo Community Association (OCA)",
    "maintainers": ["jgtolentino"],
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "development_status": "Alpha",
    "depends": [
        "base",
        "mail",
        "project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/fluent_copilot_menu.xml",
        "views/fluent_copilot_intent_views.xml",
        "views/fluent_copilot_session_views.xml",
        "views/fluent_copilot_message_views.xml",
        "views/fluent_copilot_integration_views.xml",
    ],
    "demo": [
        "demo/fluent_copilot_demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # Future: Add custom JS/CSS for chat-style UI
        ],
    },
    "external_dependencies": {
        "python": [],
    },
}
