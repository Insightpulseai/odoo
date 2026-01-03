# -*- coding: utf-8 -*-
{
    "name": "IPAI OCR Gateway",
    "version": "18.0.1.0.0",
    "category": "Productivity/Documents",
    "summary": "OCR processing gateway for document text extraction",
    "description": """
IPAI OCR Gateway
================

Production-ready OCR processing module that:
- Queues OCR jobs for async execution
- Supports multiple OCR providers (Tesseract, Google Vision, Azure, custom)
- Stores extracted text in ir.attachment
- Provides health check endpoints

Models:
- ipai.ocr.provider: Provider configuration (name, base_url, auth)
- ipai.ocr.job: OCR job queue (attachment_id, state, result_text, result_json)

Integration:
- Async job queue via ir.cron
- Config via system parameters
- Health endpoint at /ipai/ocr/health
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/ipai_ocr_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
