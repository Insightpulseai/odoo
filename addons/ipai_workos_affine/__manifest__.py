# -*- coding: utf-8 -*-
{
    "name": "IPAI WorkOS - AFFiNE Clone (Umbrella)",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "summary": "Installs the full WorkOS AFFiNE-style suite",
    "description": """
        Umbrella module that installs the complete Work OS suite providing
        AFFiNE/Notion-like functionality:
        - Pages with nested hierarchy
        - Block-based content editing
        - Databases with typed properties
        - Multiple view types (Table, Kanban, Calendar)
        - Edgeless canvas surface
        - Collaboration features
        - Global search
        - Templates
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulse.ai",
    "license": "AGPL-3",
    "depends": [
        "ipai_workos_core",
        "ipai_workos_blocks",
        "ipai_workos_db",
        "ipai_workos_views",
        "ipai_workos_collab",
        "ipai_workos_search",
        "ipai_workos_templates",
        "ipai_workos_canvas",
        "ipai_platform_permissions",
        "ipai_platform_audit",
    ],
    "data": [],
    "installable": True,
    "auto_install": False,
    "application": True,
    "sequence": 5,
}
