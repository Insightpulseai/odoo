# -*- coding: utf-8 -*-
{
    "name": "InsightPulse AI - Tenant Core",
    "version": "18.0.1.0.0",
    "category": "Administration",
    "summary": "Multi-tenant platform core for InsightPulse AI",
    "description": """
Multi-Tenant Platform Core
=========================

Provides tenant isolation and metadata management for the InsightPulse AI platform.

Features:
* Tenant metadata and configuration
* Supabase schema mapping
* Superset workspace integration
* Tenant-aware data access
* TBWA client configuration

Architecture:
* One Odoo DB per tenant (e.g., odoo_tbwa, odoo_platform)
* Shared Supabase cluster with schema isolation
* Shared Superset with tenant-specific dashboards
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": ["base", "mail", "web"],
    "data": [
        "security/ir.model.access.csv",
        "data/tenant_seed_data.xml",
        "views/ipai_tenant_views.xml",
        "views/menu.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
