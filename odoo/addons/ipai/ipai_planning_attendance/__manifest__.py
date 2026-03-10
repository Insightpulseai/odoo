# -*- coding: utf-8 -*-
{
    "name": "DEPRECATED: Planning Attendance",
    "version": "19.0.1.0.0",
    "category": "InsightPulse AI",
    "summary": "DEPRECATED - Migrated to ipai_enterprise_bridge. Do not install.",
    "description": """
Planning Attendance
===================

Compare planned vs attended

This module provides Odoo 19 Enterprise Edition parity for CE deployments.

**Features:**
- Core functionality for planning attendance
- Integration with Odoo workflows
- Audit logging and compliance

**Configuration:**
- Go to Settings > IPAI > Planning Attendance

**Credits:**
- InsightPulse AI Team
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["hr_attendance"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
    ],
    "demo": [],
    "installable": False,
    "application": False,
    "auto_install": False,
}
