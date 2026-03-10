#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Idempotent Finance PPM Stage + Project Seeder (XML-RPC)
=======================================================
Seeds canonical 6-stage workflow for Finance PPM without requiring custom modules.
Uses standard Odoo XML-RPC API - works with any CE + OCA installation.

Usage:
    export ODOO_URL="http://localhost:8069"
    export ODOO_DB="odoo_core"
    export ODOO_USER="admin"
    export ODOO_PASSWORD="admin"

    python scripts/seed_finance_ppm_stages.py seed      # Create/update stages + project
    python scripts/seed_finance_ppm_stages.py verify    # Check current state
    python scripts/seed_finance_ppm_stages.py rollback  # Remove seeded data (careful!)
"""
import os
import sys
import xmlrpc.client

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

if not all([ODOO_DB, ODOO_USER, ODOO_PASSWORD]):
    sys.stderr.write(
        "ERROR: ODOO_DB, ODOO_USER, and ODOO_PASSWORD must be set as environment variables.\n"
    )
    sys.exit(1)

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
if not uid:
    sys.stderr.write("ERROR: Authentication failed. Check credentials.\n")
    sys.exit(1)

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

# OCA-compatible stage definitions (matches stages.json)
# States: draft (not started), open (in progress), pending (waiting), done (completed), cancelled
STAGES = [
    {
        "name": "To Do",
        "sequence": 10,
        "fold": False,
        "description": "Tasks not yet started",
        "state": "draft",
    },
    {
        "name": "In Preparation",
        "sequence": 20,
        "fold": False,
        "description": "Data gathering, initial work",
        "state": "open",
    },
    {
        "name": "Under Review",
        "sequence": 30,
        "fold": False,
        "description": "Supervisor review",
        "state": "open",
    },
    {
        "name": "Pending Approval",
        "sequence": 40,
        "fold": False,
        "description": "Awaiting Finance Director sign-off",
        "state": "pending",
    },
    {
        "name": "Done",
        "sequence": 50,
        "fold": True,
        "description": "Completed tasks",
        "state": "done",
    },
    {
        "name": "Cancelled",
        "sequence": 60,
        "fold": True,
        "description": "Cancelled tasks",
        "state": "cancelled",
    },
]

FINANCE_PPM_PROJECT_NAME = "Finance PPM - Month-End Close & Tax Filing"


def ensure_project(name: str):
    """Create or update the Finance PPM project."""
    project_ids = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "project.project",
        "search",
        [[("name", "=", name)]],
        {"limit": 1},
    )
    if project_ids:
        print(f"Project exists: {name} (ID {project_ids[0]})")
        return project_ids[0]

    project_id = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "project.project",
        "create",
        [
            {
                "name": name,
                "allow_timesheets": True,
            }
        ],
    )
    print(f"Created project: {name} (ID {project_id})")
    return project_id


def ensure_stage(stage_def: dict):
    """Create or update a task stage (idempotent by name)."""
    existing_ids = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "project.task.type",
        "search",
        [[("name", "=", stage_def["name"])]],
        {"limit": 1},
    )
    vals = {
        "sequence": stage_def["sequence"],
        "fold": stage_def["fold"],
        "description": stage_def["description"],
    }
    if existing_ids:
        models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            "project.task.type",
            "write",
            [existing_ids, vals],
        )
        stage_id = existing_ids[0]
        print(f"Updated stage: {stage_def['name']} (ID {stage_id})")
        return stage_id

    vals["name"] = stage_def["name"]
    stage_id = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "project.task.type",
        "create",
        [vals],
    )
    print(f"Created stage: {stage_def['name']} (ID {stage_id})")
    return stage_id


def link_stages_to_project(stage_ids, project_id):
    """Link stages to project via Many2many field project_ids."""
    for sid in stage_ids:
        models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            "project.task.type",
            "write",
            [[sid], {"project_ids": [(4, project_id)]}],
        )
    print(f"Linked {len(stage_ids)} stages to project {project_id}")


def verify():
    """Verify Finance PPM stages and project exist."""
    print("=" * 60)
    print("Verifying Finance PPM configuration...")
    print("=" * 60)

    # Check project
    project_ids = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "project.project",
        "search",
        [[("name", "=", FINANCE_PPM_PROJECT_NAME)]],
    )
    if project_ids:
        print(f"[PASS] Finance PPM project exists: ID {project_ids[0]}")
    else:
        print("[FAIL] Finance PPM project NOT found")

    # Check stages
    print("\nStage verification:")
    all_pass = True
    for stage in STAGES:
        existing_ids = models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            "project.task.type",
            "search",
            [[("name", "=", stage["name"])]],
        )
        if existing_ids:
            # Read stage details
            stage_data = models.execute_kw(
                ODOO_DB,
                uid,
                ODOO_PASSWORD,
                "project.task.type",
                "read",
                [existing_ids, ["sequence", "fold", "description"]],
            )[0]
            status = "[PASS]"
            if stage_data["sequence"] != stage["sequence"]:
                status = "[WARN]"
                all_pass = False
            print(
                f"  {status} {stage['name']}: ID {existing_ids[0]}, "
                f"seq={stage_data['sequence']}, fold={stage_data['fold']}"
            )
        else:
            print(f"  [FAIL] {stage['name']}: NOT found")
            all_pass = False

    print("\n" + "=" * 60)
    if all_pass and project_ids:
        print("RESULT: All verifications PASSED")
    else:
        print("RESULT: Some verifications FAILED")
    print("=" * 60)


def rollback():
    """Remove Finance PPM project and canonical stages (use with caution)."""
    print("=" * 60)
    print("Rolling back Finance PPM configuration...")
    print("=" * 60)

    # Delete project
    project_ids = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "project.project",
        "search",
        [[("name", "=", FINANCE_PPM_PROJECT_NAME)]],
    )
    if project_ids:
        # Check for tasks first
        task_count = models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            "project.task",
            "search_count",
            [[("project_id", "in", project_ids)]],
        )
        if task_count > 0:
            print(f"[WARN] Project has {task_count} tasks - archive instead of delete")
            models.execute_kw(
                ODOO_DB,
                uid,
                ODOO_PASSWORD,
                "project.project",
                "write",
                [project_ids, {"active": False}],
            )
            print(f"Archived Finance PPM project: {project_ids}")
        else:
            models.execute_kw(
                ODOO_DB,
                uid,
                ODOO_PASSWORD,
                "project.project",
                "unlink",
                [project_ids],
            )
            print(f"Deleted Finance PPM project: {project_ids}")
    else:
        print("Finance PPM project not found - nothing to delete")

    # Delete stages (only if not in use)
    print("\nStage rollback:")
    for stage in STAGES:
        existing_ids = models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            "project.task.type",
            "search",
            [[("name", "=", stage["name"])]],
        )
        if existing_ids:
            # Check if stage has tasks
            task_count = models.execute_kw(
                ODOO_DB,
                uid,
                ODOO_PASSWORD,
                "project.task",
                "search_count",
                [[("stage_id", "in", existing_ids)]],
            )
            if task_count > 0:
                print(f"  [SKIP] {stage['name']}: {task_count} tasks using this stage")
            else:
                models.execute_kw(
                    ODOO_DB,
                    uid,
                    ODOO_PASSWORD,
                    "project.task.type",
                    "unlink",
                    [existing_ids],
                )
                print(f"  [DEL] {stage['name']}: deleted (ID {existing_ids[0]})")
        else:
            print(f"  [SKIP] {stage['name']}: not found")

    print("\n" + "=" * 60)
    print("Rollback complete")
    print("=" * 60)


def seed():
    """Create Finance PPM project and canonical stages."""
    print("=" * 60)
    print("Seeding Finance PPM configuration...")
    print("=" * 60)

    project_id = ensure_project(FINANCE_PPM_PROJECT_NAME)

    stage_ids = []
    for stage in STAGES:
        stage_id = ensure_stage(stage)
        stage_ids.append(stage_id)

    link_stages_to_project(stage_ids, project_id)

    print("\n" + "=" * 60)
    print("Seeding complete")
    print("=" * 60)


if __name__ == "__main__":
    mode = "seed"
    if len(sys.argv) > 1:
        mode = sys.argv[1].strip().lower()

    if mode == "seed":
        seed()
    elif mode == "verify":
        verify()
    elif mode == "rollback":
        rollback()
    else:
        sys.stderr.write("Usage: seed_finance_ppm_stages.py [seed|verify|rollback]\n")
        sys.exit(1)
