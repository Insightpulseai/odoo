# -*- coding: utf-8 -*-
{
    'name': 'IPAI Copilot Actions',
    'version': '19.0.1.0.0',
    'summary': 'AI job state, server actions, automation rules, and approval gates',
    'category': 'Productivity',
    'license': 'LGPL-3',
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'depends': [
        'base',
        'mail',
        'base_automation',
        'ipai_odoo_copilot',
    ],
    'data': [
        'security/copilot_actions_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/ir_actions_server.xml',
        'views/ai_job_views.xml',
        'views/ai_proposal_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
}
