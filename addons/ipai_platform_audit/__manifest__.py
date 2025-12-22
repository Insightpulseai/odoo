{
    "name": "IPAI Platform - Audit Trail",
    "version": "18.0.1.0.0",
    "category": "Technical",
    "summary": "Field-level audit trail for IPAI modules",
    "description": """
IPAI Platform Audit Trail
=========================

Provides comprehensive audit trail functionality for IPAI modules.

Features:
- Field-level change tracking
- Configurable audit policies per model
- Change history viewer
- Retention and archival rules
- Export capabilities

This module enables compliance-grade audit logging for
sensitive data and operations across all IPAI modules.
    """,
    "author": "IPAI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/audit_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
