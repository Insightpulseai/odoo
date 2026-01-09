# -*- coding: utf-8 -*-
{
    "name": "TBWA Backend Theme (DEPRECATED)",
    "summary": "DEPRECATED - Use ipai_theme_tbwa instead",
    "description": """
TBWA Backend Theme - DEPRECATED
===============================

**THIS MODULE IS DEPRECATED AND SHOULD NOT BE INSTALLED.**

Please use `ipai_theme_tbwa` instead, which provides:
- Simpler architecture (no complex asset hooks)
- Black chrome + Yellow accent
- Clean white/gray surfaces
- No Bootstrap compilation conflicts

To migrate:
1. Uninstall this module: Settings > Apps > ipai_theme_tbwa_backend > Uninstall
2. Install ipai_theme_tbwa: Settings > Apps > ipai_theme_tbwa > Install
3. Clear browser cache and reload
    """,
    "version": "18.0.1.2.0",
    "category": "Themes/Backend",
    "license": "AGPL-3",
    "author": "InsightPulse AI / TBWA Finance",
    "website": "https://insightpulseai.net",
    "depends": [
        "web",
    ],
    "excludes": [
        "web_enterprise",
    ],
    "assets": {},
    "installable": False,
    "application": False,
    "auto_install": False,
}
