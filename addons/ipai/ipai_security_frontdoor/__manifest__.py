# -*- coding: utf-8 -*-
{
    "name": "IPAI Front Door Security",
    "version": "19.0.1.0.0",
    "category": "Hidden",
    "summary": "Validates X-Azure-FDID header at the WSGI level to prevent WAF bypass",
    "description": """
Blocks direct access to the Azure Container App URL by validating
the X-Azure-FDID header injected by Azure Front Door. Requests
without a matching FDID are rejected with 403 Forbidden.

Health probe paths (/web/health) are exempt to prevent ACA from
restarting the container due to failed liveness checks.

Set AZURE_FRONTDOOR_ID env var to enable. When unset, the check
is skipped (safe for local dev).
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["base"],
    "installable": True,
    "auto_install": False,
}
