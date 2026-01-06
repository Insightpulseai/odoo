# -*- coding: utf-8 -*-
{
    "name": "IPAI Mattermost Connector",
    "version": "18.0.1.0.0",
    "category": "Technical/Integrations",
    "summary": "API client and sync for Mattermost chat platform",
    "description": """
IPAI Mattermost Connector
=========================

Connects Odoo to Mattermost for real-time chat and notification integration.

Features:
---------
* Mattermost API v4 client
* Channel/team synchronization
* Post messages from Odoo workflows
* Receive and process incoming webhooks
* Bot account management
* Slash command handlers

Architecture:
-------------
This module provides the Mattermost-specific API client and models.
For the admin UI, see ipai_integrations module.

External Service:
-----------------
Mattermost runs in ipai-ops-stack (NOT vendored here):
* URL: https://chat.insightpulseai.net
* API: Mattermost API v4

Author: InsightPulse AI
License: LGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "ipai_integrations",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/connector_data.xml",
        "views/mattermost_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
