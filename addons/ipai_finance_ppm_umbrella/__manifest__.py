{
    "name": "IPAI Finance PPM – TBWA Complete Configuration",
    "summary": "Complete seed data for 8-employee Finance SSC with BIR compliance and month-end closing tasks",
    "version": "18.0.1.0.0",
    "category": "Accounting/Finance",
    "website": "https://insightpulse.ai",
    "author": "InsightPulse AI",
    "license": "LGPL-3",
    "depends": ["ipai_finance_ppm", "project"],
    "data": [
        "security/ir.model.access.csv",
        "data/01_employees.xml",
        "data/02_logframe_complete.xml",
        "data/03_bir_schedule_2026.xml",
        "data/04_closing_tasks.xml",
        "data/05_raci_assignments.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
    "description": """
TBWA Finance PPM Umbrella Configuration
========================================

Complete seed data for Finance SSC operations:

**8 Employees:**
- RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB

**BIR Tax Forms (22 entries for 2026):**
- 1601-C / 0619-E (Monthly - 12 months)
- 2550Q (Quarterly VAT - 4 quarters)
- 1601-EQ (Quarterly EWT - 4 quarters)
- 1702-RT/EX (Annual Income Tax - 1 entry)
- 1702Q (Quarterly Income Tax - 1 entry)

**Month-End Closing Tasks (36 entries):**
- Payroll & Personnel
- Tax & Provisions
- Client Billings
- WIP/OOP Management
- AR/AP Aging
- Accruals & Reclassifications

**RACI Matrix:**
- Supervisor assignments per employee
- Reviewer: CKVC (Finance Supervisor), JPAL, RIM, BOM, LAS
- Approver: CKVC (Finance Director), RIM (Senior Finance Manager)

**Deadlines:**
- Preparation: BIR Deadline - 4 business days
- Review: BIR Deadline - 2 business days
- Approval: BIR Deadline - 1 business day
    """,
}
