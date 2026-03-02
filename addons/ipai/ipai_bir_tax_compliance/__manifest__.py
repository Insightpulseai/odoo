{
    "name": "IPAI BIR Tax Compliance",
    "version": "19.0.1.0.0",
    "category": "Accounting/Localizations",
    "summary": "Philippine BIR withholding tax tables, SSS/PhilHealth/Pag-IBIG contribution schedules",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["base", "account"],
    "data": [
        "security/ir.model.access.csv",
        "data/bir_tax_tables_2023.xml",
        "views/bir_tax_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
