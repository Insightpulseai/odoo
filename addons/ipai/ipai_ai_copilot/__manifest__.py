{
    "name": "IPAI AI Copilot",
    "version": "19.0.1.0.0",
    "summary": "M365 Copilot / SAP Joule-class AI for Odoo 19 CE",
    "description": """
        Pervasive AI copilot for Odoo 19 CE. Surpasses Odoo EE AI Agents with:
        - Gemini function calling (AI can execute Odoo actions)
        - Persistent sidebar on every screen
        - Cross-module awareness and proactive insights
        - Supabase RAG for external knowledge
        - n8n automation bridge for cross-system workflows
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "category": "Productivity",
    "depends": ["mail", "web", "base"],  # no enterprise deps
    "data": [
        "security/ir.model.access.csv",
        "data/copilot_tools.xml",
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
