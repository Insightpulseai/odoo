# -*- coding: utf-8 -*-
{
    "name": "IPAI Odoo Copilot — Azure Foundry",
    "version": "19.0.2.0.0",
    "category": "Productivity/Discuss",
    "summary": "Azure Foundry Copilot provider for Odoo Discuss",
    "description": """
IPAI Odoo Copilot — Azure Foundry

Provides:
- Azure Foundry copilot in Odoo Discuss (DM-based chat)
- Admin configuration via res.config.settings
- Bounded connection and agent-verification actions
- Optional healthcheck cron
- Dual auth audience support (Foundry project vs Cognitive Services)
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "base_setup",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "data/copilot_partner_data.xml",
        "data/ir_actions_server.xml",
        "data/ir_cron.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
