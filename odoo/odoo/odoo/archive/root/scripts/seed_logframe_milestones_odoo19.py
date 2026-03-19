#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logframe Milestone Seeder for Odoo 19 CE (XML-RPC)
===================================================
Seeds project milestones mapped to the Finance PPM Logframe:

  Goal    → 100% compliant and timely closing + filing
  Outcome → <1 day avg delay across teams
  IM1     → Month-End Closing (reconciliation + TB sign-off)
  IM2     → Tax Filing Compliance (BIR deadline adherence)
  Outputs → JEs finalized, BIR filed, reports approved

Milestones are linked to both Finance PPM projects.
Idempotent — safe to run multiple times.

Usage:
    python3 scripts/seed_logframe_milestones_odoo19.py <admin_password>
"""
import os
import sys
import xmlrpc.client

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ODOO_URL = os.getenv("ODOO_URL", "https://erp.insightpulseai.com")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USER = os.getenv("ODOO_USER", "admin@insightpulseai.com")

if len(sys.argv) < 2:
    sys.stderr.write("Usage: seed_logframe_milestones_odoo19.py <admin_password>\n")
    sys.exit(1)

ODOO_PASSWORD = sys.argv[1]

PROJECT_CLOSE = "Finance PPM - Month-End Close"
PROJECT_TAX = "Finance PPM - BIR Tax Filing"

# ---------------------------------------------------------------------------
# Logframe → Milestone mapping
# ---------------------------------------------------------------------------
# Each logframe level becomes a milestone in the appropriate project(s).
# Milestones serve as progress checkpoints visible on Kanban and timeline.

MILESTONES = [
    # IM1 milestones (Month-End Close project)
    {
        "name": "IM1: Phase I — Initial & Compliance",
        "project": PROJECT_CLOSE,
        "deadline": None,  # recurring monthly
        "description": (
            "Logframe IM1 / Phase I\n"
            "Activities: Process payroll, tax provisions, rent/lease entries, "
            "accruals, cash advances, prior period reversals.\n"
            "Indicator: % of tasks completed on time\n"
            "Verification: GL logs, reconciliation sheets"
        ),
    },
    {
        "name": "IM1: Phase II — Accruals & Amortization",
        "project": PROJECT_CLOSE,
        "deadline": None,
        "description": (
            "Logframe IM1 / Phase II\n"
            "Activities: Depreciation, amortization, corporate accruals, "
            "insurance, treasury, prior month reversals, regional reporting.\n"
            "Indicator: # of closing adjustments\n"
            "Verification: Amortization schedules, accrual logs"
        ),
    },
    {
        "name": "IM1: Phase III — WIP & Client Billings",
        "project": PROJECT_CLOSE,
        "deadline": None,
        "description": (
            "Logframe IM1 / Phase III\n"
            "Activities: Revenue accruals, WIP/OOP reclassification, "
            "business permit amortization, audit fees, intercompany revaluation.\n"
            "Indicator: WIP schedule reconciled\n"
            "Verification: WIP summary, AR aging report"
        ),
    },
    {
        "name": "IM1: Phase IV — Final Adjustments",
        "project": PROJECT_CLOSE,
        "deadline": None,
        "description": (
            "Logframe IM1 / Phase IV\n"
            "Activities: Input VAT compilation, recurring expense accruals, "
            "CA liquidations, expense reclassifications, AP aging.\n"
            "Indicator: All JEs posted and balanced\n"
            "Verification: Trial balance, VAT report"
        ),
    },
    {
        "name": "IM1: Phase V — Sign-off",
        "project": PROJECT_CLOSE,
        "deadline": None,
        "description": (
            "Logframe IM1 / Phase V\n"
            "Activities: SFM trial balance review (RIM), "
            "FD trial balance sign-off (CKVC), regional submission (BOM).\n"
            "Indicator: TB signed off, regional submission complete\n"
            "Verification: Signed TB, submission confirmation"
        ),
    },
    # IM2 milestones (BIR Tax Filing project)
    {
        "name": "IM2: Monthly Withholding (1601-C / 0619-E)",
        "project": PROJECT_TAX,
        "deadline": None,
        "description": (
            "Logframe IM2 / Monthly Withholding Tax\n"
            "Forms: 1601-C (Compensation WT), 0619-E (Expanded WT)\n"
            "Deadline: 10th of following month\n"
            "Indicator: % filed before BIR deadline\n"
            "Verification: BIR confirmation receipts, eFPS acknowledgment"
        ),
    },
    {
        "name": "IM2: Monthly VAT (2550M)",
        "project": PROJECT_TAX,
        "deadline": None,
        "description": (
            "Logframe IM2 / Monthly VAT Declaration\n"
            "Form: 2550M\n"
            "Deadline: 20th of following month\n"
            "Indicator: Filing rate vs deadline\n"
            "Verification: BIR confirmation receipts, Output/Input VAT reconciliation"
        ),
    },
    {
        "name": "IM2: Quarterly Filing (2550Q / 1601-EQ / 1702Q)",
        "project": PROJECT_TAX,
        "deadline": None,
        "description": (
            "Logframe IM2 / Quarterly Tax Returns\n"
            "Forms: 2550Q (Quarterly VAT), 1601-EQ (Quarterly EWT), "
            "1702Q (Quarterly Income Tax)\n"
            "Deadline: 25th-30th of month following quarter end\n"
            "Indicator: % filed with SLSP/QAP attachments\n"
            "Verification: eFPS submission confirmations, SLSP/QAP .dat files"
        ),
    },
    {
        "name": "IM2: Annual Filing (1702-RT / 1604-CF / 1604-E)",
        "project": PROJECT_TAX,
        "deadline": "2026-04-15",
        "description": (
            "Logframe IM2 / Annual Tax Returns\n"
            "Forms: 1702-RT (Annual Income Tax, due Apr 15), "
            "1604-CF (Compensation Alphalist, due Jan 31), "
            "1604-E (Expanded Alphalist, due Mar 1)\n"
            "Indicator: All annual returns filed and confirmed\n"
            "Verification: eAFS submission, BIR receipts, Alphalist/SAWT .dat"
        ),
    },
    # Cross-project milestones
    {
        "name": "Output: JEs & Accruals Finalized",
        "project": PROJECT_CLOSE,
        "deadline": None,
        "description": (
            "Logframe Output 1\n"
            "All journal entries and accruals for the period are finalized, "
            "reviewed, and posted in Odoo.\n"
            "Indicator: # completed tasks in Month-End Close project\n"
            "Verification: Monthly compliance sheet"
        ),
    },
    {
        "name": "Output: All BIR Forms Filed",
        "project": PROJECT_TAX,
        "deadline": None,
        "description": (
            "Logframe Output 2\n"
            "All BIR tax returns for the period are computed, approved, "
            "filed via eFPS/eBIRForms, and receipts uploaded.\n"
            "Indicator: # completed tasks in BIR Tax Filing project\n"
            "Verification: BIR confirmation receipts"
        ),
    },
]

# ---------------------------------------------------------------------------
# Connect
# ---------------------------------------------------------------------------
print("=" * 60)
print("Logframe Milestone Seeder - Odoo 19 CE")
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
# Resolve project IDs
# ---------------------------------------------------------------------------
project_map = {}
for proj_name in [PROJECT_CLOSE, PROJECT_TAX]:
    ids = _kw("project.project", "search", [[("name", "=", proj_name)]], {"limit": 1})
    if ids:
        project_map[proj_name] = ids[0]
        print(f"  Project: {proj_name} (ID {ids[0]})")
    else:
        print(f"  WARNING: Project '{proj_name}' not found — run seed_finance_ppm_stages_odoo19.py first")

if not project_map:
    sys.stderr.write("ERROR: No Finance PPM projects found.\n")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Check if project.milestone model exists (Odoo 19 feature)
# ---------------------------------------------------------------------------
try:
    _kw("project.milestone", "search", [[]], {"limit": 1})
    has_milestones = True
    print("  Milestone model: project.milestone (available)")
except Exception:
    has_milestones = False
    print("  Milestone model: not available — milestones require allow_milestones=True")

# ---------------------------------------------------------------------------
# Seed milestones
# ---------------------------------------------------------------------------
print()
print("Seeding Logframe Milestones...")
created = 0
skipped = 0
failed = 0

for ms in MILESTONES:
    proj_name = ms["project"]
    if proj_name not in project_map:
        print(f"  SKIP: {ms['name']} — project not found")
        skipped += 1
        continue

    project_id = project_map[proj_name]

    if has_milestones:
        # Use project.milestone model (Odoo 19)
        existing = _kw("project.milestone", "search",
                        [[("name", "=", ms["name"]), ("project_id", "=", project_id)]],
                        {"limit": 1})
        if existing:
            skipped += 1
            continue

        vals = {
            "name": ms["name"],
            "project_id": project_id,
        }
        if ms.get("deadline"):
            vals["deadline"] = ms["deadline"]

        try:
            mid = _kw("project.milestone", "create", [vals])
            created += 1
            print(f"  Created: {ms['name']} (ID {mid})")
        except Exception as e:
            failed += 1
            print(f"  FAILED: {ms['name']}: {e}")
    else:
        # Fallback: create as tags on the project
        existing = _kw("project.tags", "search",
                        [[("name", "=", ms["name"])]],
                        {"limit": 1})
        if existing:
            skipped += 1
            continue

        try:
            tid = _kw("project.tags", "create", [{"name": ms["name"]}])
            created += 1
            print(f"  Created tag: {ms['name']} (ID {tid})")
        except Exception as e:
            failed += 1
            print(f"  FAILED: {ms['name']}: {e}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print()
print("=" * 60)
print("Logframe Milestone Seeding Complete!")
print(f"  Created: {created}")
print(f"  Skipped: {skipped}")
print(f"  Failed:  {failed}")
print()
print("Logframe → Odoo Mapping:")
print("  Goal      → v_logframe_goal_kpi (on-time rate across both projects)")
print("  Outcome   → v_logframe_outcome_kpi (avg delay < 1 day)")
print(f"  IM1       → {PROJECT_CLOSE} (5 phase milestones)")
print(f"  IM2       → {PROJECT_TAX} (4 filing milestones)")
print("  Outputs   → v_logframe_outputs_kpi (JEs + BIR + reports)")
print("=" * 60)
