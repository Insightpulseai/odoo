# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "IPAI Pulser Connector",
    "version": "19.0.1.0.0",
    "summary": "Claim and execute Pulser intents from Supabase ops.taskbus_intents",
    "description": """
IPAI Pulser Connector
=====================

Bridges the Pulser control plane (Supabase) with Odoo execution surface.

Data flow:
  Pulser (Slack/API) → ops.taskbus_intents (Supabase)
  → ipai_pulser_connector claims odoo.* intents via RPC
  → Odoo executes (read-only MVP: healthcheck, modules.status, config.snapshot)
  → writes result back to ops.taskbus_intents

Configuration (env vars — NOT committed to git):
  SUPABASE_URL             — Supabase project URL
  SUPABASE_SERVICE_ROLE_KEY — Supabase service role key (RLS bypass)

Contract: docs/contracts/C-PULSER-ODOO-01.md
SSOT: ssot/secrets/registry.yaml (supabase_url, supabase_service_role_key)
    """,
    "category": "Tools",
    "license": "LGPL-3",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
