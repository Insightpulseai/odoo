# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing.
{
    "name": "InsightPulse: PH Payroll & BIR Compliance",
    "summary": "Philippine payroll with SSS, PhilHealth, Pag-IBIG, and BIR TRAIN Law",
    "description": """
        Smart Delta module providing Enterprise Edition payroll parity for Philippines.

        FEATURES:
        - 2025 SSS contribution tables (15% total: 5% EE, 10% ER)
        - 2025 PhilHealth premium rates (5% total, max PHP 100,000 base)
        - 2025 Pag-IBIG contribution rates (4% total: 2% each)
        - BIR TRAIN Law withholding tax tables
        - Integration with ipai_bir_tax_compliance for 1601-C, 2316

        REPLACES:
        - hr_payroll (Odoo Enterprise)
        - l10n_ph_payroll (Enterprise localization)

        EXTENDS:
        - ipai_bir_tax_compliance (BIR forms integration)

        2025 COMPLIANCE:
        - SSS Circular 2024-001 (new contribution rates)
        - PhilHealth Circular 2024-0009 (5% premium rate)
        - Pag-IBIG Fund guidelines
        - BIR RR 11-2018 (TRAIN Law tax tables)
    """,
    "version": "19.0.1.0.0",
    "category": "Human Resources/Payroll",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        # Core
        "base",
        "mail",
        # HR modules
        "hr",
        "hr_contract",
        "hr_attendance",
        "hr_holidays",
        # IPAI integration
        "ipai_bir_tax_compliance",
    ],
    "external_dependencies": {
        "python": ["pandas"],
    },
    "data": [
        # Security
        "security/ir.model.access.csv",
        "security/payroll_security.xml",
        # Views
        "views/hr_payslip_views.xml",
        "views/menu.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "ipai_hr_payroll_ph/static/src/**/*",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
