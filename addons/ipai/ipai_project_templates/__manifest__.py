# -*- coding: utf-8 -*-
{
    "name": "Project Templates",
    "version": "19.0.1.0.0",
    "category": "InsightPulse AI",
    "summary": "Project and task templates",
    "description": """
Project Templates
=================

Project and task templates

This module provides Odoo 19 Enterprise Edition parity for CE deployments.

**Features:**
- Core functionality for project templates
- Integration with Odoo workflows
- Audit logging and compliance

**Configuration:**
- Go to Settings > IPAI > Project Templates

**Credits:**
- InsightPulse AI Team
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": ["project"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
