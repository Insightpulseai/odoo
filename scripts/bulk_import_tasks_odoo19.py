#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bulk Import Finance PPM Tasks for Odoo 19 CE (XML-RPC)
======================================================
Imports tasks into 2 separate projects:
  - "Finance PPM - Month-End Close": 39 closing tasks (5 phases)
  - "Finance PPM - BIR Tax Filing": 50 BIR tax filing tasks (9 form types)
Total: 89 base tasks across 2 projects.

Employee Reference:
    CKVC - Khalil Veracruz  (Finance Director / Approver)
    RIM  - Rey Meran         (Senior Finance Manager / Reviewer)
    BOM  - Beng Manalo       (Finance Manager)
    JPAL - Jinky Paladin     (Finance Analyst)
    LAS  - Amor Lasaga       (Finance Analyst)
    JLI  - Jerald Loterte    (Finance Analyst)
    RMQB - Sally Brillantes  (Finance Analyst)
    JAP  - Jasmin Ignacio    (Finance Analyst)
    JRMO - Jhoee Oliva       (Finance Analyst)

Usage:
    python3 scripts/bulk_import_tasks_odoo19.py <admin_password>
    python3 scripts/bulk_import_tasks_odoo19.py <admin_password> --months 12
"""
import os
import sys
import xmlrpc.client
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ODOO_URL = os.getenv("ODOO_URL", "https://erp.insightpulseai.com")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USER = os.getenv("ODOO_USER", "admin@insightpulseai.com")

if len(sys.argv) < 2:
    sys.stderr.write("Usage: bulk_import_tasks_odoo19.py <admin_password> [--months N]\n")
    sys.exit(1)

ODOO_PASSWORD = sys.argv[1]

# Parse optional --months argument (default: generate for remaining 2026 months)
GENERATE_MONTHS = 0
if "--months" in sys.argv:
    idx = sys.argv.index("--months")
    if idx + 1 < len(sys.argv):
        GENERATE_MONTHS = int(sys.argv[idx + 1])

PROJECT_CLOSE = "Finance PPM - Month-End Close"
PROJECT_TAX = "Finance PPM - BIR Tax Filing"

# ---------------------------------------------------------------------------
# Employee directory
# ---------------------------------------------------------------------------
EMPLOYEES = {
    "CKVC": {"name": "Khalil Veracruz", "email": "khalil.veracruz@omc.com", "role": "Finance Director", "tier": "Director"},
    "RIM":  {"name": "Rey Meran", "email": "rey.meran@omc.com", "role": "Senior Finance Manager", "tier": "Senior Manager"},
    "BOM":  {"name": "Beng Manalo", "email": "beng.manalo@omc.com", "role": "Finance Manager", "tier": "Manager"},
    "JPAL": {"name": "Jinky Paladin", "email": "jinky.paladin@omc.com", "role": "Finance Analyst", "tier": "Analyst"},
    "LAS":  {"name": "Amor Lasaga", "email": "amor.lasaga@omc.com", "role": "Finance Analyst", "tier": "Analyst"},
    "JLI":  {"name": "Jerald Loterte", "email": "jerald.loterte@omc.com", "role": "Finance Analyst", "tier": "Analyst"},
    "RMQB": {"name": "Sally Brillantes", "email": "sally.brillantes@omc.com", "role": "Finance Analyst", "tier": "Analyst"},
    "JAP":  {"name": "Jasmin Ignacio", "email": "jasmin.ignacio@omc.com", "role": "Finance Analyst", "tier": "Analyst"},
    "JRMO": {"name": "Jhoee Oliva", "email": "jhoee.oliva@omc.com", "role": "Finance Analyst", "tier": "Analyst"},
}

# Canonical seed data root (SSOT — do not add fallback paths)
SEED_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "seed", "finance_ppm", "tbwa_smp")

# Company reference
COMPANY = "TBWA\\SMP Philippines"

# ---------------------------------------------------------------------------
# 36 Month-End Closing Tasks (from TBWA Finance SSC seed data)
# ---------------------------------------------------------------------------
CLOSING_TASKS = [
    # RIM tasks (Phase I: Initial & Compliance)
    {
        "code": "RIM", "seq": 10, "category": "Payroll & Personnel",
        "name": "Process and record Payroll, Final Pay, SL Conversions, and early retirement accrual",
        "reviewer": "CKVC", "approver": "CKVC",
        "assignee": "RIM", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "RIM", "seq": 20, "category": "Tax & Provisions",
        "name": "Calculate and record the monthly Tax Provision and PPB Provision (performance bonuses)",
        "reviewer": "CKVC", "approver": "CKVC",
        "assignee": "RIM", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "RIM", "seq": 30, "category": "Rent & Leases",
        "name": "Record recurring monthly Rental Income/Expense and monthly amortization expense for employee hospitalization plans",
        "reviewer": "CKVC", "approver": "CKVC",
        "assignee": "RIM", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "RIM", "seq": 40, "category": "Accruals & Expenses",
        "name": "Record accruals for Consultancy Fees and various routine General Expense Accruals",
        "detail": "Estimated expense for which a vendor invoice has not yet been received.",
        "reviewer": "CKVC", "approver": "CKVC",
        "assignee": "RIM", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "RIM", "seq": 50, "category": "Accruals & Expenses",
        "name": "Process and record Payments for various Cash Advances",
        "detail": "Recording the funding/issuance of cash to employees for expected business expenditures.",
        "reviewer": "CKVC", "approver": "CKVC",
        "assignee": "RIM", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "RIM", "seq": 60, "category": "Prior Period Review",
        "name": "Process reversal entries for the prior month's accruals and reclassifications",
        "detail": "The necessary reversal or adjustment of temporary journal entries created in a previous month.",
        "reviewer": "CKVC", "approver": "CKVC",
        "assignee": "RIM", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    # BOM tasks (Phase II: Accruals & Amortization)
    {
        "code": "BOM", "seq": 70, "category": "Amortization & Corporate",
        "name": "Record monthly Depreciation, Amortization for vehicles/purchases/LOA, and Amortization for all technology licenses and shared service costs",
        "detail": "Allocating prepaid expenses and capital costs over time to reflect true monthly resource consumption.",
        "reviewer": "RIM", "approver": "CKVC",
        "assignee": "BOM", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "BOM", "seq": 80, "category": "Corporate Accruals",
        "name": "Accrue monthly expenses for Management and Royalty fees, consulting fees, and funds for Innovations/Initiatives",
        "detail": "Recognizing an expense for internal projects or strategic corporate investments not yet formally invoiced.",
        "reviewer": "RIM", "approver": "CKVC",
        "assignee": "BOM", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "BOM", "seq": 90, "category": "Insurance",
        "name": "Record monthly accrual for various Corporate Insurance types and amortize prepaid Health Insurance",
        "detail": "Monthly tracking and recording of premiums for various corporate insurance policies.",
        "reviewer": "RIM", "approver": "CKVC",
        "assignee": "BOM", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "BOM", "seq": 100, "category": "Treasury & Other",
        "name": "Record monthly bank charges, perform revaluation of foreign currency bank accounts, and record the monthly expense portion of the Omnicom stock option grant",
        "detail": "Non-operating financial activities including capital structure and compliance.",
        "reviewer": "RIM", "approver": "CKVC",
        "assignee": "BOM", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "BOM", "seq": 110, "category": "Prior Period Review",
        "name": "Process reversal entries for all prior month Accruals (e.g., trainings, production/retainers)",
        "reviewer": "RIM", "approver": "CKVC",
        "assignee": "BOM", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "BOM", "seq": 120, "category": "Regional Reporting",
        "name": "Prepare reports for Flash, Wins & Losses and Revenue",
        "reviewer": "RIM", "approver": "CKVC",
        "assignee": "BOM", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    # JPAL tasks (Phase III: WIP)
    {
        "code": "JPAL", "seq": 130, "category": "Client Billings",
        "name": "Accrue estimated Production, Retainer Fees, Media Commission, Creative Fees, and OOPC",
        "detail": "Recognizing revenue and billable costs based on client contracts and project status. Recording estimated Out-of-Pocket Costs that will eventually be billed to a client.",
        "reviewer": "BOM", "approver": "CKVC",
        "assignee": "JPAL", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "JPAL", "seq": 140, "category": "WIP/OOP Management",
        "name": "Perform month-end Reclassifications of OOP to WIP and necessary Reclass WIP to OOP",
        "detail": "Reconciling and reclassifying costs to ensure they are correctly categorized as billable (WIP) or internal (OOP).",
        "reviewer": "BOM", "approver": "CKVC",
        "assignee": "JPAL", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "JPAL", "seq": 150, "category": "Amortization & Corporate",
        "name": "Record monthly Amortization of the Business Permit and Amortization of LOA",
        "detail": "Allocating prepaid expenses and capital costs over time to reflect true monthly resource consumption.",
        "reviewer": "BOM", "approver": "CKVC",
        "assignee": "JPAL", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "JPAL", "seq": 160, "category": "Amortization & Corporate",
        "name": "Accrue estimated monthly Audit Fees",
        "reviewer": "BOM", "approver": "CKVC",
        "assignee": "JPAL", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "JPAL", "seq": 170, "category": "Amortization & Corporate",
        "name": "Record monthly Rental Expense/Income related to intercompany transactions",
        "reviewer": "BOM", "approver": "CKVC",
        "assignee": "JPAL", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "JPAL", "seq": 180, "category": "Amortization & Corporate",
        "name": "Perform month-end Revaluation of Intercompany Balances",
        "detail": "Adjusting intercompany balances to reflect the correct value at the month-end exchange rate.",
        "reviewer": "BOM", "approver": "CKVC",
        "assignee": "JPAL", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "JPAL", "seq": 190, "category": "AR Aging - WC",
        "name": "Prepare reports for Working Capital related to AR",
        "reviewer": "BOM", "approver": "CKVC",
        "assignee": "JPAL", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    # LAS tasks
    {
        "code": "LAS", "seq": 200, "category": "CA Liquidations",
        "name": "Process and record Cash Advance (CA) Liquidations for specific project-related expenses",
        "reviewer": "RIM", "approver": "CKVC",
        "assignee": "LAS", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "LAS", "seq": 210, "category": "AP Aging - WC",
        "name": "Prepare AP Aging report for working capital submission",
        "reviewer": "BOM", "approver": "CKVC",
        "assignee": "LAS", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "LAS", "seq": 220, "category": "OOP",
        "name": "Prepare HOW's summary report",
        "reviewer": "RIM", "approver": "CKVC",
        "assignee": "LAS", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "LAS", "seq": 230, "category": "Asset & Lease Entries",
        "name": "Record monthly interest expense on leased assets and process amortization reclassifications for prepaid corporate fees",
        "detail": "Recording transactions for financed assets and long-term commitments.",
        "reviewer": "RIM", "approver": "CKVC",
        "assignee": "LAS", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "LAS", "seq": 240, "category": "Reclassifications",
        "name": "Process required reclassifications between specific GL accounts and between Marketing Expense categories",
        "detail": "Correcting entries across the general ledger (GL).",
        "reviewer": "BOM", "approver": "CKVC",
        "assignee": "LAS", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    # JLI tasks (Phase IV: Final Adjustments)
    {
        "code": "JLI", "seq": 250, "category": "VAT & Taxes",
        "name": "Compile and record monthly Input VAT entries (VAT paid on purchases) and the monthly VAT Report",
        "detail": "Cumulative summary of VAT activity.",
        "reviewer": "JPAL", "approver": "CKVC",
        "assignee": "JLI", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "JLI", "seq": 260, "category": "Accruals & Assets",
        "name": "Accrue recurring Expenses (estimated expense for regularly occurring services)",
        "detail": "Recording estimated expenses for recurring monthly costs and recognizing non-fixed asset costs.",
        "reviewer": "LAS", "approver": "CKVC",
        "assignee": "JLI", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "JLI", "seq": 270, "category": "Accruals & Assets",
        "name": "Record the monthly recognition/capitalization of Other Computer Related Costs",
        "reviewer": "LAS", "approver": "CKVC",
        "assignee": "JLI", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "JLI", "seq": 280, "category": "AP Aging",
        "name": "Prepare AP Aging report with detailed status per invoice",
        "reviewer": "LAS", "approver": "CKVC",
        "assignee": "JLI", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    # RMQB tasks
    {
        "code": "RMQB", "seq": 290, "category": "CA Liquidations",
        "name": "Process and record Cash Advance (CA) Liquidations submitted by employees",
        "reviewer": "RIM", "approver": "CKVC",
        "assignee": "RMQB", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "RMQB", "seq": 300, "category": "Accruals & Assets",
        "name": "Accrue monthly expense for Employee Cellphone Allowance",
        "reviewer": "LAS", "approver": "CKVC",
        "assignee": "RMQB", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "RMQB", "seq": 310, "category": "Expense Reclassification",
        "name": "Process reclassifications to correct expense categories (e.g., General Expense to Wireless and Meals)",
        "detail": "Adjusting a recorded expense from one GL account to another to ensure correct reporting.",
        "reviewer": "RIM", "approver": "CKVC",
        "assignee": "RMQB", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    # JAP tasks
    {
        "code": "JAP", "seq": 320, "category": "VAT Reporting",
        "name": "Compile, review, and record the monthly VAT Report (Initial and additional entries)",
        "reviewer": "JPAL", "approver": "CKVC",
        "assignee": "JAP", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "JAP", "seq": 330, "category": "Job Transfers",
        "name": "Process and record Transfers of Job Codes for consultancy fees and corporate projects",
        "detail": "Adjusting costs or revenues between different internal project codes or job numbers.",
        "reviewer": "JPAL", "approver": "CKVC",
        "assignee": "JAP", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "JAP", "seq": 340, "category": "Job Transfers",
        "name": "Record specific GL reclassifications needed for month-end adjustments",
        "reviewer": "JPAL", "approver": "CKVC",
        "assignee": "JAP", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    # JRMO tasks
    {
        "code": "JRMO", "seq": 350, "category": "Accruals",
        "name": "Compile documents for the attachment of the revenue accruals",
        "reviewer": "JPAL", "approver": "CKVC",
        "assignee": "JRMO", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    {
        "code": "JRMO", "seq": 360, "category": "WIP",
        "name": "Prepare WIP schedule summary per Job#",
        "reviewer": "JPAL", "approver": "CKVC",
        "assignee": "JRMO", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
    # Phase V: Sign-off
    {
        "code": "RIM", "seq": 370, "category": "Sign-off",
        "name": "Final Trial Balance Review (SFM)",
        "reviewer": "—", "approver": "—",
        "assignee": "RIM", "prep_days": 1, "review_days": 0, "approval_days": 0,
    },
    {
        "code": "CKVC", "seq": 380, "category": "Sign-off",
        "name": "Final Trial Balance Sign-off (FD)",
        "reviewer": "—", "approver": "—",
        "assignee": "CKVC", "prep_days": 1, "review_days": 0, "approval_days": 0,
    },
    {
        "code": "BOM", "seq": 390, "category": "Sign-off",
        "name": "Regional Submission",
        "reviewer": "RIM", "approver": "CKVC",
        "assignee": "BOM", "prep_days": 1, "review_days": 0.5, "approval_days": 0.5,
    },
]

# BIR Tax Filing Tasks for full year 2026
MONTHS_2026 = [
    ("January", "2026-01", "2026-02-10", "2026-02-20"),
    ("February", "2026-02", "2026-03-10", "2026-03-20"),
    ("March", "2026-03", "2026-04-10", "2026-04-20"),
    ("April", "2026-04", "2026-05-11", "2026-05-20"),
    ("May", "2026-05", "2026-06-10", "2026-06-22"),
    ("June", "2026-06", "2026-07-10", "2026-07-20"),
    ("July", "2026-07", "2026-08-10", "2026-08-20"),
    ("August", "2026-08", "2026-09-10", "2026-09-21"),
    ("September", "2026-09", "2026-10-12", "2026-10-20"),
    ("October", "2026-10", "2026-11-10", "2026-11-20"),
    ("November", "2026-11", "2026-12-10", "2026-12-21"),
    ("December", "2026-12", "2027-01-11", "2027-01-20"),
]

QUARTERS_2026 = [
    ("Q1", "Jan-Mar", "2026-04-25", "2026-04-30"),
    ("Q2", "Apr-Jun", "2026-07-25", "2026-07-31"),
    ("Q3", "Jul-Sep", "2026-10-26", "2026-10-30"),
    ("Q4", "Oct-Dec", "2027-01-25", "2027-01-29"),
]


def build_bir_tasks():
    """Generate 50 BIR tax filing tasks for 2026."""
    tasks = []
    seq = 1000

    # Monthly 1601-C (12 filings)
    for month_name, period, deadline_1601c, deadline_0619e in MONTHS_2026:
        tasks.append({
            "name": f"1601-C (Withholding Tax) - {month_name} 2026",
            "category": "BIR 1601-C",
            "description": (
                f"BIR Form: 1601-C (Monthly Withholding Tax on Compensation)\n"
                f"Period: {month_name} 2026\n"
                f"Deadline: {deadline_1601c}\n"
                f"Preparer: BOM | Reviewer: RIM | Approver: CKVC"
            ),
            "deadline": deadline_1601c,
            "assignee": "BOM",
            "reviewer": "RIM",
            "approver": "CKVC",
            "planned_hours": 8,
            "seq": seq,
        })
        seq += 10

        # Monthly 0619-E (12 filings) — same deadline as 1601-C (10th of following month)
        tasks.append({
            "name": f"0619-E (Expanded Withholding Tax) - {month_name} 2026",
            "category": "BIR 0619-E",
            "description": (
                f"BIR Form: 0619-E (Monthly Remittance of Creditable Income Taxes Withheld - Expanded)\n"
                f"Period: {month_name} 2026\n"
                f"Deadline: {deadline_1601c}\n"
                f"Preparer: BOM | Reviewer: RIM | Approver: CKVC"
            ),
            "deadline": deadline_1601c,
            "assignee": "BOM",
            "reviewer": "RIM",
            "approver": "CKVC",
            "planned_hours": 8,
            "seq": seq,
        })
        seq += 10

        # Monthly 2550M (12 filings) — 20th of following month
        tasks.append({
            "name": f"2550M (Monthly VAT) - {month_name} 2026",
            "category": "BIR 2550M",
            "description": (
                f"BIR Form: 2550M (Monthly Value-Added Tax Declaration)\n"
                f"Period: {month_name} 2026\n"
                f"Deadline: {deadline_0619e}\n"
                f"Preparer: BOM | Reviewer: RIM | Approver: CKVC"
            ),
            "deadline": deadline_0619e,
            "assignee": "BOM",
            "reviewer": "RIM",
            "approver": "CKVC",
            "planned_hours": 8,
            "seq": seq,
        })
        seq += 10

    # Quarterly 2550Q (4 filings)
    for qtr, months, deadline_2550q, deadline_1601eq in QUARTERS_2026:
        tasks.append({
            "name": f"2550Q (Quarterly VAT) - {qtr} 2026",
            "category": "BIR 2550Q",
            "description": (
                f"BIR Form: 2550Q (Quarterly VAT Return)\n"
                f"Period: {qtr} 2026 ({months})\n"
                f"Deadline: {deadline_2550q}\n"
                f"Preparer: BOM | Reviewer: RIM | Approver: CKVC"
            ),
            "deadline": deadline_2550q,
            "assignee": "BOM",
            "reviewer": "RIM",
            "approver": "CKVC",
            "planned_hours": 16,
            "seq": seq,
        })
        seq += 10

        # Quarterly 1601-EQ (4 filings)
        tasks.append({
            "name": f"1601-EQ (Quarterly EWT) - {qtr} 2026",
            "category": "BIR 1601-EQ",
            "description": (
                f"BIR Form: 1601-EQ (Quarterly Expanded Withholding Tax)\n"
                f"Period: {qtr} 2026 ({months})\n"
                f"Deadline: {deadline_1601eq}\n"
                f"Preparer: BOM | Reviewer: RIM | Approver: CKVC"
            ),
            "deadline": deadline_1601eq,
            "assignee": "BOM",
            "reviewer": "RIM",
            "approver": "CKVC",
            "planned_hours": 16,
            "seq": seq,
        })
        seq += 10

    # Quarterly 1702Q (Quarterly Income Tax) - Q1, Q2, Q3 2026
    # (Q4 covered by annual 1702-RT/EX; filed within 60 days of quarter end)
    quarterly_1702q = [
        ("Q1", "Jan-Mar", "2026-05-30"),
        ("Q2", "Apr-Jun", "2026-08-29"),
        ("Q3", "Jul-Sep", "2026-11-29"),
    ]
    for qtr, months, deadline_1702q in quarterly_1702q:
        tasks.append({
            "name": f"1702Q (Quarterly Income Tax) - {qtr} 2026",
            "category": "BIR 1702Q",
            "description": (
                f"BIR Form: 1702Q (Quarterly Income Tax Return)\n"
                f"Period: {qtr} 2026 ({months})\n"
                f"Deadline: {deadline_1702q}\n"
                f"Process: 1. Preparation (BOM) → 2. Report Approval (RIM) → "
                f"3. Payment Approval (CKVC) → 4. Filing & Payment (BOM)\n"
                f"Preparer: BOM | Reviewer: RIM | Approver: CKVC"
            ),
            "deadline": deadline_1702q,
            "assignee": "BOM",
            "reviewer": "RIM",
            "approver": "CKVC",
            "planned_hours": 16,
            "seq": seq,
        })
        seq += 10

    # Annual 1702-RT (1 filing)
    tasks.append({
        "name": "1702-RT (Annual Income Tax) - CY 2025",
        "category": "BIR 1702-RT",
        "description": (
            "BIR Form: 1702-RT/EX (Annual Income Tax Return)\n"
            "Period: Calendar Year 2025\n"
            "Deadline: 2026-04-15\n"
            "Process: 1. Preparation (BOM) → 2. Report Approval (RIM) → "
            "3. Payment Approval (CKVC) → 4. Filing & Payment (BOM)\n"
            "Preparer: BOM | Reviewer: RIM | Approver: CKVC"
        ),
        "deadline": "2026-04-15",
        "assignee": "BOM",
        "reviewer": "RIM",
        "approver": "CKVC",
        "planned_hours": 24,
        "seq": seq,
    })
    seq += 10

    # Annual 1604-CF (1 filing) — Annual Information Return (Compensation)
    tasks.append({
        "name": "1604-CF (Annual Info Return - Compensation) - CY 2025",
        "category": "BIR 1604-CF",
        "description": (
            "BIR Form: 1604-CF (Annual Information Return of Income Taxes Withheld on Compensation)\n"
            "Period: Calendar Year 2025\n"
            "Deadline: 2026-01-31\n"
            "Preparer: BOM | Reviewer: RIM | Approver: CKVC"
        ),
        "deadline": "2026-01-31",
        "assignee": "BOM",
        "reviewer": "RIM",
        "approver": "CKVC",
        "planned_hours": 16,
        "seq": seq,
    })
    seq += 10

    # Annual 1604-E (1 filing) — Annual Information Return (Expanded)
    tasks.append({
        "name": "1604-E (Annual Info Return - Expanded) - CY 2025",
        "category": "BIR 1604-E",
        "description": (
            "BIR Form: 1604-E (Annual Information Return of Creditable Income Taxes Withheld - Expanded)\n"
            "Period: Calendar Year 2025\n"
            "Deadline: 2026-03-01\n"
            "Preparer: BOM | Reviewer: RIM | Approver: CKVC"
        ),
        "deadline": "2026-03-01",
        "assignee": "BOM",
        "reviewer": "RIM",
        "approver": "CKVC",
        "planned_hours": 16,
        "seq": seq,
    })

    return tasks


# ---------------------------------------------------------------------------
# Connect
# ---------------------------------------------------------------------------
print("=" * 60)
print("Finance PPM Task Import - Odoo 19 CE")
print("=" * 60)

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
try:
    version = common.version()
    print(f"Server: Odoo {version.get('server_version', 'unknown')}")
except Exception as e:
    sys.stderr.write(f"ERROR: Cannot reach {ODOO_URL}: {e}\n")
    sys.exit(1)

uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
if not uid:
    sys.stderr.write("ERROR: Authentication failed.\n")
    sys.exit(1)
print(f"Authenticated as UID {uid}")

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")


def _kw(model, method, *args, **kwargs):
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, model, method, *args, **kwargs)


# ---------------------------------------------------------------------------
# Resolve projects (2 projects: Month-End Close + BIR Tax Filing)
# ---------------------------------------------------------------------------
close_ids = _kw("project.project", "search", [[("name", "=", PROJECT_CLOSE)]], {"limit": 1})
if not close_ids:
    sys.stderr.write(f"ERROR: Project '{PROJECT_CLOSE}' not found. Run seed_finance_ppm_stages_odoo19.py first.\n")
    sys.exit(1)
close_project_id = close_ids[0]
print(f"Project (Close): {PROJECT_CLOSE} (ID {close_project_id})")

tax_ids = _kw("project.project", "search", [[("name", "=", PROJECT_TAX)]], {"limit": 1})
if not tax_ids:
    sys.stderr.write(f"ERROR: Project '{PROJECT_TAX}' not found. Run seed_finance_ppm_stages_odoo19.py first.\n")
    sys.exit(1)
tax_project_id = tax_ids[0]
print(f"Project (Tax):   {PROJECT_TAX} (ID {tax_project_id})")

# ---------------------------------------------------------------------------
# Resolve stage IDs (shared across both projects)
# ---------------------------------------------------------------------------
stage_map = {}
for stage_data in _kw("project.task.type", "search_read",
                       [[("project_ids", "in", [close_project_id])]],
                       {"fields": ["name", "id"]}):
    stage_map[stage_data["name"]] = stage_data["id"]
print(f"Stages: {list(stage_map.keys())}")

in_prep_stage = stage_map.get("In Preparation", stage_map.get("To Do"))

# ---------------------------------------------------------------------------
# Resolve user IDs by email
# ---------------------------------------------------------------------------
user_map = {}
for code, emp in EMPLOYEES.items():
    users = _kw("res.users", "search", [[("login", "=", emp["email"])]], {"limit": 1})
    if users:
        user_map[code] = users[0]
        print(f"  User {code}: {emp['name']} (UID {users[0]})")
    else:
        # Try by name
        users = _kw("res.users", "search", [[("name", "ilike", emp["name"])]], {"limit": 1})
        if users:
            user_map[code] = users[0]
            print(f"  User {code}: {emp['name']} (UID {users[0]}) [matched by name]")
        else:
            print(f"  User {code}: {emp['name']} [NOT FOUND - will skip assignment]")

# ---------------------------------------------------------------------------
# Import closing tasks
# ---------------------------------------------------------------------------
print()
print("Importing 39 Month-End Closing Tasks...")
created = 0
skipped = 0
failed = 0

for task in CLOSING_TASKS:
    task_name = f"[{task['code']}] {task['category']}: {task['name']}"

    # Check if task already exists (idempotent)
    existing = _kw("project.task", "search",
                    [[("project_id", "=", close_project_id), ("name", "=", task_name)]],
                    {"limit": 1})
    if existing:
        skipped += 1
        continue

    description_parts = [
        f"Employee: {task['code']} ({EMPLOYEES[task['assignee']]['name']})",
        f"Category: {task['category']}",
        f"Detailed Task: {task['name']}",
    ]
    if task.get("detail"):
        description_parts.append(f"Detail: {task['detail']}")
    description_parts.extend([
        f"Reviewed by: {task['reviewer']}",
        f"Approved by: {task['approver']}",
        f"Preparation: {task['prep_days']} Day | Review: {task['review_days']} Day | Approval: {task['approval_days']} Day",
    ])

    vals = {
        "name": task_name,
        "project_id": close_project_id,
        "sequence": task["seq"],
        "description": "\n".join(description_parts),
        "planned_hours": 16,  # 1 day prep + 0.5 day review + 0.5 day approval = 2 days = 16h
        "stage_id": in_prep_stage,
    }

    # Assign user if resolved
    assignee_code = task["assignee"]
    if assignee_code in user_map:
        vals["user_ids"] = [(4, user_map[assignee_code])]

    try:
        _kw("project.task", "create", [vals])
        created += 1
        print(f"  Created: {task_name}")
    except Exception as e:
        failed += 1
        print(f"  FAILED: {task_name}: {e}")

print(f"\nClosing Tasks: Created={created} Skipped={skipped} Failed={failed}")

# ---------------------------------------------------------------------------
# Import BIR tax filing tasks
# ---------------------------------------------------------------------------
print()
print("Importing BIR Tax Filing Tasks...")
bir_tasks = build_bir_tasks()
bir_created = 0
bir_skipped = 0
bir_failed = 0

for task in bir_tasks:
    task_name = task["name"]

    existing = _kw("project.task", "search",
                    [[("project_id", "=", tax_project_id), ("name", "=", task_name)]],
                    {"limit": 1})
    if existing:
        bir_skipped += 1
        continue

    vals = {
        "name": task_name,
        "project_id": tax_project_id,
        "sequence": task["seq"],
        "description": task["description"],
        "planned_hours": task["planned_hours"],
        "date_deadline": task["deadline"],
        "stage_id": in_prep_stage,
    }

    assignee_code = task["assignee"]
    if assignee_code in user_map:
        vals["user_ids"] = [(4, user_map[assignee_code])]

    try:
        _kw("project.task", "create", [vals])
        bir_created += 1
        print(f"  Created: {task_name}")
    except Exception as e:
        bir_failed += 1
        print(f"  FAILED: {task_name}: {e}")

print(f"\nBIR Tasks: Created={bir_created} Skipped={bir_skipped} Failed={bir_failed}")

# ---------------------------------------------------------------------------
# Generate monthly recurring instances if requested
# ---------------------------------------------------------------------------
if GENERATE_MONTHS > 0:
    print()
    print(f"Generating recurring monthly instances for {GENERATE_MONTHS} months...")
    now = datetime.now()
    monthly_created = 0

    for month_offset in range(GENERATE_MONTHS):
        target_date = now + timedelta(days=30 * month_offset)
        month_label = target_date.strftime("%B %Y")
        deadline_str = target_date.strftime("%Y-%m-%d")

        for task in CLOSING_TASKS:
            task_name = f"[{task['code']}] {task['category']}: {task['name']} - {month_label}"

            existing = _kw("project.task", "search",
                            [[("project_id", "=", close_project_id), ("name", "=", task_name)]],
                            {"limit": 1})
            if existing:
                continue

            vals = {
                "name": task_name,
                "project_id": close_project_id,
                "sequence": task["seq"],
                "description": f"Month: {month_label}\n" + "\n".join([
                    f"Employee: {task['code']} ({EMPLOYEES[task['assignee']]['name']})",
                    f"Category: {task['category']}",
                    f"Reviewed by: {task['reviewer']} | Approved by: {task['approver']}",
                ]),
                "planned_hours": 16,
                "date_deadline": deadline_str,
                "stage_id": in_prep_stage,
            }

            assignee_code = task["assignee"]
            if assignee_code in user_map:
                vals["user_ids"] = [(4, user_map[assignee_code])]

            try:
                _kw("project.task", "create", [vals])
                monthly_created += 1
            except Exception:
                pass

    print(f"Monthly instances created: {monthly_created}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
close_total = _kw("project.task", "search_count", [[("project_id", "=", close_project_id)]])
tax_total = _kw("project.task", "search_count", [[("project_id", "=", tax_project_id)]])
print()
print("=" * 60)
print("Odoo 19 Import Complete!")
print(f"  Closing Tasks:  Created={created} Skipped={skipped} Failed={failed}")
print(f"  BIR Tasks:      Created={bir_created} Skipped={bir_skipped} Failed={bir_failed}")
print(f"  Month-End Close project: {close_total} tasks")
print(f"  BIR Tax Filing project:  {tax_total} tasks")
print(f"  Total across both:       {close_total + tax_total}")
print("=" * 60)
