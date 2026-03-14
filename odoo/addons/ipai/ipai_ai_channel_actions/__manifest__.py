{
    "name": "IPAI AI Channel Actions",
    "version": "19.0.1.0.0",
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
    "depends": ["base", "mail", "ipai_ai_copilot"],  # DEPRECATED — migrate to ipai_odoo_copilot (C-30)
    "data": [
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
