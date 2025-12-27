# -*- coding: utf-8 -*-
{
    "name": "InsightPulse Custom Home Page",
    "version": "18.0.2.0.0",
    "category": "Extra Tools",
    "summary": "Custom app grid home page with modern styling",
    "description": """
Custom Home Page for InsightPulse
=================================

A beautiful, modern app grid home page inspired by Odoo's default design
but with enhanced styling and features.

Features:
---------
* Modern app grid layout with smooth animations
* Hover effects and visual feedback
* Right-click context menu for quick actions
* Keyboard shortcut (Ctrl+K) for app search
* Favorites support
* Responsive design for all screen sizes
* Badge notifications for unread items

Technical Details:
------------------
* Built with OWL (Odoo Web Library)
* CSS Grid for responsive layout
* Client-side caching for performance

Author: InsightPulse AI
License: AGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "web",
        "mail",
    ],
    "data": [
        "data/default_home_data.xml",
        "views/home_action.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_default_home/static/src/css/home_page.css",
            "ipai_default_home/static/src/js/home_page.js",
            "ipai_default_home/static/src/xml/home_page.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
