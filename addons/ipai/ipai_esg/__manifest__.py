# -*- coding: utf-8 -*-
{
    "name": "DEPRECATED: ESG Carbon Analytics",
    "version": "19.0.1.0.0",
    "category": "InsightPulse AI",
    "summary": "DEPRECATED - Migrated to ipai_enterprise_bridge. Do not install.",
    "description": """
ESG Carbon Analytics
====================

Carbon footprint tracking

This module provides Odoo 19 Enterprise Edition parity for CE deployments.

**Features:**
- Core functionality for esg carbon analytics
- Integration with Odoo workflows
- Audit logging and compliance

**Configuration:**
- Go to Settings > IPAI > ESG Carbon Analytics

**Credits:**
- InsightPulse AI Team
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
    ],
    "demo": [],
    "installable": False,
    "application": False,
    "auto_install": False,
}
