# -*- coding: utf-8 -*-
{
    "name": "IPAI Ask AI",
    "summary": "ERP-aware RAG Engine for Finance and Month-End Close workflows",
    "description": """
IPAI Ask AI - Finance RAG Engine
================================

This module provides an AI-powered question-answering system specifically
tuned for Finance and Month-End Close (AFC) workflows.

Features:
---------
- Context-aware AI responses using RAG (Retrieval-Augmented Generation)
- Finance task context injection
- Deadline and compliance awareness
- Integration with LLM providers (OpenAI, Azure OpenAI)
- Conversation history tracking

Capabilities:
-------------
- "What's blocking the close?" - Summarizes overdue tasks by owner
- "Explain this variance" - Analyzes accounting data
- "What are today's priorities?" - Lists urgent tasks

Technical:
----------
- Uses AFC RAG Service for context retrieval
- Supports multiple LLM backends
- Caches frequent queries for performance
    """,
    "version": "18.0.1.0.0",
    "category": "Productivity/AI",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_ask_ai",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "project",
        "ipai_finance_ppm",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ask_ai_views.xml",
        "views/ask_ai_menus.xml",
        "data/ai_config.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_ask_ai/static/src/js/ask_ai_chat.js",
            "ipai_ask_ai/static/src/xml/ask_ai_chat.xml",
            "ipai_ask_ai/static/src/css/ask_ai.css",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
