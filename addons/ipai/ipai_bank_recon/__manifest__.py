# -*- coding: utf-8 -*-
{
    'name': 'IPAI Bank Reconciliation Agent',
    'version': '18.0.1.0.0',
    'summary': 'Agentic bank reconciliation with fail-closed governance and evidence-first matching.',
    'category': 'Accounting',
    'license': 'LGPL-3',
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'depends': ['account', 'ipai_bir_tax_compliance'],
    'data': [
        'security/ir.model.access.csv',
        'data/reconciliation_rules.xml',
        'views/bank_statement_line_views.xml',
    ],
    'installable': True,
    'application': True,
}
