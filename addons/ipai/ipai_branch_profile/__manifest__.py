# -*- coding: utf-8 -*-
{
    'name': 'IPAI Branch Profile',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localization',
    'sequence': 80,
    'summary': 'Operating branch registry for same-TIN BIR branch registrations',
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/branch_seed.xml',
        'views/operating_branch_views.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
