# -*- coding: utf-8 -*-
{
    "name": "IPAI OCA Must-Have Meta",
    "version": "19.0.1.0.0",
    "category": "Hidden",
    "summary": "Meta-module installing all OCA Must-Have modules (no CE19 overlap)",
    "description": """
        Meta-module for one-command installation of all OCA Must-Have modules.

        Explicitly excludes modules absorbed into Odoo 19 CE core:
        - web_advanced_search (CE17+ core search)
        - mail_activity_plan (CE17+ core activity planning)

        Install: odoo-bin -i ipai_oca_musthave_meta
        Total modules: 67 (69 candidates - 2 exclusions)

        Categories:
        - Base: 26 modules (server-tools, web, queue)
        - Accounting: 18 modules (financial tools, reporting)
        - Sales: 11 modules (workflow, management)
        - Purchases: 12 modules (procurement, workflows)

        Governance:
        - Constitution: spec/oca-musthave-no-ce19-overlap/constitution.md
        - Decision Matrix: docs/oca/musthave/decision_matrix.md
        - Install Sets: docs/oca/musthave/install_sets.yml

        Version Policy:
        - Odoo Version: 19.0
        - OCA Branches: 19.0
        - Review: Quarterly (or when CE20 approaches)
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        # Generated from install_sets.yml → musthave_all (67 modules)
        # Source: spec/oca-musthave-no-ce19-overlap/
        # Generator: Phase 4 (2026-02-15)

        # ===== Base Category (26 modules) =====

        # Server Tools
        "base_technical_features",
        "base_search_fuzzy",
        "base_exception",
        "base_tier_validation",
        "base_user_role",
        "base_jsonify",
        "base_sparse_field",
        "base_suspend_security",
        "base_custom_info",
        "base_menu_visibility_restriction",
        "base_technical_user",
        "base_fontawesome",
        "base_import_async",

        # Queue
        "queue_job",

        # Web Widgets & Tools
        "web_widget_x2many_2d_matrix",
        # web_advanced_search EXCLUDED (CE17+ core search)
        # mail_activity_plan EXCLUDED (CE17+ core activity planning)
        "web_refresher",
        "web_domain_field",
        "web_pwa_oca",
        "web_notify",
        "web_m2x_options",
        "web_responsive",
        "web_timeline",
        "web_widget_digitized_signature",
        "web_dialog_size",
        "web_search_with_and",
        "web_ir_actions_act_multi",

        # ===== Accounting Category (18 modules) =====

        "account_fiscal_year",
        "account_move_line_purchase_info",
        "account_move_line_sale_info",
        "account_invoice_refund_link",
        "account_usability",
        "account_payment_partner",
        "account_tag_menu",
        "account_type_menu",
        "account_move_tier_validation",
        "account_statement_import",
        "account_lock_to_date",
        "account_invoice_constraint_chronology",
        "account_cost_center",
        "account_journal_lock_date",
        "account_reconcile_oca",
        "account_invoice_view_payment",
        "account_chart_update",
        "account_financial_report",

        # ===== Sales Category (11 modules) =====

        "sale_automatic_workflow",
        "sale_exception",
        "sale_tier_validation",
        "sale_order_type",
        "sale_order_invoicing_grouping_criteria",
        "sale_order_line_date",
        "sale_delivery_state",
        "sale_stock_mto_as_mts_orderpoint",
        "sale_order_priority",
        "sale_force_invoiced",
        "sale_validity",

        # ===== Purchases Category (12 modules) =====

        "purchase_exception",
        "purchase_tier_validation",
        "purchase_order_type",
        "purchase_order_line_price_history",
        "purchase_order_secondary_unit",
        "purchase_last_price_info",
        "purchase_work_acceptance",
        "purchase_landed_cost",
        "purchase_discount",
        "purchase_order_analytic",
        "purchase_order_approved",
        "purchase_security",
    ],
    "data": [],
    "installable": True,
    "auto_install": False,
    "application": False,
}
