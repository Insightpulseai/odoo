# -*- coding: utf-8 -*-
{
    'name': 'IPAI Platform Theme',
    'version': '18.0.1.0.0',
    'category': 'Theme/Backend',
    'summary': 'Material 3 Expressive + Fluent design tokens for Odoo backend',
    'description': """
IPAI Platform Theme
===================

A modern theming module that implements:
- Material 3 Expressive design tokens
- Fluent Design System patterns
- Claude/OpenAI-inspired clean surfaces
- High contrast typography
- Consistent spacing and radii

This theme provides CSS variables that can be consumed by:
- ipai_ask_ai (AI Copilot)
- Other IPAI modules
- Custom OWL components
    """,
    'author': 'IPAI',
    'website': 'https://ipai.dev',
    'license': 'LGPL-3',
    'depends': ['web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'ipai_platform_theme/static/src/scss/tokens.scss',
            'ipai_platform_theme/static/src/scss/typography.scss',
            'ipai_platform_theme/static/src/scss/surfaces.scss',
            'ipai_platform_theme/static/src/scss/components.scss',
            'ipai_platform_theme/static/src/scss/animations.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
