# -*- coding: utf-8 -*-
{
    'name': 'TBWA Brand Token Theme',
    'version': '18.0.2.0.0',
    'summary': 'Applies TBWA Design Tokens with Framer-like Animations & WebGL',
    'description': """
TBWA Brand Token Theme for Odoo 18 Backend
===========================================

This theme module applies TBWA's bold design language to the Odoo backend
using a Design Token approach. It overrides Odoo's primary SCSS variables
to create a cohesive, agency-branded experience.

Features:
- Dark/Bold aesthetic with stark Black/White contrast
- Bold accent colors (Red #E60012, Yellow #FFD100)
- Framer-like micro-animations
- Custom loading screen
- Badge and button styling
- Modern typography with Inter font family

Token-First Approach:
The theme uses SCSS variables (Design Tokens) that propagate throughout
the entire backend, ensuring consistent branding without extensive
component-level overrides.
    """,
    'category': 'Theme/Backend',
    'author': 'Coding Partner',
    'website': 'https://github.com/jgtolentino/odoo-ce',
    'depends': ['web'],
    'assets': {
        # Primary variables are loaded early in the asset pipeline
        'web._assets_primary_variables': [
            'theme_tbwa_backend/static/src/scss/primary_variables.scss',
        ],
        # Backend assets loaded after primary variables
        'web.assets_backend': [
            'theme_tbwa_backend/static/src/scss/backend_overrides.scss',
            'theme_tbwa_backend/static/src/scss/animations.scss',
            'theme_tbwa_backend/static/src/js/ui_animations.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
