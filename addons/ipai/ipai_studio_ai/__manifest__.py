# -*- coding: utf-8 -*-
{
    'name': 'IPAI Studio AI',
    'version': '18.0.1.1.0',
    'category': 'Customization/Studio',
    'summary': 'Natural Language Customization Engine for Odoo',
    'description': """
IPAI Studio AI - Natural Language Customization
================================================

Create Odoo customizations using natural language commands.

Features
--------
* **Field Creation**: "Add a phone number field to contacts"
* **Automations**: "When an invoice is confirmed, send an email"
* **View Modifications**: "Show the status field in the task list view"
* **Smart Detection**: Automatically detects field types, models, and triggers

Supported Commands
------------------
Field Types:
- Text, Number, Date, Selection, Boolean
- Money, Phone, Email, URL
- Relations (Many2one, One2many, Many2many)
- Binary/File uploads

Models:
- Contacts, Sales, Purchases, Invoices
- Projects, Tasks, Employees, Expenses
- Products, Inventory, CRM, Helpdesk

Automations:
- On Create, Update, Delete
- Scheduled (daily, weekly, monthly)
- Conditional triggers with filters

Integration
-----------
Integrates with IPAI AI Assistant for conversational customization.

License: AGPL-3
Author: InsightPulse AI
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'license': 'AGPL-3',
    'depends': [
        'base',
        # 'base_automation',  # TODO: Verify in Odoo 18 CE addons_path
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/studio_ai_data.xml',
        'views/studio_ai_views.xml',
        'views/studio_ai_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ipai_studio_ai/static/src/js/studio_ai_widget.js',
            'ipai_studio_ai/static/src/css/studio_ai.css',
            'ipai_studio_ai/static/src/xml/studio_ai_templates.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
    'images': ['static/description/banner.png'],
}
