# -*- coding: utf-8 -*-
{
    "name": "IPAI Work OS Core",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "summary": "Notion-style Work OS - Core module with workspaces, spaces, and pages",
    "description": """
        Work OS Core provides the foundation for a Notion-like experience:
        - Workspaces as top-level containers
        - Spaces for organizing content within workspaces
        - Pages with nested page support (tree structure)
        - Sidebar navigation with page tree
        - Integration with blocks, databases, and other Work OS modules
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulse.ai",
    "license": "AGPL-3",
    "icon": "fa-cube",
    "depends": [
        "base",
        "web",
        "mail",
        "ipai_platform_permissions",
        "ipai_platform_audit",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/workspace_views.xml",
        "views/space_views.xml",
        "views/page_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_workos_core/static/src/scss/workos_core.scss",
            "ipai_workos_core/static/src/js/sidebar.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
    "sequence": 10,
}
