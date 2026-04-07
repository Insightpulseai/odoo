{
    'name': 'IPAI Google Workspace Add-on Backend',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Backend API for W9 Studio Google Workspace Add-on (Gmail + Calendar)',
    'description': """
Google Workspace Add-on Backend for Odoo 18
=============================================

Provides REST endpoints consumed by the Google Workspace Add-on
(deployed via Google Cloud, card-based UI).

Capabilities:
* Gmail sidebar — view/create CRM leads from email context
* Calendar sidebar — check W9 Studio availability, create bookings
* Webhook receiver — Google Workspace event subscriptions
* Dual-identity auth — Google ID token → Odoo session mapping

Architecture: Full dev (not Apps Script). Card JSON returned from
Odoo controllers, rendered by Google Workspace Add-on framework.

Ref: docs/architecture/gmail-addon-architecture.md
Ref: docs/product/gmail-addon/
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'license': 'LGPL-3',
    'depends': [
        'crm',
        'calendar',
        'mail',
        'website',
        'ipai_odoo_copilot',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/google_workspace_data.xml',
    ],
    'assets': {},
    'installable': True,
    'application': False,
    'auto_install': False,
}
