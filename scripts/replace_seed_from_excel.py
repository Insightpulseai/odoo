import pandas as pd
import xmlrpc.client
import ssl
import csv
import os
import sys
import json
import hashlib
import zipfile
import argparse
import re
from datetime import datetime

# --- CONFIG ---
DEFAULT_DB = "odoo_core"
SHEET_NAME_TASKS = "Sheet1"  # Default, will attempt to find better if needed


def get_env_or_fail(key):
    val = os.environ.get(key)
    if not val:
        print(f"BLOCKED: Missing required environment variable {key}")
        sys.exit(1)
    return val


def clean_slug(text):
    if not text:
        return ""
    # Lowercase, replace non-alnum with underscore, collapse
    s = str(text).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:80]


def parse_closing_tasks(df):
    records = []
    # Fill down 'Task Category'
    if "Task Category" in df.columns:
        df["Task Category"] = df["Task Category"].ffill()

    start_date = datetime(2026, 1, 1)  # Default baseline for relative dates if any

    for idx, row in df.iterrows():
        cat = str(row.get("Task Category", "")).strip()
        task_name = str(row.get("Detailed Monthly Tasks", "")).strip()
        if not task_name or task_name.lower() == "nan":
            continue

        emp_code = str(row.get("Employee Code", "")).strip()
        if emp_code.lower() == "nan":
            emp_code = ""

        # Project is Month-end closing usually, but maybe Category splits it?
        # User said "Month-End Close Template" and "Month-end closing".
        # Let's map all to "Month-end closing" as the active project.
        proj = "Month-end closing"

        records.append(
            {
                "project_name": proj,
                "task_name": task_name,
                "description": f"Category: {cat}",
                "stage_name": "New",
                "user_raw": emp_code,
                "active": True,
                "date_deadline": None,
            }
        )
    return records


def parse_tax_filing(df):
    records = []
    # Cols: BIR Form, Period Covered, BIR Filing & Payment Deadline (2026)
    for idx, row in df.iterrows():
        form = str(row.get("BIR Form", "")).strip()
        period = str(row.get("Period Covered", "")).strip()

        # Filter Junk
        if not form or form.lower() in ["nan", "nat", "none"]:
            continue
        if "bir form" in form.lower():
            continue  # Header row
        if "step" in form.lower() and "process" in form.lower():
            continue  # Instruction row

        # Name: Form - Period
        if period and period.lower() not in ["nan", "nat", "none"]:
            task_name = f"{form} - {period}"
        else:
            task_name = form

        # Deadline
        deadline_raw = row.get("BIR Filing & Payment Deadline (2026)")
        deadline = None

        # Robust parsing
        if pd.notnull(deadline_raw):
            try:
                dt = pd.to_datetime(deadline_raw, errors="coerce")
                if pd.notnull(dt):
                    deadline = dt.strftime("%Y-%m-%d")
            except Exception:
                pass

        records.append(
            {
                "project_name": "BIR Tax Filing",
                "task_name": task_name,
                "description": f"Form: {form}, Period: {period}",
                "stage_name": "New",
                "user_raw": "",
                "active": True,
                "date_deadline": deadline,
            }
        )
    return records

    return records


def generate_ref_ids(rec):
    # project: seed_project__{slug}
    # task: seed_task__{slug_proj}__{slug_task}
    p_slug = clean_slug(rec["project_name"])
    t_slug = clean_slug(rec["task_name"])

    rec["xid_project"] = f"seed_project__{p_slug}"
    # Hash suffix for task to avoid collisions if names identical?
    # User said: "last write wins", so collision is OK, same XID.
    rec["xid_task"] = f"seed_task__{p_slug}__{t_slug}"

    return rec


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--excel", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--build-only", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--mode", default="upsert")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    # 1. PARSE
    print(f"Reading {args.excel}...")
    normalized = []

    # Sheet: Closing Task
    try:
        df_close = pd.read_excel(args.excel, sheet_name="Closing Task")
        print(f"Loaded 'Closing Task': {len(df_close)} rows")
        normalized.extend(parse_closing_tasks(df_close))
    except Exception as e:
        print(f"WARN: Could not read 'Closing Task': {e}")

    # Sheet: Tax Filing
    try:
        df_tax = pd.read_excel(args.excel, sheet_name="Tax Filing")
        print(f"Loaded 'Tax Filing': {len(df_tax)} rows")
        normalized.extend(parse_tax_filing(df_tax))
    except Exception as e:
        print(f"WARN: Could not read 'Tax Filing': {e}")

    print(f"Total parsed task rows: {len(normalized)}")

    # 2. ENRICH XIDs
    processed = [generate_ref_ids(r) for r in normalized]

    # 3. BUILD ARTIFACTS
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out, run_id)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Projects
    projects = {}
    for r in processed:
        projects[r["xid_project"]] = r["project_name"]

    # CSV Writers
    # Projects
    with open(os.path.join(out_dir, "projects.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["xid", "name"])
        for xid, name in projects.items():
            w.writerow([xid, name])

    # Tasks
    with open(os.path.join(out_dir, "tasks.csv"), "w", newline="") as f:
        fieldnames = [
            "xid_task",
            "xid_project",
            "task_name",
            "description",
            "stage_name",
            "user_raw",
            "active",
            "date_deadline",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in processed:
            row = {k: r.get(k) for k in fieldnames}
            w.writerow(row)

    # Manifest
    manifest = {
        "run_id": run_id,
        "source": os.path.basename(args.excel),
        "counts": {"projects": len(projects), "tasks": len(processed)},
        "artifacts": ["projects.csv", "tasks.csv"],
    }
    with open(os.path.join(out_dir, "MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    # Checksums
    with open(os.path.join(out_dir, "CHECKSUMS.txt"), "w") as f:
        for fname in manifest["artifacts"]:
            # simple sha calculation
            p = os.path.join(out_dir, fname)
            with open(p, "rb") as rf:
                d = rf.read()
                h = hashlib.sha256(d).hexdigest()
                f.write(f"{h}  {fname}\n")

    # Zip
    zip_path = os.path.join(args.out, f"{run_id}_seed.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        for fname in manifest["artifacts"] + ["MANIFEST.json", "CHECKSUMS.txt"]:
            zf.write(os.path.join(out_dir, fname), fname)

    print(f"Artifacts built in {out_dir}")
    print(f"Zip: {zip_path}")

    if args.build_only:
        return

    # 4. APPLY / UPSERT
    if not args.apply:
        print("Skipping apply (use --apply).")
        return

    # Connection
    url = os.environ.get("ODOO_URL", "https://erp.insightpulseai.net").rstrip("/")
    db = os.environ.get("ODOO_DB", DEFAULT_DB)

    if args.dry_run:
        print(f"DRY RUN: Would connect to {url} / {db}")
    else:
        user = get_env_or_fail("ODOO_USER")
        password = get_env_or_fail("ODOO_PASSWORD")

        context = ssl._create_unverified_context()
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", context=context)
        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", context=context)

        uid = common.authenticate(db, user, password, {})
        if not uid:
            print("AUTH FAILED")
            sys.exit(1)
        print(f"Authenticated as UID {uid}")

    # --- UPSERT LOGIC ---
    # Helper for XID
    def get_or_create_xml_id(model, xid, dry_run_mode):
        if dry_run_mode:
            return 999

        # Check ir.model.data
        module, name = "seed_replace", xid
        # Split logic if xid has specialized prefix? User said: "seed_project__slug"
        # We can treat entire XID as name, module as 'seed_replace'

        # Search
        res = models.execute_kw(
            db,
            uid,
            password,
            "ir.model.data",
            "search_read",
            [[["module", "=", module], ["name", "=", name]]],
            {"fields": ["res_id"]},
        )
        if res:
            return res[0]["res_id"]
        return None

    def record_xml_id(model, res_id, xid):
        if args.dry_run:
            return
        module, name = "seed_replace", xid
        models.execute_kw(
            db,
            uid,
            password,
            "ir.model.data",
            "create",
            [
                {
                    "module": module,
                    "name": name,
                    "model": model,
                    "res_id": res_id,
                    "noupdate": True,
                }
            ],
        )

    # 1. UPSERT PROJECTS
    for xid, pname in projects.items():
        rid = get_or_create_xml_id("project.project", xid, args.dry_run)
        vals = {"name": pname}

        if rid:
            print(f"UPDATE Project {xid} -> ID {rid}")
            if not args.dry_run:
                models.execute_kw(
                    db, uid, password, "project.project", "write", [[rid], vals]
                )
        else:
            print(f"CREATE Project {xid}")
            if not args.dry_run:
                rid = models.execute_kw(
                    db, uid, password, "project.project", "create", [vals]
                )
                record_xml_id("project.project", rid, xid)

    # 2. UPSERT TASKS
    for r in processed:
        pxid = r["xid_project"]
        txid = r["xid_task"]

        # Resolve Project ID
        pid = get_or_create_xml_id("project.project", pxid, args.dry_run)

        # Val
        vals = {
            "name": r["task_name"],
            "project_id": pid,
            "description": r["description"],
            # Stage? User said 'New', but we need stage_id.
            # If we don't map stage XIDs, we can search by name or leave default
        }

        if r.get("date_deadline"):
            vals["date_deadline"] = r["date_deadline"]

        tid = get_or_create_xml_id("project.task", txid, args.dry_run)
        if tid:
            print(f"UPDATE Task {txid} -> ID {tid}")
            if not args.dry_run:
                models.execute_kw(
                    db, uid, password, "project.task", "write", [[tid], vals]
                )
        else:
            print(f"CREATE Task {txid}")
            if not args.dry_run:
                tid = models.execute_kw(
                    db, uid, password, "project.task", "create", [vals]
                )
                record_xml_id("project.task", tid, txid)

    print("Upsert Complete.")


if __name__ == "__main__":
    run()
