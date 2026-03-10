#!/usr/bin/env python3
"""
Create Month-End Closing and BIR Tax Filing projects with proper stages.

Usage:
    export ODOO_URL="https://erp.insightpulseai.com"
    export ODOO_DB="odoo"
    export ODOO_USER="admin@Insightpulseai"
    export ODOO_PASS="***"
    python3 create_projects_monthend_bir.py
"""

import os
import sys
import xmlrpc.client

ODOO_URL = os.environ.get("ODOO_URL")
ODOO_DB = os.environ.get("ODOO_DB")
ODOO_USER = os.environ.get("ODOO_USER")
ODOO_PASS = os.environ.get("ODOO_PASS")

if not all([ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASS]):
    print(
        "Missing env vars. Required: ODOO_URL ODOO_DB ODOO_USER ODOO_PASS",
        file=sys.stderr,
    )
    sys.exit(2)

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
if not uid:
    print("Auth failed. Check ODOO_DB/ODOO_USER/ODOO_PASS.", file=sys.stderr)
    sys.exit(3)

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")


def search(model, domain, limit=None):
    kwargs = {}
    if limit is not None:
        kwargs["limit"] = limit
    return models.execute_kw(ODOO_DB, uid, ODOO_PASS, model, "search", [domain], kwargs)


def read(model, ids, fields):
    return models.execute_kw(
        ODOO_DB, uid, ODOO_PASS, model, "read", [ids], {"fields": fields}
    )


def create(model, vals):
    return models.execute_kw(ODOO_DB, uid, ODOO_PASS, model, "create", [vals])


def write(model, ids, vals):
    return models.execute_kw(ODOO_DB, uid, ODOO_PASS, model, "write", [ids, vals])


def ensure_project(name: str) -> int:
    ids = search("project.project", [["name", "=", name]], limit=1)
    if ids:
        return ids[0]
    return create("project.project", {"name": name})


def ensure_stages_for_project(
    project_id: int, stage_names: list[str]
) -> dict[str, int]:
    """
    Creates project.task.type stages and links them to project via project_ids M2M.
    Returns {stage_name: stage_id}
    """
    out = {}
    for s in stage_names:
        # search stage with same name already linked to this project
        stage_ids = search(
            "project.task.type",
            [["name", "=", s], ["project_ids", "in", [project_id]]],
            limit=1,
        )
        if stage_ids:
            out[s] = stage_ids[0]
            continue

        # if stage name exists globally, reuse it and link to project
        global_ids = search("project.task.type", [["name", "=", s]], limit=1)
        if global_ids:
            sid = global_ids[0]
            # link to project (add)
            write("project.task.type", [sid], {"project_ids": [(4, project_id)]})
            out[s] = sid
            continue

        # create new stage and link
        sid = create("project.task.type", {"name": s, "project_ids": [(4, project_id)]})
        out[s] = sid

    return out


def main():
    # Project 1: Month-End Closing
    p_monthend = ensure_project("Month-End Closing")
    ensure_stages_for_project(p_monthend, ["Preparation", "Review", "Approval", "Done"])

    # Project 2: BIR Tax Filing
    p_bir = ensure_project("BIR Tax Filing")
    ensure_stages_for_project(
        p_bir,
        [
            "Preparation",
            "Report Approval",
            "Payment Approval",
            "Filing & Payment",
            "Done",
        ],
    )

    # Print summary
    projs = read("project.project", [p_monthend, p_bir], ["id", "name"])
    print("OK: projects ensured:")
    for p in projs:
        print(f"- {p['id']}: {p['name']}")


if __name__ == "__main__":
    main()
