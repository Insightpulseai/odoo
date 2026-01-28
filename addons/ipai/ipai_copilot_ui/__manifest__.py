# -*- coding: utf-8 -*-
{
    "name": "DEPRECATED: IPAI Copilot UI",
    "version": "18.0.1.0.0",
    "category": "Themes/Backend",
    "summary": "DEPRECATED - Use ipai_design_system_apps_sdk instead. Do not install.",
    "description": """
IPAI Copilot UI
===============

This module provides a Microsoft 365 Copilot-inspired user interface built with
OWL components and Fluent 2 design tokens. It renders a full-screen chat shell
with tool cards, similar to the M365 Copilot experience.

Features:
---------
- Fluent 2 design tokens as CSS variables
- Full-screen Copilot shell layout
- Sidebar navigation (Chat / Library / Apps)
- Tool cards grid for AI capabilities
- Responsive prompt input area
- Light theme with soft shadows and modern radii

Components:
-----------
- CopilotShell: Main layout component
- CopilotSidebar: Left navigation panel
- CopilotToolCard: Individual tool card component

Usage:
------
Navigate to: Apps > IPAI Copilot
Or use the client action: ipai_copilot_shell

Design Reference:
-----------------
Based on Microsoft 365 Copilot UI patterns:
https://copilot.microsoft.com/

Author: InsightPulse AI
License: LGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "web",
    ],
    "data": [
        "views/copilot_action.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_copilot_ui/static/src/scss/copilot_theme.scss",
            "ipai_copilot_ui/static/src/js/copilot_shell.js",
            "ipai_copilot_ui/static/src/xml/copilot_shell.xml",
        ],
    },
    "installable": False,
    "application": True,
    "auto_install": False,
}
