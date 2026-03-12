{
    "name": "IPAI Odoo Copilot — Azure Foundry Configuration",
    "summary": "Admin configuration layer for Azure Foundry Copilot agent",
    "version": "19.0.1.0.0",
    "category": "Technical",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["base_setup"],
    "data": [
        "views/res_config_settings_views.xml",
        "data/ir_actions_server.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
