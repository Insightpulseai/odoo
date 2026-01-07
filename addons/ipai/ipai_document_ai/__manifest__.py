{
    "name": "IPAI Document AI",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "summary": "Self-hosted OCR and document intelligence for Odoo",
    "description": """
IPAI Document AI
================

Self-hosted document intelligence that replaces Enterprise "Documents AI" features.

Features:
- Document upload and OCR extraction
- Field extraction with confidence scores
- Support for invoices, bills, receipts, contracts
- Review UI for extracted fields
- Apply extracted data to Odoo records

No Odoo SA AI modules or IAP required.

Supported Models:
- account.move (Bills/Invoices)
- hr.expense (Expenses)
- purchase.order (Purchase Orders)

Configuration:
Set environment variables:
- OCR_BASE_URL: OCR service endpoint
- OCR_TIMEOUT_SECONDS: Request timeout
- OCR_MAX_MB: Maximum file size
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "account",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/ipai_document_views.xml",
        "views/menu.xml",
        "data/ir_cron.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_document_ai/static/src/css/document_ai.css",
            "ipai_document_ai/static/src/js/document_upload.js",
            "ipai_document_ai/static/src/xml/document_templates.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
