# -*- coding: utf-8 -*-
{
    "name": "IPAI Platform Permissions",
    "version": "18.0.1.0.0",
    "category": "Hidden/Tools",
    "summary": "Scope-based permission and role management for IPAI modules",
    "description": """
        Platform-level permission management providing:
        - Workspace/space/page/db permission scopes
        - Role definitions (admin/member/guest)
        - Record rules generation
        - Share token management
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulse.ai",
    "license": "AGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/permission_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
