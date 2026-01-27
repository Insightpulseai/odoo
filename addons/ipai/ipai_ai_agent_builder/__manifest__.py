# -*- coding: utf-8 -*-
{
    "name": "AI Agent Builder",
    "version": "19.0.1.0.0",
    "category": "InsightPulse AI",
    "summary": "AI agents with system prompts, topics, tools",
    "description": """
AI Agent Builder
================

AI agents with system prompts, topics, tools

This module provides Odoo 19 Enterprise Edition parity for CE deployments.

**Features:**
- Core functionality for ai agent builder
- Integration with Odoo workflows
- Audit logging and compliance

**Configuration:**
- Go to Settings > IPAI > AI Agent Builder

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
    "installable": True,
    "application": False,
    "auto_install": False,
}
