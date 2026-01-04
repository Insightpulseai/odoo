{
    "name": "IPAI CRM - Pipeline Clone",
    "version": "18.0.1.0.0",
    "category": "Sales/CRM",
    "summary": "Salesforce-like CRM pipeline experience",
    "description": """
IPAI CRM Pipeline Clone
=======================

Delivers a Salesforce-like CRM pipeline experience on Odoo CRM.

Capability ID: crm.pipeline.board (P0)

Features:
- Enhanced kanban board with stage rules
- Quick action buttons (log call, schedule meeting, send email)
- Activity timeline improvements
- Stage validation rules
- Role-based dashboards

This module targets feature parity with Salesforce Sales Cloud
pipeline functionality while leveraging the IPAI design system.
    """,
    "author": "IPAI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "crm",
        "mail",
        "ipai_platform_workflow",
        "ipai_platform_theme",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/crm_lead_views.xml",
        "views/crm_stage_views.xml",
        "data/crm_stage_rules.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_crm_pipeline/static/src/scss/pipeline.scss",
        ],
    },
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
