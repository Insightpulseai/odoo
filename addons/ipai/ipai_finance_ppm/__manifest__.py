{
    "name": "IPAI Finance PPM (CE)",
    "version": "19.0.1.0.0",
    "summary": "Finance + Project + Analytic controls and import clarity for CE",
    "category": "Services/Project",
    "license": "LGPL-3",
    "depends": [
        "project",
        "account",
        "analytic",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ipai_finance_ppm_menus.xml",
        "views/project_project_views.xml",
        "views/account_analytic_account_views.xml",
        "wizards/ppm_import_wizard_views.xml",
        "data/ir_cron_ppm_sync.xml",
    ],
    "installable": True,
    "application": False,
}
