# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.
{
    "name": "IPAI AI Tools",
    "version": "18.0.1.0.0",
    "category": "Productivity/AI",
    "summary": "Built-in tools for AI agents to execute business actions",
    "description": """
IPAI AI Tools
=============

This module provides built-in tools that AI agents can execute:

- **CRM Tools**: Create leads, update opportunities
- **Calendar Tools**: Schedule events and meetings
- **Sale Tools**: Create sale orders

Features:
- Permission-gated execution
- Full audit trail
- Dry-run mode for testing
- Extensible tool framework
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "ipai_ai_agent_builder",
        "crm",
        "calendar",
        "sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ai_tools_data.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
