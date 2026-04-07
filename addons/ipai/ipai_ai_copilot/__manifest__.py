{
    "name": "IPAI AI Copilot",
    "version": "18.0.1.0.0",
    "summary": "DEPRECATED — Legacy Gemini/Supabase AI copilot bridge (superseded by ipai_odoo_copilot)",
    "description": """
        DEPRECATED as of 2026-03-13 (C-30).
        Superseded by ipai_odoo_copilot (Azure AI Foundry).

        Kept installable only because ipai_workspace_core depends on it.
        No new features, tools, or integrations should target this module.
        See docs/contracts/COPILOT_RUNTIME_CONTRACT.md for migration path.

        Original scope: Gemini function calling, Supabase RAG, n8n bridge.
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "category": "Productivity",
    "depends": ["mail", "web", "base", "ipai_ai_widget", "ipai_ai_core"],  # no enterprise deps
    "data": [
        "security/ir.model.access.csv",
        "data/res_partner_bot.xml",
        "data/mail_channel_ai.xml",
        "data/copilot_tools.xml",
        "data/copilot_cron.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_ai_copilot/static/src/js/copilot_service.js",
            "ipai_ai_copilot/static/src/js/copilot_sidebar.js",
            "ipai_ai_copilot/static/src/js/copilot_palette.js",
            "ipai_ai_copilot/static/src/xml/copilot_sidebar.xml",
            "ipai_ai_copilot/static/src/xml/copilot_palette.xml",
            "ipai_ai_copilot/static/src/css/copilot.css",
        ],
    },
    "external_dependencies": {"python": ["requests"]},
    "installable": False,  # DEPRECATED: All dependents migrated to ipai_odoo_copilot (2026-03-15)
    "application": False,
    "license": "LGPL-3",
}
