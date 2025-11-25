# -*- coding: utf-8 -*-
{
    'name': 'IPAI Finance AP Aging',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'AP Aging Heatmap Automation for Month-End Close',
    'description': """
AP Aging Automation Module
===========================

Features:
---------
* Automated AP Aging bucket calculations (0-30, 31-60, 61-90, 90+ days)
* Employee-specific context filtering (RIM, CKVC, etc.)
* ECharts heatmap visualization at /ipai/finance/ap_aging/heatmap
* Daily cron job (9 AM PHT) for automated snapshots
* n8n webhook integration for task queue automation
* Mattermost notifications for month-end close reviewers
* Print Report functionality with visual parity validation
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'account',
        'project',
        'ipai_finance_monthly_closing',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ap_aging_cron.xml',
        'views/ap_aging_views.xml',
        'views/ap_aging_menu.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ipai_finance_ap_aging/static/src/xml/heatmap_template.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
