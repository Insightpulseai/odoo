# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.
{
    "name": "IPAI AI Agent Builder",
    "version": "18.0.1.0.0",
    "category": "Productivity/AI",
    "summary": "Build AI agents with topics, tools, and RAG capabilities",
    "description": """
IPAI AI Agent Builder
=====================

This module provides Odoo 19 AI Agents feature parity for CE/OCA deployments:

- **Agents**: Configurable AI assistants with system prompts and response styles
- **Topics**: Instruction bundles that assign specific tools to agents
- **Tools**: Callable business actions with permission gating and audit trails
- **Sources**: Knowledge bases for RAG (Retrieval-Augmented Generation)

Features:
- Multi-provider support (ChatGPT, Gemini)
- Deterministic RAG pipeline
- Full audit logging
- Config-as-code via YAML
- REST API endpoints

References:
- Odoo 19 AI Agents: https://www.odoo.com/documentation/19.0/applications/productivity/ai/agents.html
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
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
