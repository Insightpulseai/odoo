# -*- coding: utf-8 -*-
{
    "name": "IPAI Ask AI Chatter",
    "summary": "Integrate Ask AI into Odoo Chatter for contextual AI assistance",
    "description": """
IPAI Ask AI Chatter Integration
===============================

This module integrates the Ask AI functionality directly into Odoo's Chatter
(messaging thread) on documents like Invoices, Tasks, and Expenses.

Features:
---------
- "Ask AI" button in Chatter widget
- Context-aware responses based on current document
- Conversation history linked to specific records
- Quick action suggestions

Usage:
------
1. Open any document with Chatter (Invoice, Task, Expense, etc.)
2. Click the "Ask AI" sparkle icon in the Chatter header
3. Ask questions about the current document
4. AI uses document context for relevant answers
    """,
    "version": "18.0.1.0.0",
    "category": "Productivity/AI",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_ask_ai_chatter",
    "license": "AGPL-3",
    "depends": [
        "mail",
        "ipai_ask_ai",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ask_ai_chatter_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_ask_ai_chatter/static/src/js/ask_ai_chatter.js",
            "ipai_ask_ai_chatter/static/src/xml/ask_ai_chatter.xml",
            "ipai_ask_ai_chatter/static/src/css/ask_ai_chatter.css",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
