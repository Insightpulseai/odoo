# -*- coding: utf-8 -*-
{
    "name": "TBWA Spectra Integration",
    "summary": "Integration with Spectra finance system for TBWA.",
    "version": "18.0.1.0.0",
    "category": "Accounting/Finance",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "AGPL-3",
    "depends": [
        "base",
        "account",
        "hr_expense",
    ],
    "data": [
        # Security (must load first)
        "security/tbwa_security.xml",
        "security/ir.model.access.csv",
        # Data files (load after security, before views)
        "data/users_data.xml",
        "data/tbwa_cron.xml",
        "data/spectra_mapping_data.xml",
        "data/approval_matrix_data.xml",
        "data/export_templates_data.xml",
        # Views (load last, comment out until created)
        "views/hr_expense_advance_views.xml",
        "views/spectra_export_views.xml",
        "views/spectra_mapping_views.xml",
        "views/approval_matrix_views.xml",
        "views/tbwa_menu.xml",
        # Wizards (load after views)
        "wizards/spectra_export_wizard_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
}
