# -*- coding: utf-8 -*-
{
    "name": "IPAI WorkOS - Canvas (Edgeless)",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "summary": "Edgeless canvas surface for WorkOS (AFFiNE-style)",
    "description": """
        Canvas module providing an edgeless infinite surface:
        - Pan and zoom navigation
        - Node-based content placement
        - Integration with blocks and pages
        - Collaborative canvas editing
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulse.ai",
    "license": "AGPL-3",
    "depends": ["base", "web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/canvas_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_workos_canvas/static/src/js/canvas_app.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}
