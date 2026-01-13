# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing details.

{
    "name": "IPAI SaaS Multi-Tenant",
    "summary": "Multi-tenant provider model for SaaS platform",
    "description": """
Multi-Tenant Provider Model
===========================

This module implements the ideal multi-tenant model where:
- Tenant = organization using the platform
- Provider = organization offering services/agents to other tenants
- Same org can be BOTH tenant and provider

Key Features:
- Account model extending res.company with SaaS-specific fields
- Service catalog for providers
- Subscription management for tenants
- Environment bindings for infrastructure
- RLS-ready tenant isolation

Integrates with:
- Supabase (saas schema)
- Prisma ORM (@ipai/saas-types package)
- InsightPulse AI platform

Data Model:
- saas.account -> extends res.company
- saas.service -> services offered by providers
- saas.service.plan -> pricing tiers
- saas.subscription -> tenant-provider relationships
- saas.environment -> infrastructure bindings
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "category": "Technical",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "security/saas_security.xml",
        "security/ir.model.access.csv",
        "views/saas_account_views.xml",
        "views/saas_service_views.xml",
        "views/saas_subscription_views.xml",
        "views/saas_menu_views.xml",
        "data/saas_data.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
