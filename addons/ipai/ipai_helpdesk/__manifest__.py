# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing.
{
    "name": "InsightPulse: Helpdesk",
    "summary": "Internal ticketing system with SLA tracking",
    "description": """
        Smart Delta module providing Enterprise Edition helpdesk parity.

        FEATURES:
        - Multi-team ticket management
        - SLA policies with escalation
        - Auto-assignment (balanced, round-robin, manual)
        - Customer portal for self-service
        - Time tracking per ticket
        - Knowledge base integration

        REPLACES:
        - helpdesk (Odoo Enterprise)

        EXTENDS:
        - project (uses project.task model concepts)
        - portal (self-service access)
    """,
    "version": "19.0.1.0.0",
    "category": "Services/Helpdesk",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "portal",
        "hr",
    ],
    "data": [
        # Security
        "security/ir.model.access.csv",
        "security/helpdesk_security.xml",
        # Data
        "data/helpdesk_stage_data.xml",
        # Views
        "views/helpdesk_ticket_views.xml",
        "views/helpdesk_team_views.xml",
        "views/menu.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "ipai_helpdesk/static/src/**/*",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
