# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.
{
    "name": "IPAI AI RAG",
    "version": "18.0.1.0.0",
    "category": "Productivity/AI",
    "summary": "RAG (Retrieval-Augmented Generation) pipeline for AI agents",
    "description": """
IPAI AI RAG
===========

This module provides the RAG (Retrieval-Augmented Generation) pipeline for AI agents:

- **Source Management**: Ingest files, URLs, and knowledge bases
- **Chunking**: Deterministic text chunking with configurable size and overlap
- **Embeddings**: Vector embeddings via OpenAI API
- **Retrieval**: Cosine similarity search with stable tie-breaking

Features:
- SHA-256 content hashing for deduplication
- Token counting for accurate chunking
- Batch embedding processing
- Configurable retrieval parameters
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": [
        "ipai_ai_agent_builder",
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
