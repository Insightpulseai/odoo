#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finance PPM Stage + Project Seeder for Odoo 19 CE (XML-RPC)
============================================================
Seeds canonical 6-stage workflow and Finance PPM project.
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

PROJECT_NAME = "Finance PPM - Month-End Close & Tax Filing"

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
        "description": stage_def["description"],
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
# Seed project
# ---------------------------------------------------------------------------
print()
print("Seeding Finance PPM Project...")
existing_project = _kw(
    "project.project", "search",
    [[("name", "=", PROJECT_NAME)]],
    {"limit": 1},
)

if existing_project:
    project_id = existing_project[0]
    print(f"  Project exists: {PROJECT_NAME} (ID {project_id})")
else:
    project_id = _kw("project.project", "create", [{
        "name": PROJECT_NAME,
        "allow_timesheets": True,
        "allow_subtasks": True,
        "allow_recurring_tasks": True,
        "allow_task_dependencies": True,
        "allow_milestones": True,
        "description": (
            "Month-End Close & BIR Tax Filing - Finance SSC\n"
            "9 employees | 36 closing tasks | 33 BIR filings\n"
            "Odoo 19 CE + OCA 19.0"
        ),
    }])
    print(f"  Created Project: {PROJECT_NAME} (ID {project_id})")

# Link stages to project
for sid in stage_ids:
    _kw("project.task.type", "write", [[sid], {"project_ids": [(4, project_id)]}])
print(f"  Linked {len(stage_ids)} stages to project {project_id}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print()
print("=" * 60)
print("Odoo 19 Seeding Complete!")
print(f"  Project: {PROJECT_NAME} (ID {project_id})")
print(f"  Stages:  {len(stage_ids)} stages linked")
print("=" * 60)
