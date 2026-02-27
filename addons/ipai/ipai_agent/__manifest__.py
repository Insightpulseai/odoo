# -*- coding: utf-8 -*-
{
    "name": "IPAI Agent Runtime",
    "summary": "Odoo-native UI for triggering and auditing IPAI agent runs via Supabase Edge Functions",
    "description": """
IPAI Agent Runtime
==================
Provides a lightweight Odoo-native surface for:

* Triggering IPAI agent runs (e.g. on expense liquidations, invoices)
* Auditing agent run state, tool calls, and outputs
* Enforcing governance policies (tool allowlists, approval gates)
* Receiving async callbacks from Supabase Edge Functions / MCP via HMAC-secured webhook

Models
------
- ipai.agent.run   — one execution record per agent invocation
- ipai.agent.tool  — registry of permitted tools + auth mode
- ipai.agent.policy — governance defaults per model/company

Security
--------
Three groups: user / approver / admin (see security/security.xml)

Secrets
-------
Endpoint URL and HMAC secret live in ir.config_parameter, never hardcoded.
    """,
    "version": "19.0.1.0.0",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "category": "Technical",
    "depends": [
        "mail",
        "hr_expense",
        "ipai_hr_expense_liquidation",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/ir_cron.xml",
        "data/activity_types.xml",
        "views/agent_run_views.xml",
        "views/agent_tool_views.xml",
        "views/agent_policy_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
