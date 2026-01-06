# -*- coding: utf-8 -*-
{
    "name": "IPAI AI Agents UI (React + Fluent)",
    "version": "18.0.1.0.0",
    "category": "Productivity/AI",
    "summary": "React + Fluent UI v9 panel for AI agents (Ask AI, citations, evidence)",
    "description": """
IPAI AI Agents UI
=================

Modern Ask AI panel built with React and Microsoft Fluent UI v9.

Features:
---------
* Command palette integration (Alt+Shift+F)
* Agent selection dropdown
* Threaded conversations
* Citation rendering with source links
* Confidence scoring display
* Light/dark theme switching
* Streaming-ready architecture

Technical:
----------
* React 18 + Fluent UI v9 IIFE bundle
* Loaded via web.assets_backend
* Client action wrapper for Odoo integration
* Uses ipai_ai_core for backend services

Usage:
------
1. Install this module and ipai_ai_core
2. Configure AI provider in Settings
3. Press Alt+Shift+F or use menu AI → Ask AI (Fluent UI)
4. Start asking questions!

Author: InsightPulse AI
License: LGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "web",
        "ipai_ai_core",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # Odoo integration wrappers
            "ipai_ai_agents_ui/static/src/command_palette.js",
            "ipai_ai_agents_ui/static/src/ai_panel_react_action.js",
            # Pre-built React + Fluent UI bundle
            "ipai_ai_agents_ui/static/lib/ipai_ai_ui.iife.js",
            "ipai_ai_agents_ui/static/lib/ipai_ai_ui.css",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
