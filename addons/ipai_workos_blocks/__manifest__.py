# -*- coding: utf-8 -*-
{
    "name": "IPAI Work OS Blocks",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "summary": "Notion-style block editor for pages",
    "description": """
        Block editor providing Notion-like content editing:
        - Block types: paragraph, heading, lists, todo, toggle, divider, quote, callout
        - Slash command menu for quick block insertion
        - Drag and drop block reordering
        - Block content stored as structured JSON
        - OWL-based editor surface
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulse.ai",
    "license": "AGPL-3",
    "icon": "fa-th",
    "depends": [
        "base",
        "web",
        "ipai_workos_core",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/block_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_workos_blocks/static/src/scss/block_editor.scss",
            "ipai_workos_blocks/static/src/js/block_editor.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}
