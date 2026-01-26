# Copyright 2024-2026 InsightPulse AI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Asset Management (OCA Bridge)",
    "summary": "Fixed asset depreciation tracking and reporting",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "InsightPulse AI, OCA",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_asset_views.xml",
        "views/menu.xml",
        "data/asset_category_data.xml",
    ],
    "demo": [
        "data/demo_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
