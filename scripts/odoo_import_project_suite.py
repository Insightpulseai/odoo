#!/usr/bin/env python3
"""
odoo_import_project_suite.py - Import projects/stages/tasks/calendar via JSON-RPC

Reads CSV files and imports into Odoo via JSON-RPC API:
- Projects
- Stages (project.task.type)
- Tasks (Pass A: parents, Pass B: children with parent linking)
- Calendar Events (optional, requires Calendar module)

Usage:
    export ODOO_URL="https://erp.example.com"
    export ODOO_DB="odoo"
    export ODOO_LOGIN="admin@example.com"
    export ODOO_PASSWORD="your_password"

    python3 scripts/odoo_import_project_suite.py \
        --projects data/odoo_import_month_end_projects.csv \
        --stages data/odoo_import_month_end_stages.csv \
        --tasks_parents data/odoo_import_month_end_tasks_PassA_parents.csv \
        --tasks_children data/odoo_import_month_end_tasks_PassB_children.csv \
        --calendar_events data/odoo_import_month_end_calendar_events.csv
"""

import argparse
import csv
import os
import re
import sys
from typing import Any, Dict, List, Optional

try:
    import requests
except ImportError:
    print("Error: requests is required. Install with: pip install requests")
    sys.exit(1)


# Module for external ID tracking
IMPORT_MODULE = "ipai_import"


class OdooClient:
    """JSON-RPC client for Odoo."""

    def __init__(self, url: str, db: str, login: str, password: str, timeout: int = 60):
        self.url = url.rstrip("/")
        self.db = db
        self.login = login
        self.password = password
        self.timeout = timeout
        self.s = requests.Session()
        self.uid = self._authenticate()

    def _jsonrpc(self, endpoint: str, payload: Dict[str, Any]) -> Any:
        """Execute JSON-RPC request."""
        r = self.s.post(f"{self.url}{endpoint}", json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(f"Odoo JSON-RPC error: {data['error']}")
        return data.get("result")

    def _authenticate(self) -> int:
        """Authenticate and return user ID."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "common",
                "method": "authenticate",
                "args": [self.db, self.login, self.password, {}],
            },
            "id": 1,
        }
        uid = self._jsonrpc("/jsonrpc", payload)
        if not uid:
            raise RuntimeError(
                "Authentication failed (check ODOO_DB/ODOO_LOGIN/ODOO_PASSWORD)."
            )
        return uid

    def call_kw(self, model: str, method: str, args=None, kwargs=None) -> Any:
        """Call model method via JSON-RPC."""
        args = args or []
        kwargs = kwargs or {}
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": model,
                "method": method,
                "args": args,
                "kwargs": kwargs,
            },
            "id": 1,
        }
        return self._jsonrpc(f"/web/dataset/call_kw/{model}/{method}", payload)

    def fields(self, model: str) -> Dict[str, Any]:
        """Get field definitions for a model."""
        return self.call_kw(model, "fields_get", [[], ["type", "string"]], {})


# -----------------------------
# Helpers
# -----------------------------
def read_csv(path: str) -> List[Dict[str, str]]:
    """Read CSV file into list of dicts."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def norm(s: str) -> str:
    """Normalize string value."""
    return (s or "").strip()


def yn_to_bool(v: str) -> Optional[bool]:
    """Convert Y/N string to boolean."""
    v = (v or "").strip().upper()
    if v in ("Y", "YES", "TRUE", "1"):
        return True
    if v in ("N", "NO", "FALSE", "0"):
        return False
    return None


def is_iso_date(s: str) -> bool:
    """Check if string is ISO date format."""
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", (s or "").strip()))


# -----------------------------
# External ID mapping via ir.model.data
# -----------------------------
def ir_model_data_get_res_id(
    odoo: OdooClient, model: str, ext_id: str
) -> Optional[int]:
    """Get resource ID from external ID."""
    ext_id = norm(ext_id)
    if not ext_id:
        return None
    ids = odoo.call_kw(
        "ir.model.data",
        "search",
        [
            [
                ["module", "=", IMPORT_MODULE],
                ["name", "=", ext_id],
                ["model", "=", model],
            ]
        ],
        {"limit": 1},
    )
    if not ids:
        return None
    rec = odoo.call_kw("ir.model.data", "read", [ids, ["res_id"]], {})
    return rec[0]["res_id"] if rec else None


def ir_model_data_set(odoo: OdooClient, model: str, ext_id: str, res_id: int) -> None:
    """Set or update external ID mapping."""
    ext_id = norm(ext_id)
    if not ext_id:
        return
    ids = odoo.call_kw(
        "ir.model.data",
        "search",
        [
            [
                ["module", "=", IMPORT_MODULE],
                ["name", "=", ext_id],
                ["model", "=", model],
            ]
        ],
        {"limit": 1},
    )
    vals = {"module": IMPORT_MODULE, "name": ext_id, "model": model, "res_id": res_id}
    if ids:
        odoo.call_kw("ir.model.data", "write", [ids, vals], {})
    else:
        odoo.call_kw("ir.model.data", "create", [vals], {})


# -----------------------------
# Upsert primitives
# -----------------------------
def upsert_project(
    odoo: OdooClient, row: Dict[str, str], project_fields: Dict[str, Any]
) -> int:
    """Upsert a project record."""
    name = norm(row.get("Project Name*"))
    if not name:
        raise ValueError("Projects CSV missing Project Name*")

    ext = norm(row.get("External ID (optional)"))
    existing = ir_model_data_get_res_id(odoo, "project.project", ext) if ext else None

    # Fallback: search by name
    if not existing:
        ids = odoo.call_kw(
            "project.project", "search", [[["name", "=", name]]], {"limit": 1}
        )
        existing = ids[0] if ids else None

    vals = {"name": name}

    # Optional fields
    privacy = norm(row.get("Privacy (private|internal|portal)"))
    if privacy and "privacy_visibility" in project_fields:
        vals["privacy_visibility"] = privacy

    allow_ts = yn_to_bool(row.get("Allow Timesheets (Y/N)"))
    if allow_ts is not None and "allow_timesheets" in project_fields:
        vals["allow_timesheets"] = allow_ts

    pm_email = norm(row.get("Project Manager Email (user_id/login)"))
    if pm_email and "user_id" in project_fields:
        uids = odoo.call_kw(
            "res.users", "search", [[["login", "=", pm_email]]], {"limit": 1}
        )
        if not uids:
            uids = odoo.call_kw(
                "res.users", "search", [[["email", "=", pm_email]]], {"limit": 1}
            )
        if uids:
            vals["user_id"] = uids[0]

    if existing:
        odoo.call_kw("project.project", "write", [[existing], vals], {})
        pid = existing
    else:
        pid = odoo.call_kw("project.project", "create", [vals], {})

    if ext:
        ir_model_data_set(odoo, "project.project", ext, pid)
    return pid


def upsert_stage(
    odoo: OdooClient,
    row: Dict[str, str],
    stage_fields: Dict[str, Any],
    project_name_to_id: Dict[str, int],
) -> int:
    """Upsert a stage record."""
    name = norm(row.get("Stage Name* (project.task.type/name)"))
    if not name:
        raise ValueError("Stages CSV missing Stage Name*")

    ext = norm(row.get("External ID (optional)"))
    existing = ir_model_data_get_res_id(odoo, "project.task.type", ext) if ext else None

    if not existing:
        ids = odoo.call_kw(
            "project.task.type", "search", [[["name", "=", name]]], {"limit": 1}
        )
        existing = ids[0] if ids else None

    vals = {"name": name}

    seq = norm(row.get("Sequence (number)"))
    if seq and "sequence" in stage_fields:
        try:
            vals["sequence"] = int(float(seq))
        except ValueError:
            pass

    fold = yn_to_bool(row.get("Folded in Kanban (Y/N) (fold)"))
    if fold is not None and "fold" in stage_fields:
        vals["fold"] = fold

    applies = norm(
        row.get(
            "Applies to Projects (comma-separated project names) (project_ids/name)"
        )
    )
    if applies and "project_ids" in stage_fields:
        pnames = [p.strip() for p in applies.split(",") if p.strip()]
        pids = [project_name_to_id[p] for p in pnames if p in project_name_to_id]
        if pids:
            vals["project_ids"] = [(6, 0, pids)]

    if existing:
        odoo.call_kw("project.task.type", "write", [[existing], vals], {})
        sid = existing
    else:
        sid = odoo.call_kw("project.task.type", "create", [vals], {})

    if ext:
        ir_model_data_set(odoo, "project.task.type", ext, sid)
    return sid


def resolve_users_by_emails(odoo: OdooClient, emails_csv: str) -> List[int]:
    """Resolve comma-separated emails to user IDs."""
    emails_csv = norm(emails_csv)
    if not emails_csv:
        return []
    # Skip placeholder emails
    if "<<MAP:" in emails_csv:
        return []
    emails = [e.strip() for e in emails_csv.split(",") if e.strip() and "@" in e]
    uids = []
    for e in emails:
        ids = odoo.call_kw("res.users", "search", [[["login", "=", e]]], {"limit": 1})
        if not ids:
            ids = odoo.call_kw(
                "res.users", "search", [[["email", "=", e]]], {"limit": 1}
            )
        if ids:
            uids.append(ids[0])
    return uids


def resolve_stage_id(odoo: OdooClient, stage_name: str) -> Optional[int]:
    """Resolve stage name to ID."""
    stage_name = norm(stage_name)
    if not stage_name:
        return None
    ids = odoo.call_kw(
        "project.task.type", "search", [[["name", "=", stage_name]]], {"limit": 1}
    )
    return ids[0] if ids else None


def resolve_tags(odoo: OdooClient, tags_csv: str) -> List[int]:
    """Resolve or create tags from comma-separated string."""
    tags_csv = norm(tags_csv)
    if not tags_csv:
        return []
    names = [t.strip() for t in tags_csv.split(",") if t.strip()]
    tag_ids = []
    for n in names:
        ids = odoo.call_kw("project.tags", "search", [[["name", "=", n]]], {"limit": 1})
        if ids:
            tag_ids.append(ids[0])
        else:
            tid = odoo.call_kw("project.tags", "create", [{"name": n}], {})
            tag_ids.append(tid)
    return tag_ids


def create_task(
    odoo: OdooClient,
    row: Dict[str, str],
    task_fields: Dict[str, Any],
    project_name_to_id: Dict[str, int],
) -> int:
    """Create or update a task."""
    name = norm(row.get("Task Name* (project.task/name)"))
    project_name = norm(row.get("Project Name* (project_id/name)"))
    if not name or not project_name:
        raise ValueError("Tasks CSV missing Task Name* or Project Name*")

    ext = norm(row.get("External ID (optional)"))
    existing = ir_model_data_get_res_id(odoo, "project.task", ext) if ext else None

    # Resolve project
    pid = project_name_to_id.get(project_name)
    if not pid:
        ids = odoo.call_kw(
            "project.project", "search", [[["name", "=", project_name]]], {"limit": 1}
        )
        if not ids:
            raise RuntimeError(f"Project not found: {project_name}")
        pid = ids[0]
        project_name_to_id[project_name] = pid

    vals: Dict[str, Any] = {"name": name, "project_id": pid}

    # Stage
    stage_name = norm(row.get("Stage Name (stage_id/name)"))
    sid = resolve_stage_id(odoo, stage_name) if stage_name else None
    if sid and "stage_id" in task_fields:
        vals["stage_id"] = sid

    # Assignees
    assignees = norm(row.get("Assignee Emails (comma-separated) (user_ids/login)"))
    uids = resolve_users_by_emails(odoo, assignees)
    if uids and "user_ids" in task_fields:
        vals["user_ids"] = [(6, 0, uids)]

    # Dates
    start = norm(row.get("Start Date (planned_date_begin or date_start)"))
    due = norm(row.get("Due Date (date_deadline)"))
    end = norm(row.get("End Date (planned_date_end) (optional)"))

    if is_iso_date(due) and "date_deadline" in task_fields:
        vals["date_deadline"] = due

    # Pick available start/end fields
    start_field = None
    for f in ("planned_date_begin", "date_start"):
        if f in task_fields:
            start_field = f
            break
    end_field = None
    for f in ("planned_date_end",):
        if f in task_fields:
            end_field = f
            break

    if is_iso_date(start) and start_field:
        vals[start_field] = start
    if is_iso_date(end) and end_field:
        vals[end_field] = end

    # Planned hours
    ph = norm(row.get("Planned Hours (planned_hours)"))
    if ph and "planned_hours" in task_fields:
        try:
            vals["planned_hours"] = float(ph)
        except ValueError:
            pass

    # Priority
    pr = norm(row.get("Priority (0-3)"))
    if pr and "priority" in task_fields:
        vals["priority"] = pr

    # Tags
    tags = norm(row.get("Tags (comma-separated) (tag_ids/name)"))
    tag_ids = resolve_tags(odoo, tags)
    if tag_ids and "tag_ids" in task_fields:
        vals["tag_ids"] = [(6, 0, tag_ids)]

    # Description
    desc = norm(row.get("Description (plain text)"))
    if desc and "description" in task_fields:
        vals["description"] = desc

    if existing:
        odoo.call_kw("project.task", "write", [[existing], vals], {})
        tid = existing
    else:
        tid = odoo.call_kw("project.task", "create", [vals], {})

    if ext:
        ir_model_data_set(odoo, "project.task", ext, tid)
    return tid


def set_task_parent(odoo: OdooClient, child_ext: str, parent_ext: str) -> None:
    """Set parent task on child task."""
    child_id = ir_model_data_get_res_id(odoo, "project.task", child_ext)
    parent_id = ir_model_data_get_res_id(odoo, "project.task", parent_ext)
    if not child_id or not parent_id:
        return
    odoo.call_kw("project.task", "write", [[child_id], {"parent_id": parent_id}], {})


def resolve_event_types(odoo: OdooClient, tags_csv: str) -> List[int]:
    """Resolve or create calendar event types."""
    tags_csv = norm(tags_csv)
    if not tags_csv:
        return []
    names = [t.strip() for t in tags_csv.split(",") if t.strip()]
    type_ids = []
    for n in names:
        ids = odoo.call_kw(
            "calendar.event.type", "search", [[["name", "=", n]]], {"limit": 1}
        )
        if ids:
            type_ids.append(ids[0])
        else:
            tid = odoo.call_kw("calendar.event.type", "create", [{"name": n}], {})
            type_ids.append(tid)
    return type_ids


def create_calendar_event(
    odoo: OdooClient, row: Dict[str, str], event_fields: Dict[str, Any]
) -> int:
    """Create a calendar event."""
    name = norm(row.get("Event Title* (calendar.event/name)"))
    if not name:
        raise ValueError("Calendar Events CSV missing Event Title*")

    ext = norm(row.get("External ID (optional)"))
    existing = ir_model_data_get_res_id(odoo, "calendar.event", ext) if ext else None

    allday = yn_to_bool(row.get("All Day (Y/N)"))
    start = norm(row.get("Start (YYYY-MM-DD)"))
    end = norm(row.get("End (YYYY-MM-DD)")) or start
    desc = norm(row.get("Description"))
    tags = norm(row.get("Tags (optional)"))

    vals: Dict[str, Any] = {"name": name}

    if allday is not None and "allday" in event_fields:
        vals["allday"] = allday

    # Prefer date fields if present
    if (
        "start_date" in event_fields
        and "stop_date" in event_fields
        and is_iso_date(start)
        and is_iso_date(end)
    ):
        vals["start_date"] = start
        vals["stop_date"] = end
    else:
        # Fallback to datetime fields
        if (
            "start" in event_fields
            and "stop" in event_fields
            and is_iso_date(start)
            and is_iso_date(end)
        ):
            vals["start"] = f"{start} 00:00:00"
            vals["stop"] = f"{end} 23:59:59"

    if desc and "description" in event_fields:
        vals["description"] = desc

    # Tagging
    if tags and "categ_ids" in event_fields:
        type_ids = resolve_event_types(odoo, tags)
        if type_ids:
            vals["categ_ids"] = [(6, 0, type_ids)]

    if existing:
        odoo.call_kw("calendar.event", "write", [[existing], vals], {})
        eid = existing
    else:
        eid = odoo.call_kw("calendar.event", "create", [vals], {})

    if ext:
        ir_model_data_set(odoo, "calendar.event", ext, eid)
    return eid


# -----------------------------
# Main import flow
# -----------------------------
def main():
    ap = argparse.ArgumentParser(description="Import project data to Odoo via JSON-RPC")
    ap.add_argument("--url", default=os.getenv("ODOO_URL", "https://localhost"))
    ap.add_argument("--db", default=os.getenv("ODOO_DB", "odoo"))
    ap.add_argument("--login", default=os.getenv("ODOO_LOGIN", ""))
    ap.add_argument("--password", default=os.getenv("ODOO_PASSWORD", ""))
    ap.add_argument("--projects", required=True, help="Projects CSV path")
    ap.add_argument("--stages", required=True, help="Stages CSV path")
    ap.add_argument(
        "--tasks_parents", required=True, help="Tasks (Pass A - parents) CSV path"
    )
    ap.add_argument(
        "--tasks_children", required=True, help="Tasks (Pass B - children) CSV path"
    )
    ap.add_argument(
        "--calendar_events", required=False, help="Calendar events CSV path (optional)"
    )
    ap.add_argument(
        "--dry_run", action="store_true", help="Validate without making changes"
    )
    args = ap.parse_args()

    if not args.login or not args.password:
        print("Error: Missing ODOO_LOGIN or ODOO_PASSWORD (env vars or flags).")
        sys.exit(1)

    print(f"Connecting to Odoo at {args.url}...")
    odoo = OdooClient(args.url, args.db, args.login, args.password)
    print(f"Authenticated as user ID: {odoo.uid}")

    project_fields = odoo.fields("project.project")
    stage_fields = odoo.fields("project.task.type")
    task_fields = odoo.fields("project.task")

    # Cache: project name -> id
    project_name_to_id: Dict[str, int] = {}

    # 1) Projects
    projects = read_csv(args.projects)
    print(f"\n[1/4] Projects: {len(projects)} rows")
    for row in projects:
        if args.dry_run:
            continue
        pid = upsert_project(odoo, row, project_fields)
        pname = norm(row.get("Project Name*"))
        if pname:
            project_name_to_id[pname] = pid
            print(f"  - {pname}: {pid}")

    # 2) Stages
    stages = read_csv(args.stages)
    print(f"\n[2/4] Stages: {len(stages)} rows")
    for row in stages:
        if args.dry_run:
            continue
        sid = upsert_stage(odoo, row, stage_fields, project_name_to_id)
        sname = norm(row.get("Stage Name* (project.task.type/name)"))
        print(f"  - {sname}: {sid}")

    # 3) Tasks - Parents
    parents = read_csv(args.tasks_parents)
    print(f"\n[3/4] Parent tasks: {len(parents)} rows")
    for row in parents:
        if args.dry_run:
            continue
        create_task(odoo, row, task_fields, project_name_to_id)

    # 4) Tasks - Children
    children = read_csv(args.tasks_children)
    print(f"\n[4/4] Child tasks: {len(children)} rows")
    for row in children:
        child_ext = norm(row.get("External ID (optional)"))
        parent_ext = norm(row.get("Parent Task External ID (optional parent_id/id)"))
        if args.dry_run:
            continue
        create_task(odoo, row, task_fields, project_name_to_id)
        if child_ext and parent_ext:
            set_task_parent(odoo, child_ext, parent_ext)

    # 5) Calendar Events (optional)
    if args.calendar_events:
        try:
            event_fields = odoo.fields("calendar.event")
            events = read_csv(args.calendar_events)
            print(f"\n[5/5] Calendar events: {len(events)} rows")
            for row in events:
                if args.dry_run:
                    continue
                create_calendar_event(odoo, row, event_fields)
        except Exception as e:
            print(
                f"\nWarning: Calendar import failed (Calendar module may not be installed): {e}"
            )

    # Verification summary
    print("\n=== VERIFICATION ===")
    for pname, pid in project_name_to_id.items():
        count = odoo.call_kw(
            "project.task", "search_count", [[["project_id", "=", pid]]], {}
        )
        print(f"- Project '{pname}': {count} tasks")

    if args.dry_run:
        print("\nDRY RUN: No changes were made.")
    else:
        print("\nImport completed successfully.")


if __name__ == "__main__":
    main()
