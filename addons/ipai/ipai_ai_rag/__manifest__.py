# -*- coding: utf-8 -*-
{
    "name": "DEPRECATED: AI RAG Pipeline",
    "version": "19.0.1.0.0",
    "category": "InsightPulse AI",
    "summary": "DEPRECATED - Migrated to ipai_enterprise_bridge. Do not install.",
    "description": """
AI RAG Pipeline
===============

RAG for document-based context retrieval

This module provides Odoo 19 Enterprise Edition parity for CE deployments.

**Features:**
- Core functionality for ai rag pipeline
- Integration with Odoo workflows
- Audit logging and compliance

**Configuration:**
- Go to Settings > IPAI > AI RAG Pipeline

**Credits:**
- InsightPulse AI Team
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": ["ipai_ai_agent_builder"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
    ],
    "demo": [],
    "installable": False,
    "application": False,
    "auto_install": False,
}
