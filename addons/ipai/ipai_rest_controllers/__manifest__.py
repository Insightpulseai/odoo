{
    'name': 'IPAI REST Controllers',
    'version': '19.0.1.0.0',
    'category': 'Technical',
    'summary': 'Native REST API controllers (interim solution until base_rest 19.0)',
    'description': """
Native Odoo REST Controllers
=============================

Provides REST API endpoints using native Odoo HTTP controllers.

This is an interim solution while waiting for OCA base_rest migration to Odoo 19.0.

Features:
---------
* JSON-RPC endpoints for external integrations
* Session and API key authentication
* Request validation and error handling
* Migration path to base_rest documented

TODO: Migrate to base_rest when available
- Monitor OCA/connector for component module 19.0
- Monitor OCA/rest-framework for version bump to 19.0.x
- See docs/architecture/rest_migration_plan.md
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
