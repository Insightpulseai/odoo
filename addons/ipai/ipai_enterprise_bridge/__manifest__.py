# -*- coding: utf-8 -*-
{
    "name": "IPAI Enterprise Bridge",
    "summary": "Thin glue layer for CE+OCA parity: config, approvals, AI/infra integration",
    "version": "18.0.1.0.0",
    "category": "InsightPulse/Core",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_enterprise_bridge",
    "license": "AGPL-3",
    "depends": [
        # CE core platform
        "base",
        "web",
        "mail",
        "contacts",
        # CE business backbone
        "account",
        "sale_management",
        "purchase",
        "stock",
        "project",
        "hr",
        "hr_timesheet",
        # OCA governance baseline (only stable modules)
        "base_tier_validation",
        "base_exception",
        "date_range",
        # IPAI foundation
        "ipai_workspace_core",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/groups.xml",
        "data/sequences.xml",
        "data/scheduled_actions.xml",
        "data/enterprise_bridge_data.xml",
        "views/res_config_settings_views.xml",
        "views/ipai_policy_views.xml",
        "views/ipai_close_views.xml",
        "views/product_views.xml",
        "views/enterprise_bridge_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
}
