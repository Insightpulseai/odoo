{
    'name': 'IPAI Month-End Closing & BIR Tax Filing',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'SAP AFC-style month-end closing with BIR tax compliance for TBWA Finance',
    'description': """
IPAI Month-End Closing & BIR Tax Filing
=======================================

Complete month-end financial closing workflow based on SAP Advanced Financial
Closing (AFC) best practices, tailored for TBWA Finance operations.

Features
--------
* 36 pre-configured closing tasks organized by functional area
* Employee assignments mapped to TBWA Finance team (RIM, BOM, JPAL, LAS, JLI, RMQB, JAP, JRMO)
* Three-tier approval workflow: Preparation → Review → Approval
* Task dependencies matching SAP AFC workflow patterns
* BIR tax filing calendar with automated deadlines (1601-C, 1601-EQ, 2550Q, 1702-RT/EX, 1702Q)

Functional Areas
----------------
* Payroll & Personnel
* Tax & Provisions
* Rent & Leases
* Accruals & Expenses
* Prior Period Review
* Amortization & Corporate
* Insurance
* Treasury & Other
* Client Billings & WIP/OOP
* VAT & Taxes
* CA Liquidations
* AR/AP Aging
* Regional Reporting

BIR Compliance
--------------
* Monthly: 1601-C (Compensation), 0619-E (Creditable EWT)
* Quarterly: 1601-EQ (EWT), 2550Q (VAT), 1702Q (Income Tax)
* Annual: 1702-RT/EX (Income Tax Return)

Architecture: Smart Delta
-------------------------
This module follows the ipai_* Smart Delta pattern:
- Extends core Odoo project module
- No monkey-patching or forks
- OCA-compatible, marketplace-ready
- AGPL-3 licensed
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ipai_users.xml',
        'data/project_config.xml',
        'data/ipai_closing_tasks.xml',
        'data/ipai_bir_tasks.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
