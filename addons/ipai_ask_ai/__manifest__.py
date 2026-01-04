# -*- coding: utf-8 -*-
{
    "name": "IPAI Ask AI Assistant",
    "version": "18.0.1.1.0",
    "category": "Productivity/AI",
    "summary": "AI-powered conversational assistant for Odoo",
    "description": """
IPAI Ask AI Assistant
=====================

An integrated AI-powered conversational assistant that:
- Processes natural language business queries
- Accesses database and business logic contextually
- Returns intelligent responses with real-time data
- Uses message-based architecture via Discuss module
- Provides intuitive chat interface
- **AFC RAG Integration** - Semantic search over AFC Close Manager knowledge base

Features:
- Chat window component with real-time messaging
- Integration with discuss.channel for persistence
- Context-aware responses based on current model/view
- Support for business queries (customers, sales, etc.)
- **AFC/BIR Compliance Queries** - Philippine tax filing and financial closing
- **RAG-powered answers** - Retrieval-Augmented Generation using pgvector
- Message threading and history
- Mark as read functionality
- Keyboard shortcuts (ESC to close, Enter to send)

Technical Stack:
- OWL Components for reactive chat UI
- Discuss module integration for message storage
- Custom AI service for response generation
- **AFC RAG Service** - pgvector semantic search with Supabase integration
- SCSS styling with IPAI platform tokens

Theming:
- Uses ipai_platform_theme tokens for consistent branding
- No hardcoded colors - all styling via CSS variables
- Automatically inherits brand colors from theme modules

Dependencies:
- psycopg2 (for Supabase vector search)
- OpenAI API (for embeddings - optional, requires configuration)
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "icon": "fa-robot",
    "depends": [
        "base",
        "web",
        "mail",
        "ipai_platform_theme",  # Token source of truth
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ai_channel_data.xml",
        "data/afc_config_params.xml",
        "views/ask_ai_views.xml",
        "views/res_config_settings_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_ask_ai/static/src/scss/ask_ai.scss",
            "ipai_ask_ai/static/src/js/ask_ai_service.js",
            "ipai_ask_ai/static/src/js/ask_ai_chat.js",
            "ipai_ask_ai/static/src/js/ask_ai_systray.js",
            "ipai_ask_ai/static/src/xml/ask_ai_templates.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
