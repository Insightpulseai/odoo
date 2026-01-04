# -*- coding: utf-8 -*-
{
    "name": "IPAI Ask AI Chatter (Headless)",
    "version": "18.0.1.1.0",
    "category": "Productivity/AI",
    "summary": "Copilot-style @askai in chatter with async jobs + external executor",
    "description": """
IPAI Ask AI Chatter
===================

Headless AI assistant triggered by @askai in chatter on any record.

Features:
- Type @askai <question> in any record's chatter
- Async processing via OCA queue_job (no UI blocking)
- External executor call (configurable endpoint)
- Response posted back to chatter as a message
- Request audit trail (database model)

Configuration (System Parameters):
- ipai_ask_ai_chatter.enabled: True/False
- ipai_ask_ai_chatter.api_url: External executor URL
- ipai_ask_ai_chatter.api_key: Bearer token (optional)
- ipai_ask_ai_chatter.trigger: Trigger token (default: @askai)
- ipai_ask_ai_chatter.context_messages: Context depth (default: 12)
- ipai_ask_ai_chatter.timeout_seconds: HTTP timeout (default: 30)

Dependencies:
- OCA queue_job for async processing (add OCA/queue submodule)
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "icon": "fa-comments",
    "depends": [
        "base",
        "mail",
        # "queue_job",  # TODO: Add OCA/queue submodule to external-src
    ],
    "data": [
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
