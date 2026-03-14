{
    "name": "IPAI AI Copilot (DEPRECATED)",
    "version": "19.0.2.0.0",
    "summary": "DEPRECATED — replaced by ipai_odoo_copilot (Azure Foundry). Do not extend.",
    "description": """
        DEPRECATED as of 2026-03-13.
        Replaced by: ipai_odoo_copilot (Azure AI Foundry — ipai-odoo-copilot-azure).
        See: docs/contracts/COPILOT_RUNTIME_CONTRACT.md (C-30).

        This module remains installable only because ipai_workspace_core and
        ipai_ai_channel_actions still depend on it. No new features, tools, or
        integrations should target this module. Migration path: dependents must
        migrate to ipai_odoo_copilot before this module can be removed.

        Legacy stack: Gemini via Vercel bridge → Supabase pgvector RAG.
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
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
