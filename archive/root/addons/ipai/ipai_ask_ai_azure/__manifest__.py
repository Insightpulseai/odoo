# (c) 2026 InsightPulse AI
# License LGPL-3.0-or-later
{
    "name": "IPAI Ask AI (Azure OpenAI)",
    "summary": "Systray Ask AI widget backed by Azure OpenAI — no IAP dependency",
    "version": "19.0.1.0.0",
    "category": "Technical",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_ask_ai_azure/static/src/scss/ask_ai_systray.scss",
            "ipai_ask_ai_azure/static/src/xml/ask_ai_systray.xml",
            "ipai_ask_ai_azure/static/src/js/ask_ai_systray.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}
