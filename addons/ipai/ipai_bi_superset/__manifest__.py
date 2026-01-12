# -*- coding: utf-8 -*-
{
    "name": "IPAI BI Superset",
    "summary": "Thin-layer Superset integration via guest token embedding",
    "description": """
IPAI BI Superset
================

Thin metadata layer for Apache Superset integration:

- Superset Instance configuration (URL, JWT credentials)
- Dataset mapping (Supabase tables exposed to Superset)
- Dashboard registry with embed URLs
- Guest token generation for secure embedding

Architecture:
- Odoo stores metadata + embed URLs only
- Supabase/Superset are the data/BI authority
- No heavy analytics in Odoo

Usage:
1. Configure Superset instance in Settings
2. Register dashboards for embedding
3. Use smart buttons to open filtered dashboards
    """,
    "version": "18.0.1.0.0",
    "category": "Technical",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ipai_bi_security.xml",
        "security/ir.model.access.csv",
        "views/superset_instance_views.xml",
        "views/superset_dataset_views.xml",
        "views/superset_dashboard_views.xml",
        "views/superset_menu.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
