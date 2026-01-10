# -*- coding: utf-8 -*-
{
    "name": "IPAI Marketing Journey Builder",
    "version": "18.0.1.0.1",
    "category": "Marketing",
    "summary": "Node-based marketing journey builder (Enterprise MA substitute)",
    "description": """
IPAI Marketing Journey Builder
==============================

Enterprise-like Marketing Automation substitute for Odoo CE.
Provides node-based journey builder with delays, branches, and multi-step sequences.

Features:
---------
* **Journey Builder**: Visual journey design with nodes and edges
* **Node Types**: Email, delay, branch, action, SMS
* **Participant Tracking**: State machine for journey participants
* **Execution Engine**: Cron-based runner for delayed actions
* **Mass Mailing Integration**: Orchestrates mass_mailing sends

OCA Integration:
----------------
This module orchestrates OCA modules:
- mass_mailing for email delivery
- automation_oca for trigger-based rules

Models:
-------
- marketing.journey: Journey definition
- marketing.journey.node: Journey step/node
- marketing.journey.edge: Node connections
- marketing.journey.participant: Participant state machine
- marketing.journey.execution.log: Execution audit trail

Author: InsightPulse AI
License: LGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_marketing_journey",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "mass_mailing",
        "utm",
        "ipai_agent_core",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/journey_views.xml",
        "views/node_views.xml",
        "views/participant_views.xml",
        "views/menu_views.xml",
        "data/cron_data.xml",
        "data/node_types.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_marketing_journey/static/src/css/journey.css",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
