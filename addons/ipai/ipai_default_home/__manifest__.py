# -*- coding: utf-8 -*-
{
    'name': 'InsightPulse Default Home Page',
    'version': '18.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Set default landing page to Apps Dashboard after login',
    'description': """
Default Home Page Configuration
================================

Automatically redirects users to Apps Dashboard (/odoo) after login - the icon grid view.

Features:
---------
* Shows Apps Dashboard with icon grid (Discuss, Dashboards, Invoicing, Employees, Expenses, Apps, Settings)
* Matches official Odoo behavior
* Works for all users
* No user action required

Configuration:
--------------
After installation, all users will see the Apps Dashboard after login.

Author: InsightPulse AI
License: AGPL-3
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'project',
    ],
    'data': [
        'data/default_home_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
