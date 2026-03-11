{
    "name": "IPAI Ops Mirror (Supabase SSOT)",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "category": "Technical",
    "summary": "Read-only mirror of ops SSOT summaries from Supabase into Odoo",
    "description": """
IPAI Ops Mirror
===============

This module provides read-only cached summaries of operational data
from the Supabase SSOT (Single Source of Truth) into Odoo.

Features:
---------
* Deployment status summary (latest deployment, version, health)
* Incident summary (open incidents, severity, SLA timers)
* Automatic refresh via scheduled cron job
* Circuit breaker pattern for resilience
* Deep links to SSOT artifacts

Architecture:
-------------
* Supabase is the SSOT for ops/artifacts
* Odoo is the System of Record for business data
* This module provides read-only mirror (no write-back)
* Uses HMAC-secured ops-summary Edge Function

Configuration:
--------------
Set these environment variables in the Odoo container:
* IPAI_OPS_SUMMARY_URL: URL of the ops-summary Edge Function
* IPAI_OPS_SUMMARY_HMAC_SECRET: HMAC secret for signing requests
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "data/cron.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
