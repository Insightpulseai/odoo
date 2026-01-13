# -*- coding: utf-8 -*-
{
    "name": "IPAI Copilot Hub",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "summary": "Ops Control Room / AI Runbook Hub with Fluent UI shell",
    "description": """
IPAI Copilot Hub
================

A centralized operations control room that embeds an external Fluent UI
application for managing AI runbooks, pipelines, and operational workflows.

Features
--------
* Embeds external Fluent UI shell via iframe
* Configurable external URL via system parameter
* Full-screen client action for immersive experience
* OWL component with loading states and error handling
* Fluent 2 design tokens integration

Architecture
------------
This module acts as a bridge between Odoo and an external Ops Control Room
application built with Microsoft Fluent UI React components.

The external app URL is configured via the system parameter:
``ipai.copilot.hub_url``

Menu Structure
--------------
* Ops Control Room
    * AI Runbooks - Main embedded dashboard
    * Settings - Configuration panel

Configuration
-------------
Set the system parameter ``ipai.copilot.hub_url`` to your Fluent UI app URL.
Default: https://ops.insightpulseai.net

Usage
-----
1. Install the module
2. Configure the hub URL in Settings > Technical > System Parameters
3. Navigate to Ops Control Room menu

Author: InsightPulse AI
License: LGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "base",
        "web",
        "mail",
    ],
    "data": [
        # Security
        "security/copilot_hub_security.xml",
        "security/ir.model.access.csv",
        # Data
        "data/ir_config_parameter.xml",
        # Views
        "views/copilot_hub_views.xml",
        "views/copilot_hub_menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_copilot_hub/static/src/css/copilot_hub.css",
            "ipai_copilot_hub/static/src/js/copilot_hub.js",
            "ipai_copilot_hub/static/src/xml/copilot_hub_templates.xml",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
