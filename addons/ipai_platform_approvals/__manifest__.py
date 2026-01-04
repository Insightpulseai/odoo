{
    "name": "IPAI Platform - Approvals",
    "version": "18.0.1.0.0",
    "category": "Technical",
    "summary": "Role-based approval chains for IPAI modules",
    "description": """
IPAI Platform Approvals
=======================

Provides configurable approval chain functionality for IPAI modules.

Features:
- Role-based approver lookup
- Multi-level approval chains
- Delegation configuration
- Escalation timers
- Approval audit trail

This module extends ipai_platform_workflow to add approval-specific
functionality like approver resolution, delegation, and escalation.
    """,
    "author": "IPAI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": ["base", "mail", "ipai_platform_workflow"],
    "data": [
        "security/ir.model.access.csv",
        "views/approval_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
