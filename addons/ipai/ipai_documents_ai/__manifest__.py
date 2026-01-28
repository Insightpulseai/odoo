# -*- coding: utf-8 -*-
{
    "name": "DEPRECATED: Documents AI",
    "version": "19.0.1.0.0",
    "category": "InsightPulse AI",
    "summary": "DEPRECATED - Use dms (OCA) + ipai_enterprise_bridge instead. Do not install.",
    "description": """
Documents AI
============

AI document classification

This module provides Odoo 19 Enterprise Edition parity for CE deployments.

**Features:**
- Core functionality for documents ai
- Integration with Odoo workflows
- Audit logging and compliance

**Configuration:**
- Go to Settings > IPAI > Documents AI

**Credits:**
- InsightPulse AI Team
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": ["mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
    ],
    "demo": [],
    "installable": False,
    "application": False,
    "auto_install": False,
}
