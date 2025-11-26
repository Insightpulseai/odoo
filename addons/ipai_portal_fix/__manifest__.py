# -*- coding: utf-8 -*-
{
    'name': 'IPAI Portal Fix - Website-Free Support',
    'version': '1.0.0',
    'category': 'Hidden',
    'summary': 'Fix portal layout KeyError when Website module is not installed',
    'description': """
IPAI Portal Fix Module
======================
Fixes the KeyError: 'website' that occurs when portal pages are accessed
in finance-only deployments.

This module removes the unnecessary website/SEO metadata block from the portal
layout that causes errors when 'website' context is missing.

Technical Details:
- Removes website.layout's html_data.update block (SEO metadata)
- Controller ensures safe 'website' context for portal operations
- Optimized for finance-only Odoo instances without marketing website
- Zero overhead: removes unused website/publishing code entirely

Author: Jake Tolentino (TBWA Finance SSC)
""",
    'author': 'InsightPulse AI - Jake Tolentino',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': [
        'portal',
        'website',  # Required to override website.layout template
    ],
    'data': [
        'views/portal_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,  # Auto-install when portal is installed
}
