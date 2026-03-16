# -*- coding: utf-8 -*-
{
    "name": "IPAI Platform API",
    "version": "19.0.1.0.0",
    "category": "Website",
    "summary": "REST API bridge for Next.js SaaS landing page",
    "description": """
Platform API Bridge
===================

Provides JSON-RPC API endpoints for the Next.js frontend to:
- Fetch features from Odoo CMS
- Trigger deployments via n8n
- Get deployment logs and metrics
- Manage platform resources

Integration with:
- Next.js frontend (templates/saas-landing/)
- n8n workflows
- MCP task queue
- Supabase authentication
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "website",
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/platform_feature_views.xml",
        "views/platform_deployment_views.xml",
        "data/platform_feature_data.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
