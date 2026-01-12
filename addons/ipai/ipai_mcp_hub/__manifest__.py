# -*- coding: utf-8 -*-
{
    "name": "IPAI MCP Hub",
    "summary": "Model Context Protocol (MCP) server and tool registry",
    "description": """
IPAI MCP Hub
============

Thin metadata layer for MCP (Model Context Protocol) integration:

- MCP Server registry (Supabase, Azure, Vercel, DigitalOcean, GitHub)
- MCP Tool catalog with capabilities
- Model/Field bindings for context-aware tool invocation
- No business logic - just integration metadata

Architecture:
- Odoo stores registry of available MCP servers/tools
- External agents query this registry to know what tools are available
- Actual tool execution happens in sandbox/CLI, not Odoo controllers

Usage:
1. Register MCP servers in Settings
2. Catalog available tools per server
3. Bind tools to Odoo models/fields for context awareness
4. Query from CLI/agents: "For account.move, what tools are available?"
    """,
    "version": "18.0.1.0.0",
    "category": "Technical",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": [
        "security/ipai_mcp_security.xml",
        "security/ir.model.access.csv",
        "views/mcp_server_views.xml",
        "views/mcp_tool_views.xml",
        "views/mcp_binding_views.xml",
        "views/mcp_menu.xml",
        "data/mcp_server_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
