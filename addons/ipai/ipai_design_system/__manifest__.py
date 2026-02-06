# -*- coding: utf-8 -*-
{
    'name': 'IPAI Design System',
    'version': '19.0.1.0.0',
    'category': 'Hidden/Tools',
    'summary': 'Unified design tokens for IPAI stack (Fluent UI v9 + Copilot)',
    'description': """
IPAI Design System
==================

Provides unified design tokens and components based on:
- Microsoft Fluent UI React v9
- Microsoft Copilot design patterns
- Teams purple (#6264A7) brand color

Features:
- CSS custom properties (tokens) for Odoo backend
- JSON token export for portals and external apps
- Copilot-style components (chat, cards, actions)
- Consistent typography, spacing, shadows, and colors

Usage:
- Odoo: Tokens auto-loaded via web assets
- Portals: Import from /ipai_design_system/static/src/tokens/tokens.json
- React/Next.js: Use exported TypeScript definitions
    """,
    'author': 'InsightPulse AI',
    'website': 'https://jgtolentino.github.io/odoo-ce/',
    'license': 'LGPL-3',
    'depends': ['web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'ipai_design_system/static/src/css/tokens.css',
            'ipai_design_system/static/src/css/components.css',
            'ipai_design_system/static/src/css/copilot.css',
        ],
        'web.assets_frontend': [
            'ipai_design_system/static/src/css/tokens.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    "installable": False,
}