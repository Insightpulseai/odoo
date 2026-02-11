#!/usr/bin/env python3
import os
import sys
import xmlrpc.client

ODOO_URL = os.environ.get("ODOO_URL")
ODOO_DB = os.environ.get("ODOO_DB")
ODOO_USER = os.environ.get("ODOO_USER")
ODOO_PASS = os.environ.get("ODOO_PASS")

if not all([ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASS]):
    print("Missing env vars. Required: ODOO_URL ODOO_DB ODOO_USER ODOO_PASS", file=sys.stderr)
    sys.exit(2)

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
if not uid:
    print("Auth failed.", file=sys.stderr)
    sys.exit(3)

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

def search(model, domain, limit=None):
    kw = {}
    if limit is not None:
        kw["limit"] = limit
    return models.execute_kw(ODOO_DB, uid, ODOO_PASS, model, "search", [domain], kw)

def read(model, ids, fields):
    return models.execute_kw(ODOO_DB, uid, ODOO_PASS, model, "read", [ids], {"fields": fields})

def create(model, vals):
    return models.execute_kw(ODOO_DB, uid, ODOO_PASS, model, "create", [vals])

def write(model, ids, vals):
    return models.execute_kw(ODOO_DB, uid, ODOO_PASS, model, "write", [ids, vals])

def ensure_project(name: str) -> int:
    ids = search("project.project", [["name", "=", name]], limit=1)
    if ids:
        return ids[0]
    return create("project.project", {"name": name})

def ensure_stage(project_id: int, name: str, sequence: int, fold: bool=False) -> int:
    # stage already linked to this project?
    ids = search("project.task.type", [["name", "=", name], ["project_ids", "in", [project_id]]], limit=1)
    if ids:
        sid = ids[0]
        # ensure seq/fold are aligned (idempotent correction)
        write("project.task.type", [sid], {"sequence": sequence, "fold": fold})
        return sid

    # stage exists globally? reuse & link
    global_ids = search("project.task.type", [["name", "=", name]], limit=1)
    if global_ids:
        sid = global_ids[0]
        write("project.task.type", [sid], {"project_ids": [(4, project_id)], "sequence": sequence, "fold": fold})
        return sid

    # create new
    return create("project.task.type", {"name": name, "sequence": sequence, "fold": fold, "project_ids": [(4, project_id)]})

def ensure_pipeline(project_name: str, stages: list[tuple[str,int,bool]]):
    pid = ensure_project(project_name)
    for (name, seq, fold) in stages:
        ensure_stage(pid, name, seq, fold)
    return pid

def main():
    # Month-End Closing stages (from your sheet: Preparation, Review, Approval, Done)
    month_end_id = ensure_pipeline(
        "Month-End Closing",
        [("Preparation", 10, False),
         ("Review", 20, False),
         ("Approval", 30, False),
         ("Done", 40, True)]
    )

    # BIR Tax Filing stages (from your sheet: Prep, Report Approval, Payment Approval, Filing & Payment)
    bir_id = ensure_pipeline(
        "BIR Tax Filing",
        [("Preparation", 10, False),
         ("Report Approval", 20, False),
         ("Payment Approval", 30, False),
         ("Filing & Payment", 40, False),
         ("Done", 50, True)]
    )

    rows = read("project.project", [month_end_id, bir_id], ["id", "name"])
    print("OK: ensured projects")
    for r in rows:
        print(f"- {r['id']}: {r['name']}")

if __name__ == "__main__":
    main()
