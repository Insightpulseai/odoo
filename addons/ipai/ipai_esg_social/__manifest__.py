# -*- coding: utf-8 -*-
{
    "name": "ESG Social Metrics",
    "version": "19.0.1.0.0",
    "category": "InsightPulse AI",
    "summary": "Gender parity and pay gap",
    "description": """
ESG Social Metrics
==================

Gender parity and pay gap

This module provides Odoo 19 Enterprise Edition parity for CE deployments.

**Features:**
- Core functionality for esg social metrics
- Integration with Odoo workflows
- Audit logging and compliance

**Configuration:**
- Go to Settings > IPAI > ESG Social Metrics

**Credits:**
- InsightPulse AI Team
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": ["hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
