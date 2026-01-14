# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════════════════
# ipai_hello - Sample InsightPulse AI Module
# ═══════════════════════════════════════════════════════════════════════════════
# Purpose: Template for ipai_* modules following Smart Delta conventions
# License: AGPL-3 (OCA standard)
# ═══════════════════════════════════════════════════════════════════════════════

{
    'name': 'InsightPulse AI - Hello World',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Sample ipai_* module template',
    'description': """
InsightPulse AI - Hello World Module
====================================

This is a template module demonstrating the Smart Delta pattern:
- Extends core Odoo models via _inherit (not replace)
- Uses OCA conventions for structure
- Ready for marketplace deployment

Enterprise Feature Parity: N/A (template only)
    """,
    
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    
    'depends': [
        'base',
        'web',
    ],
    
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/menu.xml',
    ],
    
    'demo': [],
    
    'installable': True,
    'application': False,
    'auto_install': False,
    
    # OCA metadata
    'maintainers': ['jgtolentino'],
    'development_status': 'Alpha',
}
