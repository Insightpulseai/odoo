#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finance PPM Stage + Project Seeder for Odoo 19 CE (XML-RPC)
============================================================
Seeds canonical 6-stage workflow and 2 Finance PPM projects
(Month-End Close + BIR Tax Filing).
Idempotent - safe to run multiple times.

Usage:
    python3 scripts/seed_finance_ppm_stages_odoo19.py <admin_password>

    # Or with env vars:
    export ODOO_URL="https://erp.insightpulseai.com"
    export ODOO_DB="odoo"
    export ODOO_USER="admin@insightpulseai.com"
    python3 scripts/seed_finance_ppm_stages_odoo19.py "$ODOO_ADMIN_PASSWORD"
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
    sys.stderr.write("Usage: seed_finance_ppm_stages_odoo19.py <admin_password>\n")
    sys.exit(1)

ODOO_PASSWORD = sys.argv[1]

# ---------------------------------------------------------------------------
# Canonical stage definitions (Odoo 19 CE + OCA 19.0)
# ---------------------------------------------------------------------------
STAGES = [
    {
        "name": "To Do",
        "sequence": 10,
        "fold": False,
        "description": "Tasks not yet started",
    },
    {
        "name": "In Preparation",
        "sequence": 20,
        "fold": False,
        "description": "Data gathering, initial JE preparation (1 Day)",
    },
    {
        "name": "Under Review",
        "sequence": 30,
        "fold": False,
        "description": "Supervisor review of entries (0.5 Day)",
    },
    {
        "name": "Pending Approval",
        "sequence": 40,
        "fold": False,
        "description": "Finance Director sign-off (0.5 Day)",
    },
    {
        "name": "Done",
        "sequence": 50,
        "fold": True,
        "description": "Task completed and posted",
    },
    {
        "name": "Cancelled",
        "sequence": 60,
        "fold": True,
        "description": "Task cancelled or deferred",
    },
]

PROJECT_CLOSE = "Finance PPM - Month-End Close"
PROJECT_TAX = "Finance PPM - BIR Tax Filing"

# ---------------------------------------------------------------------------
# Connect
# ---------------------------------------------------------------------------
print("=" * 60)
print("Finance PPM Stage Seeder - Odoo 19 CE")
print("=" * 60)
print(f"URL: {ODOO_URL}")
print(f"DB:  {ODOO_DB}")
print()

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
try:
    version = common.version()
    server_version = version.get("server_version", "unknown")
    print(f"Server: Odoo {server_version}")
except Exception as e:
    sys.stderr.write(f"ERROR: Cannot reach {ODOO_URL}: {e}\n")
    sys.exit(1)

uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
if not uid:
    sys.stderr.write("ERROR: Authentication failed. Check credentials.\n")
    sys.exit(1)
print(f"Authenticated as UID {uid}")

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")


def _kw(model, method, *args, **kwargs):
    """Shorthand for execute_kw."""
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, model, method, *args, **kwargs)


# ---------------------------------------------------------------------------
# Seed stages
# ---------------------------------------------------------------------------
print()
print("Seeding Stages (Odoo 19)...")
stage_ids = []

for stage_def in STAGES:
    existing = _kw(
        "project.task.type", "search",
        [[("name", "=", stage_def["name"])]],
        {"limit": 1},
    )
    vals = {
        "sequence": stage_def["sequence"],
        "fold": stage_def["fold"],
    }
    if existing:
        _kw("project.task.type", "write", [existing, vals])
        sid = existing[0]
        print(f"  Updated {stage_def['name']} (ID {sid})")
    else:
        vals["name"] = stage_def["name"]
        sid = _kw("project.task.type", "create", [vals])
        print(f"  Created {stage_def['name']} (ID {sid})")
    stage_ids.append(sid)

# ---------------------------------------------------------------------------
# Seed projects (2 projects: Monthly Close + BIR Tax Filing)
# ---------------------------------------------------------------------------
print()
print("Seeding Finance PPM Projects...")

project_ids_map = {}
for proj_name, proj_desc in [
    (PROJECT_CLOSE, (
        "Month-End Close - Finance SSC\n"
        "9 employees | 39 closing tasks across 5 phases\n"
        "Odoo 19 CE + OCA 19.0"
    )),
    (PROJECT_TAX, (
        "BIR Tax Filing - Finance SSC\n"
        "9 employees | 50 BIR tax filing tasks\n"
        "1601-C, 0619-E, 2550M, 2550Q, 1601-EQ, 1702Q, 1702-RT, 1604-CF, 1604-E\n"
        "Odoo 19 CE + OCA 19.0"
    )),
]:
    existing_project = _kw(
        "project.project", "search",
        [[("name", "=", proj_name)]],
        {"limit": 1},
    )

    if existing_project:
        pid = existing_project[0]
        print(f"  Project exists: {proj_name} (ID {pid})")
    else:
        # Discover available fields to avoid Invalid field errors on CE installs
        available_fields = _kw("project.project", "fields_get", [], {"attributes": ["string"]})
        proj_vals = {"name": proj_name}
        optional = {
            "allow_timesheets": True,
            "allow_subtasks": True,
            "allow_recurring_tasks": True,
            "allow_task_dependencies": True,
            "allow_milestones": True,
            "description": proj_desc,
        }
        for k, v in optional.items():
            if k in available_fields:
                proj_vals[k] = v
        pid = _kw("project.project", "create", [proj_vals])
        print(f"  Created Project: {proj_name} (ID {pid})")

    # Link stages to project
    for sid in stage_ids:
        _kw("project.task.type", "write", [[sid], {"project_ids": [(4, pid)]}])
    print(f"  Linked {len(stage_ids)} stages to project {pid}")
    project_ids_map[proj_name] = pid

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print()
print("=" * 60)
print("Odoo 19 Seeding Complete!")
for pname, pid in project_ids_map.items():
    print(f"  Project: {pname} (ID {pid})")
print(f"  Stages:  {len(stage_ids)} stages linked to both projects")
print("=" * 60)
