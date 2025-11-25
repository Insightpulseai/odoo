# -*- coding: utf-8 -*-
{
    'name': 'Finance PPM Transaction Data Ingestion (TDI)',
    'version': '1.0.0',
    'category': 'Finance',
    'summary': 'Import finance team, tasks, BIR calendar, and LogFrame data',
    'description': """
Finance PPM TDI Module
======================
Provides CSV/Excel import wizards for:
- Finance team members (12 employees)
- Month-end closing tasks (50+ tasks across 5 phases)
- BIR filing calendar (24+ forms for 2025-2026)
- LogFrame KPI definitions

Features:
- CSV template generation
- Data validation and error reporting
- Audit trail for all imports
- Integration with ipai_finance_monthly_closing module
    """,
    'author': 'InsightPulse AI - Jake Tolentino',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'project',
        'hr',
        'account',
        # OCA dependencies temporarily disabled for initial deployment
        # 'project_timeline',
        # 'mis_builder',
        # 'purchase_request',
        # 'date_range',
    ],
    'data': [
        # Security ONLY - minimal test to isolate model loading issue
        'security/security_groups.xml',
        'security/ir.model.access.csv',

        # # Seed data (TEMPORARILY DISABLED FOR TESTING)
        # 'data/finance_team_seed.xml',
        # 'data/month_end_tasks_seed.xml',
        # 'data/bir_calendar_seed.xml',
        # 'data/logframe_kpi_seed.xml',
        # 'data/ph_holiday_calendar_seed.xml',

        # # Wizard views (TEMPORARILY DISABLED)
        # 'wizard/finance_ppm_import_wizard_views.xml',

        # # Audit log views (TEMPORARILY DISABLED)
        # 'views/finance_ppm_tdi_audit_views.xml',

        # # Menu (TEMPORARILY DISABLED)
        # 'views/menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
