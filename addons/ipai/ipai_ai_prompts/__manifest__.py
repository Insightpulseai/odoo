# -*- coding: utf-8 -*-
{
    "name": "IPAI AI Prompts Library",
    "version": "18.0.1.0.0",
    "category": "Productivity/AI",
    "summary": "Prompt templates and topic library for AI interactions",
    "description": """
IPAI AI Prompts Library
=======================

Centralized management of AI prompts, templates, and topic definitions
for use across the IPAI AI ecosystem.

Features:
---------
* **Prompt Templates**: Reusable prompt definitions with variables
* **Topic Library**: Categorized topics for AI assistance (Finance, Marketing, HR, etc.)
* **Preset Actions**: Quick "Ask AI" presets for common tasks
* **Persona Definitions**: AI persona/tone configurations
* **Context Builders**: Dynamic context assembly for prompts

Prompt Structure:
-----------------
Each prompt template supports:
- System instructions
- Variable placeholders ({{variable}})
- Output format specifications
- Example few-shot patterns

Topics:
-------
Topics organize prompts by domain:
- Finance & Accounting
- Marketing & Sales
- HR & Operations
- Technical Support
- General Assistant

Author: InsightPulse AI
License: LGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_ai_prompts",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "ipai_agent_core",
        "ipai_ai_provider_pulser",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/prompt_views.xml",
        "views/topic_views.xml",
        "views/menu_views.xml",
        "data/topics.xml",
        "data/prompts.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
