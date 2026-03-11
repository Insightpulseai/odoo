# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.
{
    "name": "DEPRECATED: AI Fields",
    "version": "19.0.1.0.0",
    "category": "Productivity/AI",
    "summary": "RAG (Retrieval-Augmented Generation) pipeline for AI agents",
    "description": """
AI Fields
=========

AI-powered field population

- **Source Management**: Ingest files, URLs, and knowledge bases
- **Chunking**: Deterministic text chunking with configurable size and overlap
- **Embeddings**: Vector embeddings via OpenAI API
- **Retrieval**: Cosine similarity search with stable tie-breaking

**Features:**
- Core functionality for ai fields
- Integration with Odoo workflows
- Audit logging and compliance

**Configuration:**
- Go to Settings > IPAI > AI Fields

**Credits:**
- InsightPulse AI Team
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        "ipai_ai_core",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ai_source_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
    "external_dependencies": {
        "python": ["tiktoken", "requests"],
    },
}
