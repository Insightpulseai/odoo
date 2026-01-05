# -*- coding: utf-8 -*-
{
    "name": "IPAI OCR Expense Digitization",
    "summary": "AI-powered receipt scanning and expense digitization",
    "description": """
IPAI OCR Expense Digitization
=============================

This module provides AI-powered document digitalization for expense management:

Features:
---------
- Receipt image upload and OCR scanning
- AI-extracted expense data (Amount, Vendor, Date)
- Confidence scoring for extracted data
- Manual validation workflow for low-confidence extractions
- Integration with ipai_expense and hr_expense modules

Technical:
----------
- Connects to external OCR gateway service
- Supports multiple image formats (PNG, JPG, PDF)
- Async processing with status tracking

Usage:
------
1. Upload a receipt image to an expense record
2. Click "Digitize Receipt (AI)" button
3. Review AI-extracted data
4. Validate or correct extracted fields
    """,
    "version": "18.0.1.0.0",
    "category": "Human Resources/Expenses",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_ocr_expense",
    "license": "AGPL-3",
    "depends": [
        "hr_expense",
        "ipai_expense",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ipai_ocr_expense_views.xml",
        "views/ipai_ocr_expense_menus.xml",
        "data/ocr_config.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
