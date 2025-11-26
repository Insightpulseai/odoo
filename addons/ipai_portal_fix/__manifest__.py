# -*- coding: utf-8 -*-
{
    'name': 'IPAI Portal Fix',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Fixes KeyError: website in portal.frontend_layout template',
    'description': """
IPAI Portal Fix
===============

Fixes the KeyError: 'website' error in portal.frontend_layout template.

This error occurs when the portal templates try to access the 'website'
variable in the QWeb context, but it's not present. This can happen when:

1. The website module is not installed
2. A route doesn't have website=True set
3. The context is cleared or corrupted

This module fixes the issue by:
1. Injecting a default 'website' context variable when missing
2. Adding defensive checks in template overrides
    """,
    'author': 'InsightPulseAI',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': [
        'portal',
    ],
    'data': [
        'views/portal_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,  # Auto-install when portal is installed
}
