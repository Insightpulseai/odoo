# -*- coding: utf-8 -*-
{
    "name": "IPAI Focalboard Connector",
    "version": "18.0.1.0.0",
    "category": "Technical/Integrations",
    "summary": "API client and sync for Focalboard project boards",
    "description": """
IPAI Focalboard Connector
=========================

Connects Odoo to Focalboard for Kanban-style project tracking.

Features:
---------
* Focalboard API client
* Board/card synchronization
* Bidirectional task sync with Odoo project.task
* Webhook handlers for real-time updates

Architecture:
-------------
This module provides the Focalboard-specific API client and models.
For the admin UI, see ipai_integrations module.

External Service:
-----------------
Focalboard runs in ipai-ops-stack (NOT vendored here):
* URL: https://boards.insightpulseai.net
* API: Focalboard REST API

Author: InsightPulse AI
License: LGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "base",
        "project",
        "ipai_integrations",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/connector_data.xml",
        "views/focalboard_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
