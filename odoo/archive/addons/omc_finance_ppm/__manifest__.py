# -*- coding: utf-8 -*-
{
    'name': 'OMC Finance PPM - Minimal',
    'version': '1.0',
    'category': 'Project Management',
    'summary': 'Minimal Finance PPM - Models Only',
    'license': 'LGPL-3',
    'depends': ['base', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/finance_todo_views.xml',
        'views/project_task_views.xml',
        'data/ppm_seed_finance_wbs_2025_2026.xml',
        'data/ppm_seed_users.xml',
    ],
    'application': True,
    'installable': True,
}
