# -*- coding: utf-8 -*-
{
    "name": "IPAI Finance OKR Governance",
    "summary": "OKR + PMBOK + WBS governance for Finance month-end close and tax filing.",
    "version": "18.0.1.0.0",
    "category": "Accounting/Finance",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce/tree/18.0/addons/ipai/ipai_finance_okr",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "project",
        "ipai_finance_ppm",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/okr_objective_views.xml",
        "views/okr_key_result_views.xml",
        "views/okr_risk_views.xml",
        "views/okr_milestone_views.xml",
        "views/menus.xml",
        "data/okr_objective_seed.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
