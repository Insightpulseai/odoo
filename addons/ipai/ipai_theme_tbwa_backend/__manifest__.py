# -*- coding: utf-8 -*-
{
    "name": "IPAI TBWA Backend Theme",
    "version": "18.0.1.0.0",
    "category": "Themes",
    "summary": "TBWA brand colors applied to ChatGPT SDK design system",
    "description": """
IPAI TBWA Backend Theme
=======================

Applies TBWA brand identity to the ChatGPT App SDK design system.

This module extends `ipai_chatgpt_sdk_theme` by overriding the color
tokens with TBWA brand colors while preserving:

- ChatGPT-style rounded corners and subtle shadows
- Clean, modern typography (system font stack)
- Responsive layouts and spacing
- Chat bubble patterns for AI interactions

TBWA Brand Colors:
------------------
- Primary: TBWA Yellow (#FEDD00)
- Secondary: TBWA Black (#000000)
- Accent: Deep Yellow (#E5C700)
- Background: Clean white with subtle gray tones

Design Philosophy:
------------------
"Disruption" - Bold yellow accents that stand out while maintaining
professional polish and usability.

Usage:
------
Install this module AFTER `ipai_chatgpt_sdk_theme` to apply the
TBWA color scheme. The ChatGPT SDK layout patterns remain intact.
    """,
    "author": "InsightPulse AI / TBWA",
    "website": "https://tbwa.com",
    "license": "AGPL-3",
    "depends": [
        "ipai_chatgpt_sdk_theme",
    ],
    "data": [],
    "assets": {
        # Override primary variables (loaded before Bootstrap)
        "web._assets_primary_variables": [
            ("after", "ipai_chatgpt_sdk_theme/static/src/scss/primary_variables.scss",
             "ipai_theme_tbwa_backend/static/src/scss/tbwa_primary_variables.scss"),
        ],
        # Override design tokens (loaded after base tokens)
        "web.assets_backend": [
            ("after", "ipai_chatgpt_sdk_theme/static/src/scss/tokens.scss",
             "ipai_theme_tbwa_backend/static/src/scss/tbwa_tokens.scss"),
            "ipai_theme_tbwa_backend/static/src/scss/tbwa_backend.scss",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
