# -*- coding: utf-8 -*-
{
    'name': 'Finance PPM & Tax Compliance',
    'version': '18.0.1.0.0',
    'summary': 'Month-End Closing WBS and Tax Filing Management',
    'description': """
Finance PPM & Tax Compliance Module
====================================
This module provides comprehensive finance project portfolio management
capabilities including:

* BIR Tax Calendar with automated deadline tracking
* Month-end closing workflow with WBS structure
* Finance team directory with role-based assignments
* Canvas dashboards with ECharts visualization
* Preparer/Reviewer/Approver workflow

Key Features:
- Hierarchical task structure (LogFrame)
- Multi-level approval workflow
- Tax deadline compliance tracking
- Customizable dashboard widgets
    """,
    'category': 'Accounting/Finance',
    'author': 'Coding Partner',
    'website': 'https://github.com/your-org/ipai-finance-ppm',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/finance_ppm_data.xml',
        'views/finance_ppm_task_views.xml',
        'views/finance_canvas_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
