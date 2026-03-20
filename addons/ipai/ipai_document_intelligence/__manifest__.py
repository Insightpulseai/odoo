# -*- coding: utf-8 -*-
{
    'name': 'IPAI Document Intelligence Bridge',
    'version': '19.0.1.0.0',
    'summary': 'Azure Document Intelligence OCR, extraction, and classification bridge',
    'category': 'Productivity',
    'license': 'LGPL-3',
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'depends': [
        'base',
        'mail',
        'ipai_enterprise_bridge',
        'ipai_copilot_actions',
    ],
    'external_dependencies': {
        'python': ['requests'],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'views/ocr_result_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
}
