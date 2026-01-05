# -*- coding: utf-8 -*-
{
    "name": "IPAI Superset Connector",
    "version": "18.0.1.0.0",
    "category": "Reporting/BI",
    "summary": "Embed Superset dashboards in Odoo with guest token authentication",
    "description": """
IPAI Superset Connector
=======================

Integrates Apache Superset BI dashboards into Odoo using the official
Embedded SDK guest token pattern.

Features:
---------
* Guest token authentication (no Superset login required for Odoo users)
* Dashboard mapping with Odoo group-based access control
* Row-Level Security (RLS) scoping by company/region/user
* Token caching to minimize API calls
* Full audit trail of token issuance
* OWL component for seamless backend embedding

Architecture:
-------------
1. Odoo user opens Analytics menu
2. OWL component requests guest token from Odoo controller
3. Controller authenticates with Superset service account
4. Guest token returned with RLS rules applied
5. Superset Embedded SDK renders dashboard in iframe

Configuration:
--------------
Set these System Parameters:
* ipai_superset.base_url - Superset instance URL
* ipai_superset.username - Service account username
* ipai_superset.password - Service account password (use env var)
* ipai_superset.embed_domain - Allowed embed origin

Author: InsightPulse AI
License: LGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_superset_connector",
    "license": "LGPL-3",
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "security/superset_security.xml",
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "views/dashboard_views.xml",
        "views/audit_views.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_superset_connector/static/src/css/superset_embed.css",
            "ipai_superset_connector/static/src/js/superset_embed.js",
            "ipai_superset_connector/static/src/xml/superset_embed.xml",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
