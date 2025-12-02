# -*- coding: utf-8 -*-
{
    "name": "IPAI Tax Shield (Philippines)",
    "version": "18.0.1.0.0",
    "category": "Accounting/Localizations",
    "summary": "BIR 2307 Generator & Alphalist/RELIEF DAT File Engine",
    "description": """
IPAI Tax Shield - Philippines BIR Compliance
=============================================

Provides BIR compliance features for Philippine operations:

* **BIR Form 2307** - Certificate of Creditable Tax Withheld at Source
* **Alphalist/RELIEF Generator** - DAT file export for BIR validation
* **EWT Integration** - Works with OCA account_invoice_tax_witholding

Features:
---------
* QWeb report template matching official BIR 2307 layout
* Server action to generate RELIEF/MAP DAT files
* Automatic withholding tax calculation integration
* ATC (Alphanumeric Tax Code) support

Dependencies:
-------------
* account (Odoo native)
* OCA account-invoicing (for withholding tax logic)
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "reports/bir_2307_report.xml",
        "wizards/bir_dat_file_wizard_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
