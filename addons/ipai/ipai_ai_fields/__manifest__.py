# -*- coding: utf-8 -*-
{
    "name": "AI Fields",
    "version": "19.0.1.0.0",
    "category": "InsightPulse AI",
    "summary": "AI-powered field population",
    "description": """
AI Fields
=========

AI-powered field population

This module provides Odoo 19 Enterprise Edition parity for CE deployments.

**Features:**
- Core functionality for ai fields
- Integration with Odoo workflows
- Audit logging and compliance

**Configuration:**
- Go to Settings > IPAI > AI Fields

**Credits:**
- InsightPulse AI Team
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": ["ipai_ai_agent_builder"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
