# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.
{
    "name": "DEPRECATED: WhatsApp Connector",
    "version": "19.0.1.0.0",
    "category": "Productivity/AI",
    "summary": "Build AI agents with topics, tools, and RAG capabilities",
    "description": """
WhatsApp Connector
==================

WhatsApp messaging integration

- **Agents**: Configurable AI assistants with system prompts and response styles
- **Topics**: Instruction bundles that assign specific tools to agents
- **Tools**: Callable business actions with permission gating and audit trails
- **Sources**: Knowledge bases for RAG (Retrieval-Augmented Generation)

**Features:**
- Core functionality for whatsapp connector
- Integration with Odoo workflows
- Audit logging and compliance

**Configuration:**
- Go to Settings > IPAI > WhatsApp Connector

**Credits:**
- InsightPulse AI Team
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "web",
        "mail",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ai_agent_data.xml",
        "views/ai_agent_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    "external_dependencies": {
        "python": ["openai", "pyyaml"],
    },
}
