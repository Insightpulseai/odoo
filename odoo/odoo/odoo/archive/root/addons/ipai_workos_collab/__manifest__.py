# -*- coding: utf-8 -*-
{
    "name": "IPAI Work OS Collaboration",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "summary": "Comments, mentions, and notifications",
    "description": """
        Collaboration module providing Notion-like features:
        - Comments on pages and database rows
        - @mentions with notifications
        - Activity log for edits/moves/shares
        - Integration with mail module
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulse.ai",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "ipai_workos_core",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/comment_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
