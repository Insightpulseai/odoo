# -*- coding: utf-8 -*-
{
    'name': 'Finance PPM Go-Live Checklist',
    'version': '18.0.1.0.0',
    'category': 'Finance',
    'summary': 'Production go-live checklist for Finance PPM modules',
    'description': """
Finance PPM Go-Live Checklist Module
====================================

Complete production readiness checklist for Finance PPM system with:
- 9 section groups (Data, Module, AFC, STC, Control Room, Notion, Audit, Operational, Go-Live)
- 60+ granular checklist items
- Approval workflow (Finance Supervisor → Senior Supervisor Finance → Director)
- Dashboard with completion % tracking
- PDF export for Director sign-off
- Integration with Finance PPM modules

Author: Jake Tolentino (InsightPulse AI / TBWA)
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
        'security/ir.model.access.csv',
        'data/checklist_sections.xml',
        'data/checklist_items.xml',
        'views/golive_checklist_views.xml',
        'views/golive_section_views.xml',
        'views/golive_item_views.xml',
        'views/golive_dashboard_views.xml',
        'views/menus.xml',
        'reports/golive_cfo_signoff.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
