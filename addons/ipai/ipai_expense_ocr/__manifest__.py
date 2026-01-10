{
    "name": "IPAI Expense OCR",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Expenses",
    "summary": "OCR-powered receipt scanning for expense management",
    "description": """
IPAI Expense OCR
================

Self-hosted OCR integration for expense receipt scanning and field extraction.

Features:
- Scan receipts from expense forms
- Auto-extract merchant, date, amount, tax
- Duplicate receipt detection (SHA256 hash)
- Confidence scores for extracted fields
- Queue-based async processing
- Full-text search on OCR content

No Odoo SA AI modules or IAP required.

Extracted Fields:
- merchant_name
- receipt_date
- total_amount
- currency
- tax_amount
- payment_method (optional)
- line_items (optional, feature flag)

Configuration:
Set environment variables:
- OCR_BASE_URL: OCR service endpoint
- OCR_TIMEOUT_SECONDS: Request timeout
- EXPENSE_OCR_DUPLICATE_DAYS: Days to check for duplicates (default: 90)
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "hr_expense",
        "ipai_document_ai",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/hr_expense_views.xml",
        "views/expense_ocr_views.xml",
        "data/ir_cron.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_expense_ocr/static/src/css/expense_ocr.css",
            "ipai_expense_ocr/static/src/js/expense_ocr.js",
            "ipai_expense_ocr/static/src/xml/expense_ocr_templates.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
