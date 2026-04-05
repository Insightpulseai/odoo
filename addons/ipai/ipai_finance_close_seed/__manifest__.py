{
    "name": "IPAI Finance Close Seed (TBWA\\SMP)",
    "version": "18.0.2.0.0",
    "summary": "Seed data: 8 projects, 130+ tasks, 6 stages, 60+ tags, 30+ milestones, 17 partners",
    "description": """
Finance PPM — Month-End Close + BIR Tax Filing + Copilot Demo Portfolio
========================================================================

Pure data module. Install to create:

* **6 Kanban stages** (To Do → Done / Cancelled)
* **60+ project tags** (phases, categories, BIR forms, portfolio health,
  copilot skills, artifact types, control plane, finance ops)
* **17 partners** (1 company + 9 team members + 8 vendors)
* **8 projects** (2 core close + AP review + payroll compliance +
  document intelligence + copilot eval + close control plane + artifact pipeline)
* **30+ milestones** (close phases + BIR cadences + portfolio milestones)
* **89 month-end/BIR tasks** + **40+ portfolio tasks** (vendor bills, control
  plane findings, copilot evals, artifact generation, payroll compliance)
* **10 demo prompt tasks** (copilot demonstration catalog)

Portfolio health spread: 2 Green, 3 Amber, 2 Red, 1 At-Risk

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
        "data/08_tags_copilot.xml",
        "data/03_partners_employees.xml",
        "data/09_vendors.xml",
        "data/04_projects.xml",
        "data/10_portfolio_projects.xml",
        "data/05_milestones.xml",
        "data/11_milestones_portfolio.xml",
        "data/06_tasks_month_end.xml",
        "data/07_tasks_bir_tax.xml",
        "data/12_tasks_ap_review.xml",
        "data/13_tasks_control_plane.xml",
        "data/14_tasks_copilot_eval.xml",
        "data/15_demo_prompts.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
