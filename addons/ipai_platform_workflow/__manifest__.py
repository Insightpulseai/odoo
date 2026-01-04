{
    "name": "IPAI Platform - Workflow Engine",
    "version": "18.0.1.0.0",
    "category": "Technical",
    "summary": "Generic workflow state machine for IPAI modules",
    "description": """
IPAI Platform Workflow Engine
=============================

Provides a generic, reusable workflow state machine for IPAI modules.

Features:
- Configurable state definitions
- Transition rules with conditions
- Notification hooks (email, Mattermost)
- Audit trail integration

This module serves as the foundation for approval workflows,
status tracking, and process automation across all IPAI modules.
    """,
    "author": "IPAI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/workflow_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
