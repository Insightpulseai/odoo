# Copyright 2024-2026 InsightPulse AI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Bank Reconciliation (OCA Bridge)",
    "summary": "Automatic bank statement reconciliation with matching proposals",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "InsightPulse AI, OCA",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "account",
        "account_statement_import",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_reconcile_views.xml",
        "views/menu.xml",
    ],
    "demo": [
        "data/demo_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "external_dependencies": {
        "python": [],
    },
}
