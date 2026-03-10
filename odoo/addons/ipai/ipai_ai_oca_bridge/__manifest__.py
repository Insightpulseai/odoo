{
    "name": "IPAI AI OCA Bridge",
    "version": "19.0.1.0.0",
    "summary": "Bridges OCA ai_oca_bridge with ipai_ai_core provider system",
    "description": """
Odoo Copilot — OCA Bridge Glue
===============================

Inherits ai.bridge and adds an optional ipai_provider_id field.
When set, executions route through ipai.ai.provider (Supabase Edge)
instead of raw URL POST.

Part of the Odoo Copilot stack (spec/odoo-copilot/).
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "category": "Productivity/AI",
    "license": "LGPL-3",
    "depends": ["ai_oca_bridge", "ipai_ai_core"],
    "data": [
        "security/ir.model.access.csv",
        "views/ai_bridge_views.xml",
        "data/ai_bridge_supabase.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
