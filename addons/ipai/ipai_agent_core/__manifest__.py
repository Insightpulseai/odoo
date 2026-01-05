# -*- coding: utf-8 -*-
{
    "name": "IPAI Agent Core",
    "version": "18.0.1.0.0",
    "category": "Productivity/AI",
    "summary": "Skill/tool/knowledge registry + run logs for IPAI agents",
    "description": """
IPAI Agent Core - Agent Skill Registry
=======================================

Central registry for AI agent skills, tools, and knowledge sources.

Features:
---------
* **Skills**: Workflow definitions with intent routing
* **Tools**: Callable actions mapped to Odoo methods
* **Knowledge Sources**: Documents, URLs, models for context
* **Run Logs**: Full audit trail of agent executions

Usage:
------
1. Define skills in skillpack/manifest.json
2. Install this module to load skills into database
3. Execute skills via ipai.agent.run records
4. Monitor runs in Agent Core → Runs menu

Integration:
------------
Works with ipai_studio_ai for natural language customization
and external clients (ChatGPT Apps, MCP servers) via JSON-RPC.

Author: InsightPulse AI
License: LGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_agent_core",
    "license": "LGPL-3",
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/agent_core_menu.xml",
        "views/skill_views.xml",
        "views/tool_views.xml",
        "views/knowledge_views.xml",
        "views/run_views.xml",
        "data/seed_skillpack.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": True,
    "auto_install": False,
}
