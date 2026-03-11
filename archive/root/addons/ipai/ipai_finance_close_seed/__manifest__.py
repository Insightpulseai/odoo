{
    "name": "IPAI Finance Close Seed (TBWA\\SMP)",
    "version": "19.0.1.0.0",
    "summary": "Seed data: 2 projects, 89 tasks, 6 stages, 33 tags, 11 milestones, 9 team members",
    "description": """
Finance PPM — Month-End Close + BIR Tax Filing
================================================

Pure data module. Install to create:

* **6 Kanban stages** (To Do → Done / Cancelled)
* **33 project tags** (5 phases + 19 categories + 9 BIR forms)
* **9 team members** (res.partner + hr.employee)
* **2 projects** (Month-End Close + BIR Tax Filing)
* **11 milestones** (5 closing phases + 4 BIR cadences + 2 outputs)
* **39 month-end closing tasks** (Phases I–V)
* **50 BIR tax filing tasks** (12 months × 3 forms + quarterlies + annuals)

Canonical data source: ``data/seed/finance_ppm/tbwa_smp/``
    """,
    "category": "Services/Project",
    "license": "LGPL-3",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "depends": [
        "project",
        "hr",
    ],
    "data": [
        "data/01_stages.xml",
        "data/02_tags.xml",
        "data/03_partners_employees.xml",
        "data/04_projects.xml",
        "data/05_milestones.xml",
        "data/06_tasks_month_end.xml",
        "data/07_tasks_bir_tax.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
