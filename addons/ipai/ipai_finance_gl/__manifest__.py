{
    "name": "IPAI Finance — General Ledger Parity Foundation",
    "version": "18.0.1.0.0",
    "summary": "D365 Finance GL parity overlay: chart-of-accounts, fiscal calendar, "
               "financial dimensions, accounting structures, journals, periodic processes.",
    "description": """
IPAI Finance GL — Wave-01 D365 Finance Parity (Epic #523)
==========================================================

Thin overlay on Odoo CE `account` + selected OCA finance modules to capture the
D365 Finance "General Ledger and Financial Foundation" parity surface as
explicit, queryable parity-mapping records.

This module does NOT re-implement GL behavior. Odoo CE + OCA already provide the
runtime; this module documents the D365-to-Odoo parity, exposes a parity matrix
view, and adds light extensions where CE+OCA composition leaves a gap.

Module type: **overlay** (parity tracking + light extension)

Wave-01 Issue coverage (7 Tasks under Epic #523):
- Define general-ledger parity scope
- Define chart-of-accounts and main-account model
- Define fiscal-calendar model
- Define financial-dimensions and dimension-set model
- Define accounting-structure model
- Define financial-journal model
- Define periodic financial-process model

Anchors:
- CLAUDE.md §"Odoo extension and customization doctrine"
- ssot/benchmarks/parity_matrix.yaml
- docs/architecture/repo-adoption-register.md §F.1 D365 Finance reference surfaces
- ADO Boards Epic #523 D365 Finance Parity
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "category": "InsightPulseAI/Finance",
    "depends": [
        "base",
        # Odoo CE 18 baseline
        "account",
        "analytic",
        # OCA finance (selected; per ssot/odoo/module_install_manifest.yaml)
        "account_financial_report",       # OCA/account-financial-reporting
        "account_journal_lock_date",      # OCA/account-financial-tools
        "mis_builder",                    # OCA/mis-builder (for periodic processes)
    ],
    "data": [
        "security/ipai_finance_gl_security.xml",
        "security/ir.model.access.csv",
        "data/d365_parity_data.xml",
        "views/d365_parity_views.xml",
        "views/menu.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
