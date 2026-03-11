# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.
{
    "name": "DEPRECATED: AI Automations",
    "version": "19.0.1.0.0",
    "category": "InsightPulse AI",
    "summary": "DEPRECATED - Migrated to ipai_enterprise_bridge. Do not install.",
    "description": """
AI Automations
==============

AI in server actions

- **CRM Tools**: Create leads, update opportunities
- **Calendar Tools**: Schedule events and meetings
- **Sale Tools**: Create sale orders

**Features:**
- Core functionality for ai automations
- Integration with Odoo workflows
- Audit logging and compliance

**Configuration:**
- Go to Settings > IPAI > AI Automations

**Credits:**
- InsightPulse AI Team
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["ipai_ai_agent_builder", "base_automation"],
    "data": [
        "security/ir.model.access.csv",
        "data/ai_tools_data.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
