# -*- coding: utf-8 -*-
{
    "name": "IPAI Expense OCA Wiring",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Expenses",
    "summary": "Boundary hardening and adjacent OCA module wiring for the expense stack",
    "description": """
IPAI Expense OCA Wiring
=======================

Composition formalization module — not a rewrite.

This module:

* Documents layer ownership boundaries for the expense stack (CE / OCA / delta / bridge)
* Wires adjacent OCA modules (dms, auditlog, queue_job) into the expense flow
  using soft/graceful integration — no hard dependency on optional OCA modules
* Provides computed detection fields for installed OCA modules
* Adds DMS receipt archive reference to hr.expense.sheet with graceful no-op
  when dms is absent

Architecture:
  - CE ``hr_expense`` is the base expense-execution surface
  - OCA hr-expense modules are the extension path (advance clearing, payment, tier-validation)
  - This module wires adjacent OCA infrastructure without creating hard deps
  - Custom delta (ipai_hr_expense_liquidation, ipai_expense_ops) owns PH-specific logic only

Wired OCA modules (soft/graceful):
  - ``dms`` + ``dms_field`` — receipt archival reference on expense reports
  - ``auditlog`` — change audit trail for hr.expense.sheet and cash.advance
  - ``queue_job`` — async OCR pipeline via ipai_document_intelligence

Boundary documentation:
  Records are pre-loaded for all layers so the proven/declared/candidate
  coverage matrix lives in the DB and can be queried/extended at runtime.

Author: InsightPulse AI
License: LGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "hr_expense",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/expense_boundary_doc_views.xml",
        "data/expense_parity_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
