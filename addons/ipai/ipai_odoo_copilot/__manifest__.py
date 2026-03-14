# -*- coding: utf-8 -*-
{
    "name": "IPAI Odoo Copilot — Azure Foundry",
    "version": "19.0.1.0.0",
    "category": "Productivity/Discuss",
    "summary": "Thin Odoo control-plane integration for Azure Foundry Copilot",
    "description": """
IPAI Odoo Copilot

Thin Odoo integration addon for Azure Foundry Copilot.
Provides:
- admin configuration via res.config.settings
- bounded connection and agent-verification actions
- optional healthcheck cron
- Odoo-side policy/control boundary for external copilot runtime
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "base_setup",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "data/ir_actions_server.xml",
        "data/ir_cron.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
