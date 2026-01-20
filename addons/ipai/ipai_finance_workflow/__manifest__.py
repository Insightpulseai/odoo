# -*- coding: utf-8 -*-
# Copyright (C) InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).
{
    "name": "IPAI Finance Workflow",
    "version": "18.0.1.0.0",
    "summary": "Shared finance stages + projects for Month-End Close and BIR workflows.",
    "description": """
IPAI Finance Workflow
=====================

Provides the canonical finance workflow infrastructure:

Projects:
---------
- FIN - Month-End Close (IM1)
- FIN - BIR Returns (IM2)

Normalized Stages:
------------------
- Preparation (PREP)
- Review (REVIEW)
- Approval (APPROVE)
- Execute / File / Pay (EXECUTE)
- Closed / Archived (CLOSE)

Finance Team Roles:
-------------------
- Finance Director (CKVC)
- Senior Finance Manager (RIM)
- Finance Supervisor (BOM)
- Accountants (JPAL, LAS, RMQB, JPL, JI, JO, JM, CJD)

This module serves as the foundation for:
- ipai_finance_month_end
- ipai_finance_bir_compliance
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "category": "Accounting/Project",
    "license": "AGPL-3",
    "depends": [
        "project",
        "mail",
        "hr",
        "ipai_workspace_core",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/finance_roles.xml",
        "data/finance_task_stages.xml",
        "data/finance_projects.xml",
        "data/finance_team.xml",
        "views/finance_role_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
