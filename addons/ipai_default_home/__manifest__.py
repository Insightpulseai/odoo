# -*- coding: utf-8 -*-
{
    'name': 'InsightPulse Default Home Page',
    'version': '18.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Set default landing page to Project view after login',
    'description': """
Default Home Page Configuration
================================

Automatically redirects users to Project view (/odoo/project) after login.

Features:
---------
* Configures default home action to Project application
* Works for all users
* Overrides Odoo's default home page behavior
* No user action required

Configuration:
--------------
After installation, all users will land on Project view after login.

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
