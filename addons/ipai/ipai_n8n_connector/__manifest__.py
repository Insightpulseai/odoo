# -*- coding: utf-8 -*-
{
    "name": "IPAI n8n Connector",
    "version": "18.0.1.0.0",
    "category": "Technical/Integrations",
    "summary": "Workflow automation integration with n8n",
    "description": """
IPAI n8n Connector
==================

Connects Odoo to n8n for workflow automation and orchestration.

Features:
---------
* n8n API client for workflow management
* Webhook endpoints for n8n triggers
* Outbound webhook calls to n8n
* Workflow execution tracking
* Credential management (references only)

Architecture:
-------------
This module provides the n8n-specific API client and webhook handlers.
For the admin UI, see ipai_integrations module.

External Service:
-----------------
n8n runs in ipai-ops-stack (NOT vendored here):
* URL: https://n8n.insightpulseai.net
* API: n8n REST API

Workflow Storage:
-----------------
Workflow JSON exports are stored in the ops repo:
* ipai-ops-stack/n8n/workflows/*.json

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
        "views/n8n_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
