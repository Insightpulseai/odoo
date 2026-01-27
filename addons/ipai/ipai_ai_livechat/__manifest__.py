# -*- coding: utf-8 -*-
{
    "name": "AI Livechat",
    "version": "19.0.1.0.0",
    "category": "InsightPulse AI",
    "summary": "AI agent for live chat",
    "description": """
AI Livechat
===========

AI agent for live chat

This module provides Odoo 19 Enterprise Edition parity for CE deployments.

**Features:**
- Core functionality for ai livechat
- Integration with Odoo workflows
- Audit logging and compliance

**Configuration:**
- Go to Settings > IPAI > AI Livechat

**Credits:**
- InsightPulse AI Team
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": ["ipai_ai_agent_builder", "im_livechat"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
