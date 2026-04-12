{
    "name": "IPAI Finance PPM (Delta) [DEPRECATED]",
    "version": "18.0.4.0.0",
    "summary": (
        "DEPRECATED — replaced by CE project config"
        " + OCA mis_builder + project OCA modules"
    ),
    "description": """
        DEPRECATED as of 2026-04-11.

        All capabilities are now provided by:
        - CE project (milestones, dependencies, recurring, activities)
        - OCA mis_builder + mis_builder_budget (KPI/budget reports)
        - OCA project_task_stage_state (RAG stage mapping)
        - OCA project_pivot, project_timeline
        - Odoo Documents (evidence vault)
        - Seed data in ipai_finance_ppm_seed

        See docs/architecture/PPM_DASHBOARD_DECOMPOSITION.md
    """,
    "category": "Services/Project",
    "license": "LGPL-3",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    # OCA modules (project_parent, project_milestone_status) are listed here if
    # they are hydrated in addons/oca/. Omitted by default; add back when confirmed
    # present in the deployment addons-path.
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
        "views/ppm_okr_objective_views.xml",
        "views/ppm_okr_key_result_views.xml",
        "views/ppm_import_wizard_views.xml",
        "views/ipai_finance_ppm_menus.xml",
        # data/ir_cron_ppm_sync.xml removed — cron referenced deprecated sync pattern.
        # Budget sync from project to analytic is available via direct method call
        # or future Azure Logic Apps trigger (promotion-lane).
    ],
    "demo": [
        "demo/ipai_finance_ppm_demo_projects.xml",
    ],
    "installable": False,  # DEPRECATED 2026-04-11
    "application": False,
    "auto_install": False,
}
