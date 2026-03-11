{
    "name": "IPAI AI Copilot",
    "version": "19.0.2.0.0",
    "summary": "M365 Copilot / SAP Joule-class AI for Odoo 19 CE — Azure ACA-ready",
    "description": """
        Pervasive AI copilot for Odoo 19 CE. Surpasses Odoo EE AI Agents with:
        - Azure OpenAI (Responses + Chat Completions API modes)
        - Gemini function calling (AI can execute Odoo actions)
        - Persistent sidebar on every screen
        - Cross-module awareness and proactive insights
        - Env-to-config seeding for Azure Container Apps
        - Self-contained provider bridge (no ipai_ai_widget dependency)
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "category": "Productivity",
    "depends": ["base", "mail", "ipai_ai_core"],
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
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
