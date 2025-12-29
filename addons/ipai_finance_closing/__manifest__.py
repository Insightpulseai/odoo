{
    'name': 'SAP AFC-Style Month-End Closing Template',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Month-end financial closing task template based on SAP Advanced Financial Closing',
    'description': """
SAP AFC-Style Month-End Closing Template
=========================================

This module provides a comprehensive month-end closing task template
based on SAP S/4HANA Cloud for Advanced Financial Closing (AFC) best practices.

Features:
---------
* Pre-configured project template for month-end close
* 25+ closing tasks organized by functional area
* Task dependencies matching SAP AFC workflow
* Tags for GL, AP, AR, Assets, Tax, Reporting
* Automated actions for recurring tasks
* BIR (Philippines) tax compliance tasks

Functional Areas Covered:
------------------------
* Pre-Closing (period management, master data review)
* Accounts Payable (bills, GR/IR, payments, accruals)
* Accounts Receivable (invoices, revenue cutoff, dunning, bad debt)
* Asset Accounting (capitalizations, depreciation, disposals)
* General Ledger (accruals, prepaids, FX revaluation)
* Tax Compliance (BIR 1601-C, 1601-EQ, 2550M/Q)
* Reporting (bank recon, TB, financial statements)

Based on SAP Documentation:
--------------------------
* SAP-docs/s4hana-cloud-advanced-financial-closing (CC-BY-4.0)
* SAP Help Portal - Advanced Financial Closing Administration Guide

No Python Code Required:
-----------------------
This module contains only XML data files and can be installed
without any custom Python development.
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'account',
    ],
    'data': [
        'data/closing_tasks.xml',
        'data/closing_automation.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': [],
}
