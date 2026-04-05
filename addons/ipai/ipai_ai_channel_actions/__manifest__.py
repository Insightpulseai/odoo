{
    "name": "IPAI AI Channel Actions",
    "version": "18.0.1.0.0",
    "summary": "Expose Odoo business actions to external channels via Odoo Copilot",
    "description": """
Odoo Copilot — Channel Actions
===============================

Thin adapter module that exposes existing Odoo business actions to external
channels (Slack, Teams) via copilot tools. Uses Odoo's existing mail.activity
system — does not create new approval state machines.

Part of the Odoo Copilot stack (spec/odoo-copilot/).
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "category": "Productivity/AI",
    "license": "LGPL-3",
    "depends": ["base", "mail", "ipai_ai_copilot"],
    "data": [
        "security/ir.model.access.csv",
    ],
    "installable": False,
    "application": False,
    "auto_install": False,
    # DEPRECATED: Replaced by Foundry livechat mode via ipai_odoo_copilot (2026-03-15)
    # See: ssot/governance/ai-consolidation-foundry.yaml
}
