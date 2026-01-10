{
    "name": "IPAI BIR Tax Compliance",
    "summary": "Philippine BIR tax compliance - 36 eBIRForms support",
    "description": """
        Complete Philippine Bureau of Internal Revenue (BIR) tax compliance module.

        Supported Tax Types:
        - VAT (Forms 2550M, 2550Q)
        - Withholding Tax (Forms 1600, 1601-C, 1601-E, 1601-F, 1604-CF)
        - Income Tax (Forms 1700, 1701, 1702)
        - Excise Tax (Forms 2200A, 2200P, 2200T, 2200M, 2200AN)
        - Percentage Tax (Forms 2551M, 2551Q)
        - Capital Gains Tax (Forms 1706, 1707)
        - Documentary Stamp Tax (Forms 2000, 2000-OT)

        Features:
        - Automated tax computation from Odoo transactions
        - Filing deadline calendar with alerts
        - Form generation wizards
        - Compliance dashboard
        - TIN validation
        - Audit trail
    """,
    "version": "18.0.1.0.0",
    "category": "Accounting/Localizations",
    "author": "IPAI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "account",
        "project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/bir_tax_rates.xml",
        "data/bir_filing_deadlines.xml",
        "data/ir_cron.xml",
        "views/bir_tax_return_views.xml",
        "views/bir_vat_views.xml",
        "views/bir_withholding_views.xml",
        "views/bir_dashboard_views.xml",
        "views/res_partner_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
