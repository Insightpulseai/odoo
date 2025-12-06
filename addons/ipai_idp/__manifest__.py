# -*- coding: utf-8 -*-
{
    "name": "IPAI Intelligent Document Processing (IDP)",
    "summary": "OCR + LLM-based document extraction with versioned models and human review.",
    "description": """
IPAI IDP - Intelligent Document Processing Engine
==================================================

Enterprise-grade IDP service that converts messy documents into clean,
validated, analytics-ready structured records.

Features:
---------
* Multi-document type support (invoices, receipts, POs, delivery notes)
* LLM-based extraction with versioned prompts/models
* Confidence scoring and auto-approval logic
* Human-in-the-loop review for low-confidence extractions
* Validation rules engine
* Health/liveness/readiness endpoints
* Comprehensive audit logging

Architecture:
-------------
Upload -> OCR -> Classify -> LLM Extract -> Validate -> Auto-approve/Review -> Export

Compliant with OCA guidelines. No Odoo Enterprise dependencies.
    """,
    "version": "18.0.1.0.0",
    "category": "Document Management",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/idp_model_versions_data.xml",
        "views/idp_document_views.xml",
        "views/idp_extraction_views.xml",
        "views/idp_model_version_views.xml",
        "views/idp_review_views.xml",
        "views/idp_menus.xml",
    ],
    "assets": {},
    "installable": True,
    "application": True,
    "auto_install": False,
}
