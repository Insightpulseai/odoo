# -*- coding: utf-8 -*-
{
    "name": "IPAI AI Default Prompts",
    "version": "19.0.1.0.0",
    "category": "Productivity/AI",
    "summary": "Contextual default prompt registry for AI agents",
    "description": """
IPAI AI Default Prompts
========================

Official Odoo 19 AI parity: configurable prompt registry for contextual
AI helpers embedded into Odoo workflows.

Each prompt defines:
- A contextual trigger (mail composer, text selector, chatter, etc.)
- Instructions for the AI agent
- An assigned agent and optional topic
- A primary action button label

Seed data includes 10 default prompts matching the official Odoo 19 AI
Default Prompts structure.
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "ipai_ai_agent_builder",
        "ipai_ai_core",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ai_prompt_views.xml",
        "data/ai_prompt_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
