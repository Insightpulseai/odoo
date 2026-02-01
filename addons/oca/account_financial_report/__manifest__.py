# Copyright 2024-2026 InsightPulse AI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Financial Reports (OCA Bridge)",
    "summary": "Generate trial balance, P&L, balance sheet with drill-down",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "InsightPulse AI, OCA",
    "website": "https://insightpulseai.com",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/financial_report_views.xml",
        "views/menu.xml",
        "report/report_templates.xml",
        "data/report_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
