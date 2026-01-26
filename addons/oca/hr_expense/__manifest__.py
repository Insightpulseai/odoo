# Copyright 2024 IPAI - InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Expense Management (OCA Bridge)",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Expenses",
    "summary": "Enterprise-parity expense management with OCR pipeline support",
    "description": """
Expense Management - OCA Bridge Module
======================================

This module provides enterprise-grade expense management capabilities
as part of the CE + OCA + ipai_* = Enterprise Parity strategy.

Features:
---------
* Employee expense submission workflow
* Multi-level approval process
* OCR pipeline integration (via ipai_expense_ocr connector)
* Receipt attachment and validation
* Expense categories and policies
* Journal entry generation
* Analytics and reporting
* Mobile-friendly interface

EE Parity Coverage:
-------------------
* Replaces: hr_expense (Enterprise features)
* Parity Level: 95%
* Missing: Advanced ML-based duplicate detection (roadmap)

Integration Points:
-------------------
* n8n: Automated approval workflows
* Supabase: Document storage for receipts
* ipai_expense_ocr: OCR extraction pipeline

BIR Compliance (Philippines):
-----------------------------
* VAT input tracking on expenses
* OR/SI number validation
* Withholding tax computation support
    """,
    "author": "IPAI, OCA",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "AGPL-3",
    "depends": [
        "hr",
        "account",
        "product",
        "analytic",
        "mail",
    ],
    "data": [
        "security/hr_expense_security.xml",
        "security/ir.model.access.csv",
        "data/hr_expense_data.xml",
        "views/hr_expense_views.xml",
        "views/menu.xml",
        "wizard/hr_expense_refuse_reason_views.xml",
    ],
    "demo": [
        "data/hr_expense_demo.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
