# -*- coding: utf-8 -*-
{
    "name": "IPAI Odoo Copilot — Azure Foundry",
    "version": "19.0.2.0.0",
    "category": "Productivity/Discuss",
    "summary": "Odoo control-plane integration for Microsoft Foundry Copilot with RAG knowledge bases",
    "description": """
IPAI Odoo Copilot

Odoo integration addon for Microsoft Foundry Copilot (Responses API v2).
Provides:
- admin configuration via res.config.settings
- bounded connection and agent-verification actions
- optional healthcheck cron
- Odoo-side policy/control boundary for external copilot runtime
- Grounded RAG search across 3 knowledge bases (Odoo, Azure, Databricks)
- DefaultAzureCredential auth chain (managed identity, az login, env vars)
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "base_setup",
    ],
    "external_dependencies": {
        "python": [
            "azure-identity",
            "azure-search-documents",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "data/ir_actions_server.xml",
        "data/ir_cron.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_odoo_copilot/static/src/js/copilot_systray.js",
            "ipai_odoo_copilot/static/src/xml/copilot_systray.xml",
            "ipai_odoo_copilot/static/src/scss/copilot_systray.scss",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
