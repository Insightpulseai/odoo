# -*- coding: utf-8 -*-
{
    "name": "IPAI Skill API",
    "version": "18.0.1.0.0",
    "category": "Productivity/AI",
    "summary": "REST API endpoints for agent skill execution",
    "description": """
IPAI Skill API - REST Endpoints for Agent Skills
=================================================

Exposes agent skills and run execution via REST API for external
agent surfaces (Claude Code CLI, MCP servers, n8n workflows).

Features:
---------
* **Skills Endpoint**: List and discover available skills
* **Runs Endpoint**: Create, execute, and monitor runs
* **OpenAPI**: Auto-generated documentation
* **Auth**: JWT and API key authentication support

Endpoints:
----------
* GET  /api/v1/skills         - List active skills
* GET  /api/v1/skills/{key}   - Get skill by key
* POST /api/v1/runs           - Create and optionally execute run
* GET  /api/v1/runs/{id}      - Get run status and trace
* POST /api/v1/runs/{id}/execute - Execute a draft run

Dependencies:
-------------
* ipai_agent_core - Skill/tool/run models
* base_rest (OCA) - REST framework (optional, graceful fallback)

Author: InsightPulse AI
License: LGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "base",
        "web",
        "ipai_agent_core",
    ],
    "external_dependencies": {
        "python": [],
    },
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
