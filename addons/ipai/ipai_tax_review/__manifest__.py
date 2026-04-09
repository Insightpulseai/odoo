{
    "name": "IPAI Tax Review",
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "summary": "TaxPulse PH — deterministic invoice validation and review workflow",
    "description": """
        Thin bridge between the TaxPulse PH validation service and Odoo 18.
        Stores validation results, blocks autoposting on failure, and provides
        a review queue for AP/AR exceptions.
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/tax_review_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
