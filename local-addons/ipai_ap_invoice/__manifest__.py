# -*- coding: utf-8 -*-
{
    'name': 'InsightPulse AI - AP Invoice Agent',
    'version': '1.0.0',
    'category': 'Accounting',
    'summary': 'Autonomous AP Invoice Agent with TaxPulse Compliance',
    'author': 'InsightPulse AI',
    'depends': ['account', 'ipai_taxpulse'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/ipai_deployment_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
