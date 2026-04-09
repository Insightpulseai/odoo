{
    "name": "IPAI Finance Close Seed (TBWA\\SMP)",
    "version": "18.0.2.0.0",
    "summary": "Seed data: 8 projects, 130+ tasks, 6 stages, 60+ tags, 30+ milestones, 17 partners",
    "description": """
Finance PPM — Month-End Close + BIR Tax Filing Seed Data
=========================================================

Pure data module. Install to create:

* **3 Month-End stages** (Preparation → Review → Approval)
* **4 BIR stages** (Preparation → Report Approval → Payment Approval → Filing & Payment)
* **40+ project tags** (phases, categories, BIR forms)
* **9 partners** (1 company + 9 team members)
* **2 projects** (Month-End Close + BIR Tax Filing)
* **10 milestones** (5 close phases + 4 BIR cadences + output milestones)
* **89 tasks** (39 month-end + 50 BIR tasks)

Canonical data source: ``data/``
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
