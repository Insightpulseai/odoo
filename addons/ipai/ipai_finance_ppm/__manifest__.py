{
    "name": "IPAI Finance PPM (Delta)",
    "version": "18.0.2.0.0",
    "summary": "Portfolio finance delta — budget, health, risk, scoring, gate reviews",
    "description": """
        Finance-portfolio delta addon for Clarity PPM equivalence.

        CE + OCA provide the project execution and governance base.
        This module adds only what CE/OCA do not cover:
        - Budget vs forecast vs actual per project per period
        - Portfolio health / RAG status
        - Risk register
        - Issue register
        - Investment scoring / prioritization
        - Phase-gate review governance

        See spec/ppm-clarity-plane-odoo/ for architecture doctrine.
    """,
    "category": "Services/Project",
    "license": "LGPL-3",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "depends": [
        "project",
        "account",
        "analytic",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/project_project_views.xml",
        "views/account_analytic_account_views.xml",
        "views/ppm_budget_line_views.xml",
        "views/ppm_portfolio_health_views.xml",
        "views/ppm_risk_views.xml",
        "views/ppm_issue_views.xml",
        "views/ppm_scoring_views.xml",
        "views/ppm_gate_review_views.xml",
        "views/ppm_import_wizard_views.xml",
        "views/ipai_finance_ppm_menus.xml",
        "data/ir_cron_ppm_sync.xml",
    ],
    "demo": [
        "demo/ipai_finance_ppm_demo_projects.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
