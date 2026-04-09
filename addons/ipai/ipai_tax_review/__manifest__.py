{
    "name": "IPAI Tax Review",
    "version": "18.0.2.0.0",
    "category": "Accounting",
    "summary": "TaxPulse PH — deterministic invoice validation, review workflow, BIR export",
    "description": """
        TaxPulse PH for Odoo 18 — Philippines-first tax and compliance layer.

        Phase 1: Deterministic validation engine bridge, posting blocker
        Phase 2: Multi-company config, kanban queue, override wizard
        Phase 3: AI explanation bridge (Foundry integration)
        Phase 4: BIR export batches, compliance datasets, dashboard
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["account", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "wizards/tax_review_override_wizard_views.xml",
        "views/tax_review_views.xml",
        "views/tax_review_kanban.xml",
        "views/tax_review_report_views.xml",
        "views/account_move_views.xml",
        "views/tax_rule_config_views.xml",
        "views/bir_export_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
