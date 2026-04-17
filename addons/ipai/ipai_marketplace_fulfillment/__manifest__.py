{
    'name': 'IPAI Microsoft Marketplace Fulfillment',
    'version': '18.0.1.0.0',
    'category': 'Sales/Subscriptions',
    'summary': 'SaaS Fulfillment API v2 Bridge for Microsoft Commercial Marketplace',
    'description': """
Microsoft Marketplace Fulfillment Bridge
========================================

Implements the SaaS Fulfillment API v2 contract to handle transactable 
SaaS offers on the Microsoft Commercial Marketplace.

Key Features:
* Webhook endpoint: /api/marketplace/webhook
* Automated subscription tracking (Activate, Suspend, Unsubscribe)
* Entra ID alignment for tenant provisioning logic
* Audit logging of all marketplace events

Ref: platform/ssot/integrations/microsoft-marketplace.yaml
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'auth_oauth',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/marketplace_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
