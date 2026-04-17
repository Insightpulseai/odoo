# -*- coding: utf-8 -*-
{
    'name': 'IPAI Document Intelligence',
    'version': '18.0.1.0.0',
    'summary': 'Azure Document Intelligence bridge — invoice/receipt/form extraction to Odoo records',
    'description': """
Replaces Odoo IAP document digitization with Azure Document Intelligence.

Features:
- Upload PDF/image → extract fields via Azure DocAI prebuilt-invoice model
- Auto-create vendor bills (account.move) from extracted data
- Auto-classify VAT 12% and EWT (2%/10%) from vendor type
- Confidence-based routing: auto-create (>90%) or review queue (<90%)
- Support for TBWA custom forms via DocAI custom models (future)
- Managed Identity auth (no API keys in code)

Replaces: Odoo IAP document digitization (paid per-scan cloud OCR)
DocAI resource: docai-ipai-dev (Southeast Asia)
    """,
    'category': 'Accounting',
    'license': 'LGPL-3',
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'depends': ['base', 'account', 'mail'],
    'external_dependencies': {
        'python': [
            'requests',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
