import xmlrpc.client
import ssl
import csv
import os
import sys
import json
import hashlib
import zipfile
import shutil
from datetime import datetime
import argparse

# --- CONFIG & SECURITY ---
# NO HARDCODED CREDS allowed.
# We default DB only for convenience if not provided, but never user/pass.

DEFAULT_DB = "odoo_core"


def get_env_or_fail(key):
    val = os.environ.get(key)
    if not val:
        print(f"BLOCKED: Missing required environment variable {key}")
        sys.exit(1)
    return val


def redact(val):
    if not val:
        return "None"
    if len(val) < 4:
        return "***"
    return val[:2] + "***" + val[-1:]


def get_file_checksum(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_script_checksum():
    return get_file_checksum(__file__)


def run(dry_run=False):
    # 1. SETUP
    run_ts = datetime.utcnow().isoformat() + "Z"

    # Args
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        dry_run = True

    # Auth Config
    url = os.environ.get("ODOO_URL", "https://erp.insightpulseai.com").rstrip("/")
    db = os.environ.get("ODOO_DB", DEFAULT_DB)

    if dry_run:
        print("DRY RUN: Skipping authentication checks.")
        user = "dry_run_user"
        password = "dry_run_password"
    else:
        user = get_env_or_fail("ODOO_USER")
        password = get_env_or_fail("ODOO_PASSWORD")

    # Output Paths
    base_artifact_dir = "artifacts/seed_export"
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(base_artifact_dir, run_id)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    print(f"--- REMOTE EXTRACTION START ---")
    print(f"Run ID: {run_id}")
    print(f"Target: {url} | DB: {db} | User: {redact(user)}")

    manifest = {
        "run_id": run_id,
        "run_utc": run_ts,
        "odoo_url": url,
        "db_name": db,
        "username_redacted": redact(user),
        "script_checksum": get_script_checksum(),
        "status": "pending",
        "extracted_models": [],
        "artifacts": [],
    }

    # 2. CONNECT
    uid = None
    common = None
    models = None

    if not dry_run:
        try:
            context = ssl._create_unverified_context()
            common = xmlrpc.client.ServerProxy(
                f"{url}/xmlrpc/2/common", context=context
            )
            models = xmlrpc.client.ServerProxy(
                f"{url}/xmlrpc/2/object", context=context
            )

            uid = common.authenticate(db, user, password, {})
            if not uid:
                print("CRITICAL FAILURE: Authentication failed via RPC.")
                sys.exit(1)

            print(f"RPC SUCCESS: Authenticated as UID {uid}")

        except Exception as e:
            print(f"RPC ERROR: {e}")
            sys.exit(1)
    else:
        uid = 999
        print("DRY RUN: Simulated UID 999")

    # 3. EXTRACTION LOGIC
    # Target Projects
    target_projects = [
        "BIR Tax Filing",
        "Month-End Close Template",
        "Month-end closing",
    ]
    ids_to_export = []
    project_map = {}

    if not dry_run:
        # Find Projects
        for name in target_projects:
            # Exact match
            ids = models.execute_kw(
                db, uid, password, "project.project", "search", [[["name", "=", name]]]
            )
            if not ids:
                # ILIKE
                ids = models.execute_kw(
                    db,
                    uid,
                    password,
                    "project.project",
                    "search",
                    [[["name", "ilike", name]]],
                )

            if ids:
                p_data = models.execute_kw(
                    db,
                    uid,
                    password,
                    "project.project",
                    "read",
                    [ids],
                    {"fields": ["name"]},
                )
                for p in p_data:
                    project_map[p["id"]] = p["name"]
                    ids_to_export.append(p["id"])

    # 4. FETCH TASKS
    tasks = []
    task_fields = [
        "name",
        "project_id",
        "stage_id",
        "user_ids",
        "tag_ids",
        "date_deadline",
        "description",
        "priority",
        "sequence",
        "parent_id",
        "company_id",
        "active",
    ]

    if ids_to_export and not dry_run:
        domain = [["project_id", "in", ids_to_export], ["active", "in", [True, False]]]
        tasks = models.execute_kw(
            db,
            uid,
            password,
            "project.task",
            "search_read",
            [domain],
            {"fields": task_fields},
        )

        manifest["extracted_models"].append(
            {"model": "project.task", "count": len(tasks), "domain": str(domain)}
        )
        print(f"EXTRACTED: {len(tasks)} records from project.task")

    # 5. PROCESS DATA & REFERENCES
    rows = []
    ref_projects = set()
    ref_stages = set()
    ref_tags = set()
    ref_users = set()

    for t in tasks:
        # Resolve Relations (M2O is [id, name], M2M is [id, id, ...])
        pid = t["project_id"][0] if t["project_id"] else ""
        pname = t["project_id"][1] if t["project_id"] else ""
        if pid:
            ref_projects.add((pid, pname))

        sid = t["stage_id"][0] if t["stage_id"] else ""
        sname = t["stage_id"][1] if t["stage_id"] else ""
        if sid:
            ref_stages.add((sid, sname))

        # Collect IDs for batch fetch
        for u in t.get("user_ids", []):
            ref_users.add(u)
        for tag in t.get("tag_ids", []):
            ref_tags.add(tag)

        row = {
            "id": t["id"],
            "name": t["name"],
            "project_id": pid,
            "project_name": pname,
            "stage_id": sid,
            "stage_name": sname,
            "active": t["active"],
            "priority": t["priority"],
            "sequence": t["sequence"],
            "date_deadline": t["date_deadline"],
            "parent_id": t["parent_id"][0] if t["parent_id"] else "",
            "parent_name": t["parent_id"][1] if t["parent_id"] else "",
            "company_id": t["company_id"][0] if t["company_id"] else "",
            "description": t["description"] or "",
            # Placeholders
            "user_ids_raw": t.get("user_ids", []),
            "tag_ids_raw": t.get("tag_ids", []),
        }
        rows.append(row)

    # Batch Fetch References
    user_map = {}
    tag_map = {}

    if not dry_run:
        if ref_users:
            udata = models.execute_kw(
                db,
                uid,
                password,
                "res.users",
                "read",
                [list(ref_users)],
                {"fields": ["name", "login"]},
            )
            for u in udata:
                user_map[u["id"]] = u["login"]

        if ref_tags:
            tdata = models.execute_kw(
                db,
                uid,
                password,
                "project.tags",
                "read",
                [list(ref_tags)],
                {"fields": ["name", "color"]},
            )
            for tag in tdata:
                tag_map[tag["id"]] = tag["name"]

    # Finalize Rows
    final_rows = []
    for r in rows:
        ulogins = [user_map.get(u, "") for u in r["user_ids_raw"]]
        tnames = [tag_map.get(t, "") for t in r["tag_ids_raw"]]

        r["user_logins"] = ",".join(filter(None, ulogins))
        r["tag_names"] = ",".join(filter(None, tnames))

        # Cleanup internal keys
        del r["user_ids_raw"]
        del r["tag_ids_raw"]
        final_rows.append(r)

    # 6. WRITE ARTIFACTS
    def write_csv(filename, data, headers):
        path = os.path.join(out_dir, filename)
        with open(path, "w", newline="", encoding="utf-8") as f:
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                w = csv.DictWriter(f, fieldnames=headers)
                w.writeheader()
                w.writerows(data)
            else:
                w = csv.writer(f)
                w.writerow(headers)
                w.writerows(data)

        csum = get_file_checksum(path)
        manifest["artifacts"].append({"name": filename, "sha256": csum})
        return path

    # Tasks
    task_headers = [
        "id",
        "name",
        "project_id",
        "project_name",
        "stage_id",
        "stage_name",
        "active",
        "priority",
        "sequence",
        "date_deadline",
        "parent_id",
        "parent_name",
        "company_id",
        "description",
        "user_logins",
        "tag_names",
    ]
    write_csv("tasks.csv", final_rows, task_headers)

    # Aux
    write_csv("projects.csv", list(ref_projects), ["id", "name"])
    write_csv("stages.csv", list(ref_stages), ["id", "name"])
    write_csv("tags.csv", [[k, v] for k, v in tag_map.items()], ["id", "name"])
    write_csv("users.csv", [[k, v] for k, v in user_map.items()], ["id", "login"])

    # Manifest
    manifest["status"] = "success"
    manifest_path = os.path.join(out_dir, "MANIFEST.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # Checksums File
    with open(os.path.join(out_dir, "CHECKSUMS.txt"), "w") as f:
        for art in manifest["artifacts"]:
            f.write(f"{art['sha256']}  {art['name']}\n")

    # Zip
    zip_path = os.path.join(base_artifact_dir, f"{run_id}_full_export.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(out_dir):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    os.path.relpath(
                        os.path.join(root, file), os.path.join(out_dir, "..")
                    ),
                )

    # Symlink Latest
    latest_link = os.path.join(base_artifact_dir, "latest")
    if os.path.exists(latest_link):
        os.remove(latest_link)
    # Symlink might fail on basic Windows, but standard on Mac/Linux
    try:
        os.symlink(run_id, latest_link)
    except OSError:
        pass  # Ignore if FS doesn't support

    print(f"SUCCESS: Artifacts in {out_dir}")
    print(f"Archive: {zip_path}")

    # 7. VERIFICATION OUTPUT
    print("\n--- VERIFICATION REPORT ---")
    counts = {}
    for r in final_rows:
        p = r["project_name"]
        if p not in counts:
            counts[p] = {"total": 0, "active": 0}
        counts[p]["total"] += 1
        if r["active"]:
            counts[p]["active"] += 1

    print(f"{'PROJECT':<30} | {'TOTAL':<6} | {'ACTIVE':<6}")
    print("-" * 50)
    for p, d in counts.items():
        print(f"{p:<30} | {d['total']:<6} | {d['active']:<6}")


if __name__ == "__main__":
    run()
