# -*- coding: utf-8 -*-
{
    "name": "IPAI Expense OCR",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Expenses",
    "summary": "Auto-extract expense data from receipt attachments via OCR",
    "description": """
IPAI Expense OCR Integration
============================

Automatically extracts expense data from uploaded receipt images/PDFs using
an external OCR service and populates expense fields.

Features:
- Automatic OCR on expense attachment upload
- Extracts: vendor, date, total, tax, currency, line items
- Supports multiple OCR backends (custom endpoint, OpenAI Vision, Gemini)
- Stores raw OCR JSON response for audit
- Manual "Extract from Receipt" button for re-processing

Configuration:
1. Go to Settings → Expenses → OCR Configuration
2. Set your OCR endpoint URL or enable AI provider
3. Upload receipt → fields auto-populate

Supported OCR Backends:
- Custom OCR Service (PaddleOCR-VL, etc.)
- OpenAI GPT-4 Vision
- Google Gemini Vision
- DigitalOcean Model Endpoints (via proxy)
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "hr_expense",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "views/hr_expense_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
