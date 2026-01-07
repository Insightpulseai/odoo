# -*- coding: utf-8 -*-
{
    "name": "IPAI UI Brand Tokens",
    "version": "18.0.1.0.0",
    "category": "Themes",
    "summary": "Single source of truth for brand tokens (Odoo + React)",
    "description": """
IPAI UI Brand Tokens
====================

This module provides a **single source of truth** for brand design tokens that can
be consumed by both Odoo (via CSS variables) and React apps (via JSON API).

Key Features
------------
- Per-company brand token configuration
- JSON API endpoint: GET /ipai/ui/tokens.json?company_id=X
- CSS variables injection for Odoo backend
- TBWA brand preset (black/yellow) as default
- Light/dark theme support

Token Categories
----------------
- palette.primary, palette.accent
- surface.bg, surface.card
- text.primary, text.muted
- radius.sm, radius.md, radius.lg
- shadow.sm, shadow.md, shadow.lg
- typography.fontFamily, typography.fontSizes

Usage
-----
Odoo: Reference tokens via CSS variables:
    background: var(--tbwa-primary);
    color: var(--tbwa-text-primary);

React: Fetch tokens from API:
    fetch('/ipai/ui/tokens.json?company_id=1')
    .then(res => res.json())
    .then(tokens => applyToFluentProvider(tokens));

Settings
--------
Configure brand tokens at: Settings → Companies → Brand Tokens tab
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "LGPL-3",
    "depends": [
        "web",
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "data/token_defaults.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_ui_brand_tokens/static/src/scss/tokens_inject.scss",
            "ipai_ui_brand_tokens/static/src/js/tokens_boot.js",
        ],
        "web.assets_frontend": [
            "ipai_ui_brand_tokens/static/src/scss/tokens_inject.scss",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
