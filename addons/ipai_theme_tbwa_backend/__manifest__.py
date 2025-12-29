# -*- coding: utf-8 -*-
{
    'name': 'TBWA Backend Theme',
    'summary': 'TBWA branding for Odoo backend - Black + Yellow + IBM Plex',
    'description': '''
        Applies TBWA corporate identity to Odoo backend:
        - TBWA Yellow (#FFD800) as primary accent
        - Black navbar/sidebar
        - IBM Plex Sans typography
        - Rounded cards matching Scout/InsightPulse design
        
        Can be used standalone OR with MuK Backend Theme.
    ''',
    'version': '18.0.1.0.0',
    'category': 'Themes/Backend',
    'license': 'AGPL-3',
    'author': 'InsightPulse AI / TBWA Finance',
    'website': 'https://insightpulseai.net',
    'depends': [
        'web',
    ],
    'excludes': [
        'web_enterprise',
    ],
    'assets': {
        # Primary variables - MUST load early to override Bootstrap/Odoo vars
        'web._assets_primary_variables': [
            (
                'after',
                'web/static/src/scss/primary_variables.scss',
                'ipai_theme_tbwa_backend/static/src/scss/variables.scss',
            ),
        ],
        # Backend assets - fonts, button fixes, UI tweaks
        'web.assets_backend': [
            'ipai_theme_tbwa_backend/static/src/scss/fonts.scss',
            'ipai_theme_tbwa_backend/static/src/scss/backend.scss',
        ],
        # Dark mode overrides (optional)
        'web.assets_web_dark': [
            (
                'after',
                'ipai_theme_tbwa_backend/static/src/scss/variables.scss',
                'ipai_theme_tbwa_backend/static/src/scss/variables_dark.scss',
            ),
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
