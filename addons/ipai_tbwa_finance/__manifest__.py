{
    "name": "IPAI TBWA Finance",
    "summary": "Unified month-end closing + BIR tax compliance for TBWA Philippines",
    "description": """
        Complete finance operations module for TBWA Philippines combining:

        1. MONTH-END CLOSING (SAP AFC Replacement)
           - Template-driven 36-task checklist across 4 phases
           - RACI workflow (Prep → Review → Approve)
           - Holiday-aware workday scheduling
           - Progress tracking dashboards

        2. BIR TAX COMPLIANCE (Philippine Statutory)
           - 36 eBIRForms support (VAT, WHT, Income, Excise)
           - Filing deadline calendar with alerts
           - Auto-compute from Odoo transactions
           - TIN validation

        SHARED COMPONENTS:
           - Philippine holiday calendar (2024-2027)
           - Unified task model with Kanban
           - Single team configuration (BOM, RIM, CKVC)
           - Integrated compliance dashboard

        Cost: Replaces SAP AFC ($500K-1M) + SAP Tax Compliance at zero licensing.
    """,
    "version": "18.0.1.0.0",
    "category": "Accounting",
    "author": "IPAI / TBWA",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ph_holidays.xml",
        "data/month_end_templates.xml",
        "data/bir_form_types.xml",
        "data/compliance_checks.xml",
        "data/ir_cron.xml",
        "views/ph_holiday_views.xml",
        "views/finance_task_views.xml",
        "views/closing_period_views.xml",
        "views/bir_return_views.xml",
        "views/dashboard_views.xml",
        "views/res_partner_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
