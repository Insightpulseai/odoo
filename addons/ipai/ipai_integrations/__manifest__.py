# -*- coding: utf-8 -*-
{
    "name": "IPAI Integrations",
    "version": "18.0.1.0.0",
    "category": "Technical/Integrations",
    "summary": "Central integration hub for Mattermost, Focalboard, and n8n",
    "description": """
IPAI Integrations
=================

Admin UI for managing external collaboration tool integrations,
modeled after Mattermost's Integrations menu.

Features:
---------
* Webhook registration and management (incoming/outgoing)
* Bot account configuration
* OAuth application management
* Slash command definitions
* Integration audit logging
* Connector status monitoring

Supported Integrations:
-----------------------
* Mattermost (chat.insightpulseai.net)
* Focalboard (boards.insightpulseai.net)
* n8n (n8n.insightpulseai.net)

Architecture:
-------------
This module provides the core admin UI. Actual API clients
and sync jobs are in separate connector modules:
* ipai_mattermost_connector
* ipai_focalboard_connector
* ipai_n8n_connector

Note: Mattermost, Focalboard, and n8n run in a separate
deployment (ipai-collab-stack), NOT vendored into this repo.

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
        "security/integrations_security.xml",
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "views/integration_views.xml",
        "views/webhook_views.xml",
        "views/bot_views.xml",
        "views/oauth_views.xml",
        "views/audit_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
