#!/usr/bin/env python3
"""
generate_month_end_imports.py - Generate Odoo import CSVs from Month-end workbook

Reads Month-end Closing Task and Tax Filing workbook and generates
import-ready CSVs for Projects, Stages, Tasks (Pass A/B), and Calendar Events.

Uses all sheets:
- "Closing Task" (matrix) -> assignee defaults per stage
- "Closing Task - Gannt Chart" -> task schedule
- "Tax Filing" -> BIR filing tasks with stages
- "Holidays & Calendar" -> calendar events

Usage:
    python3 scripts/generate_month_end_imports.py \
        --workbook data/source.xlsx \
        --outdir data \
        --user_map data/user_map.csv
"""

import argparse
import csv
import os
import re
from typing import Dict, List, Optional

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is required. Install with: pip install pandas openpyxl")
    raise SystemExit(1)


def slug(s: str) -> str:
    """Convert string to URL-safe slug."""
    s = str(s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:60] if s else "x"


def fmt_date(v) -> str:
    """Format value as ISO date string."""
    if pd.isna(v):
        return ""
    d = pd.to_datetime(v, errors="coerce")
    if pd.isna(d):
        return ""
    return d.date().isoformat()


def is_nonempty(v) -> bool:
    """Check if value is non-empty."""
    if pd.isna(v):
        return False
    s = str(v).strip()
    return s != "" and s.lower() != "nan"


def write_csv(path: str, rows: List[Dict], fieldnames: List[str]) -> None:
    """Write rows to CSV file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def read_user_map(path: Optional[str]) -> Dict[str, str]:
    """
    Read employee code to email mapping from CSV.

    Expected columns: employee_code, email
    """
    if not path or not os.path.exists(path):
        return {}
    mp = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            code = (r.get("employee_code") or "").strip()
            email = (r.get("email") or "").strip()
            if code and email:
                mp[code] = email
    return mp


def normalize_assignee_cell(cell, code_to_email: Dict[str, str]) -> str:
    """
    Normalize assignee cell value to comma-separated emails.

    Handles:
    - Direct emails
    - Employee codes (mapped via code_to_email)
    - Y/Yes/True values (treated as blank)
    - Comma-separated values
    """
    if not is_nonempty(cell):
        return ""
    s = str(cell).strip()

    # Y/Yes means "stage exists but no assignee specified"
    if s.upper() in ("Y", "YES", "TRUE", "1"):
        return ""

    parts = [p.strip() for p in s.split(",") if p.strip()]
    out = []
    for p in parts:
        if "@" in p:
            out.append(p)
        elif p in code_to_email:
            out.append(code_to_email[p])
        else:
            # Keep as placeholder for manual mapping
            out.append(f"<<MAP:{p}>>")

    # De-duplicate while preserving order
    seen = set()
    dedup = []
    for e in out:
        if e not in seen:
            seen.add(e)
            dedup.append(e)
    return ",".join(dedup)


def main():
    ap = argparse.ArgumentParser(
        description="Generate Odoo import CSVs from Month-end workbook"
    )
    ap.add_argument(
        "--workbook",
        required=True,
        help="Path to Month-end Closing Task and Tax Filing workbook (.xlsx)",
    )
    ap.add_argument(
        "--outdir",
        default="data",
        help="Output directory for generated CSVs (default: data)",
    )
    ap.add_argument(
        "--user_map", default="", help="Optional CSV mapping employee_code->email"
    )
    ap.add_argument(
        "--project_close",
        default="Month-end Close",
        help="Name for Month-end Close project",
    )
    ap.add_argument(
        "--project_tax", default="Tax Filing", help="Name for Tax Filing project"
    )
    args = ap.parse_args()

    code_to_email = read_user_map(args.user_map)
    wb = args.workbook
    outdir = args.outdir
    P_CLOSE = args.project_close
    P_TAX = args.project_tax

    print(f"Reading workbook: {wb}")

    # Read sheets
    try:
        closing_matrix = pd.read_excel(wb, sheet_name="Closing Task")
        closing_gantt = pd.read_excel(wb, sheet_name="Closing Task - Gannt Chart")
        tax = pd.read_excel(wb, sheet_name="Tax Filing")
        hol = pd.read_excel(wb, sheet_name="Holidays & Calendar")
    except Exception as e:
        print(f"Error reading workbook: {e}")
        raise SystemExit(1)

    # -----------------------------
    # Projects
    # -----------------------------
    projects_fields = [
        "External ID (optional)",
        "Project Name*",
        "Company (Name)",
        "Customer (Name)",
        "Project Manager Email (user_id/login)",
        "Privacy (private|internal|portal)",
        "Allow Timesheets (Y/N)",
        "Analytic Account (Name) (optional)",
        "Default Stages (comma-separated stage names) (optional note)",
    ]
    projects_rows = [
        {
            "External ID (optional)": "proj_month_end_close",
            "Project Name*": P_CLOSE,
            "Company (Name)": "",
            "Customer (Name)": "",
            "Project Manager Email (user_id/login)": "",
            "Privacy (private|internal|portal)": "internal",
            "Allow Timesheets (Y/N)": "Y",
            "Analytic Account (Name) (optional)": "",
            "Default Stages (comma-separated stage names) (optional note)": "Preparation, Review, Approval, Done",
        },
        {
            "External ID (optional)": "proj_tax_filing",
            "Project Name*": P_TAX,
            "Company (Name)": "",
            "Customer (Name)": "",
            "Project Manager Email (user_id/login)": "",
            "Privacy (private|internal|portal)": "internal",
            "Allow Timesheets (Y/N)": "N",
            "Analytic Account (Name) (optional)": "",
            "Default Stages (comma-separated stage names) (optional note)": "Preparation, Review, Approval, Done",
        },
    ]

    # -----------------------------
    # Stages
    # -----------------------------
    stages_fields = [
        "External ID (optional)",
        "Stage Name* (project.task.type/name)",
        "Sequence (number)",
        "Folded in Kanban (Y/N) (fold)",
        "Applies to Projects (comma-separated project names) (project_ids/name)",
    ]
    stages_rows = [
        {
            "External ID (optional)": "stage_preparation",
            "Stage Name* (project.task.type/name)": "Preparation",
            "Sequence (number)": 1,
            "Folded in Kanban (Y/N) (fold)": "N",
            "Applies to Projects (comma-separated project names) (project_ids/name)": f"{P_CLOSE},{P_TAX}",
        },
        {
            "External ID (optional)": "stage_review",
            "Stage Name* (project.task.type/name)": "Review",
            "Sequence (number)": 2,
            "Folded in Kanban (Y/N) (fold)": "N",
            "Applies to Projects (comma-separated project names) (project_ids/name)": f"{P_CLOSE},{P_TAX}",
        },
        {
            "External ID (optional)": "stage_approval",
            "Stage Name* (project.task.type/name)": "Approval",
            "Sequence (number)": 3,
            "Folded in Kanban (Y/N) (fold)": "N",
            "Applies to Projects (comma-separated project names) (project_ids/name)": f"{P_CLOSE},{P_TAX}",
        },
        {
            "External ID (optional)": "stage_done",
            "Stage Name* (project.task.type/name)": "Done",
            "Sequence (number)": 4,
            "Folded in Kanban (Y/N) (fold)": "Y",
            "Applies to Projects (comma-separated project names) (project_ids/name)": f"{P_CLOSE},{P_TAX}",
        },
    ]

    # -----------------------------
    # Matrix defaults: Detailed Monthly Tasks -> stage emails
    # -----------------------------
    matrix_defaults: Dict[str, Dict[str, str]] = {}
    if "Detailed Monthly Tasks" in closing_matrix.columns:
        cm = closing_matrix.dropna(subset=["Detailed Monthly Tasks"])
        for _, r in cm.iterrows():
            detailed = str(r.get("Detailed Monthly Tasks", "")).strip()
            if not detailed:
                continue
            matrix_defaults[detailed] = {
                "Preparation": normalize_assignee_cell(
                    r.get("Preparation", ""), code_to_email
                ),
                "Review": normalize_assignee_cell(r.get("Review", ""), code_to_email),
                "Approval": normalize_assignee_cell(
                    r.get("Approval", ""), code_to_email
                ),
            }

    # -----------------------------
    # Tasks
    # -----------------------------
    task_fields = [
        "External ID (optional)",
        "Task Name* (project.task/name)",
        "Project Name* (project_id/name)",
        "Stage Name (stage_id/name)",
        "Assignee Emails (comma-separated) (user_ids/login)",
        "Start Date (planned_date_begin or date_start)",
        "Due Date (date_deadline)",
        "End Date (planned_date_end) (optional)",
        "Planned Hours (planned_hours)",
        "Priority (0-3)",
        "Tags (comma-separated) (tag_ids/name)",
        "Description (plain text)",
        "Parent Task External ID (optional parent_id/id)",
    ]

    tasks: List[Dict[str, str]] = []
    parents_seen = set()

    # Process Closing Gantt
    # Expected columns: Task Category, Detailed Task, Activity, Employee, Date, Email
    cg = closing_gantt.dropna(subset=["Detailed Task", "Activity", "Date"])
    print(f"Processing {len(cg)} rows from Closing Task - Gannt Chart")

    for _, r in cg.iterrows():
        cat = str(r.get("Task Category", "") or "").strip()
        detailed = str(r["Detailed Task"]).strip()
        stage = str(r["Activity"]).strip()  # Preparation/Review/Approval
        date_iso = fmt_date(r["Date"])
        email_row = str(r.get("Email", "") or "").strip()

        parent_ext = f"close_{slug(detailed)}"
        if parent_ext not in parents_seen:
            tasks.append(
                {
                    "External ID (optional)": parent_ext,
                    "Task Name* (project.task/name)": detailed,
                    "Project Name* (project_id/name)": P_CLOSE,
                    "Stage Name (stage_id/name)": "Preparation",
                    "Assignee Emails (comma-separated) (user_ids/login)": "",
                    "Start Date (planned_date_begin or date_start)": "",
                    "Due Date (date_deadline)": "",
                    "End Date (planned_date_end) (optional)": "",
                    "Planned Hours (planned_hours)": "",
                    "Priority (0-3)": "",
                    "Tags (comma-separated) (tag_ids/name)": cat,
                    "Description (plain text)": "",
                    "Parent Task External ID (optional parent_id/id)": "",
                }
            )
            parents_seen.add(parent_ext)

        # Prefer matrix default for that detailed task + stage, else fallback to gantt email
        default_email = ""
        if detailed in matrix_defaults:
            default_email = matrix_defaults[detailed].get(stage, "") or ""
        assignee = default_email if default_email else email_row

        child_ext = (
            f"{parent_ext}_{slug(stage)}_{date_iso.replace('-', '')}"
            if date_iso
            else f"{parent_ext}_{slug(stage)}"
        )
        tasks.append(
            {
                "External ID (optional)": child_ext,
                "Task Name* (project.task/name)": f"{detailed} — {stage}",
                "Project Name* (project_id/name)": P_CLOSE,
                "Stage Name (stage_id/name)": stage,
                "Assignee Emails (comma-separated) (user_ids/login)": assignee,
                "Start Date (planned_date_begin or date_start)": date_iso,
                "Due Date (date_deadline)": date_iso,
                "End Date (planned_date_end) (optional)": date_iso,
                "Planned Hours (planned_hours)": "",
                "Priority (0-3)": "",
                "Tags (comma-separated) (tag_ids/name)": cat,
                "Description (plain text)": "",
                "Parent Task External ID (optional parent_id/id)": parent_ext,
            }
        )

    # Process Tax Filing
    # Try multiple possible header patterns
    deadline_col = None
    for col in tax.columns:
        if "BIR Filing" in col and "Deadline" in col:
            deadline_col = col
            break

    # Step columns - try to find matching patterns
    step_cols = []
    for col in tax.columns:
        if "Prep" in col or "Preparation" in col:
            step_cols.append(("Preparation", col, "Finance Supervisor"))
        elif "Review" in col or "Report Approval" in col:
            step_cols.append(("Review", col, "Senior Finance Manager"))
        elif "Payment Approval" in col:
            step_cols.append(("Approval", col, "Finance Director"))

    tx = tax.dropna(subset=["BIR Form"])
    print(f"Processing {len(tx)} rows from Tax Filing")

    for _, r in tx.iterrows():
        form = str(r["BIR Form"]).strip()
        period = str(r.get("Period Covered", "") or "").strip()
        parent_name = f"{form}" + (f" — {period}" if period else "")
        parent_ext = f"tax_{slug(form)}_{slug(period) if period else 'period'}"

        dl = fmt_date(r.get(deadline_col)) if deadline_col else ""
        tasks.append(
            {
                "External ID (optional)": parent_ext,
                "Task Name* (project.task/name)": parent_name,
                "Project Name* (project_id/name)": P_TAX,
                "Stage Name (stage_id/name)": "Preparation",
                "Assignee Emails (comma-separated) (user_ids/login)": "",
                "Start Date (planned_date_begin or date_start)": "",
                "Due Date (date_deadline)": dl,
                "End Date (planned_date_end) (optional)": "",
                "Planned Hours (planned_hours)": "",
                "Priority (0-3)": "",
                "Tags (comma-separated) (tag_ids/name)": "Tax Filing",
                "Description (plain text)": (f"Deadline: {dl}" if dl else ""),
                "Parent Task External ID (optional parent_id/id)": "",
            }
        )

        for stage, col, role in step_cols:
            if col not in tax.columns or not is_nonempty(r.get(col)):
                continue
            iso = fmt_date(r.get(col))
            child_ext = (
                f"{parent_ext}_{slug(stage)}_{iso.replace('-', '')}"
                if iso
                else f"{parent_ext}_{slug(stage)}"
            )
            tasks.append(
                {
                    "External ID (optional)": child_ext,
                    "Task Name* (project.task/name)": f"{parent_name} — {stage}",
                    "Project Name* (project_id/name)": P_TAX,
                    "Stage Name (stage_id/name)": stage,
                    "Assignee Emails (comma-separated) (user_ids/login)": f"<<MAP:{role}>>",
                    "Start Date (planned_date_begin or date_start)": iso,
                    "Due Date (date_deadline)": iso,
                    "End Date (planned_date_end) (optional)": iso,
                    "Planned Hours (planned_hours)": "",
                    "Priority (0-3)": "",
                    "Tags (comma-separated) (tag_ids/name)": "Tax Filing",
                    "Description (plain text)": "",
                    "Parent Task External ID (optional parent_id/id)": parent_ext,
                }
            )

    # -----------------------------
    # Calendar Events from holidays
    # -----------------------------
    cal_fields = [
        "External ID (optional)",
        "Event Title* (calendar.event/name)",
        "All Day (Y/N)",
        "Start (YYYY-MM-DD)",
        "End (YYYY-MM-DD)",
        "Description",
        "Tags (optional)",
    ]
    cal_rows: List[Dict[str, str]] = []
    if "Date" in hol.columns and "Holiday Name" in hol.columns:
        for _, r in hol.dropna(subset=["Date", "Holiday Name"]).iterrows():
            d = fmt_date(r["Date"])
            if not d:
                continue
            name = str(r["Holiday Name"]).strip()
            if not name:
                continue
            tag = "Holiday"
            if "Type" in hol.columns and is_nonempty(r.get("Type")):
                tag = str(r.get("Type")).strip()
            cal_rows.append(
                {
                    "External ID (optional)": f"holiday_{d.replace('-', '')}_{slug(name)}",
                    "Event Title* (calendar.event/name)": name,
                    "All Day (Y/N)": "Y",
                    "Start (YYYY-MM-DD)": d,
                    "End (YYYY-MM-DD)": d,
                    "Description": "Imported from Holidays & Calendar",
                    "Tags (optional)": tag,
                }
            )
        print(f"Processing {len(cal_rows)} calendar events from Holidays & Calendar")

    # Split Pass A (parents) / Pass B (children)
    parents_rows = [
        t
        for t in tasks
        if not str(
            t.get("Parent Task External ID (optional parent_id/id)", "") or ""
        ).strip()
    ]
    children_rows = [
        t
        for t in tasks
        if str(
            t.get("Parent Task External ID (optional parent_id/id)", "") or ""
        ).strip()
    ]

    # Write outputs
    write_csv(
        os.path.join(outdir, "odoo_import_month_end_projects.csv"),
        projects_rows,
        projects_fields,
    )
    write_csv(
        os.path.join(outdir, "odoo_import_month_end_stages.csv"),
        stages_rows,
        stages_fields,
    )
    write_csv(
        os.path.join(outdir, "odoo_import_month_end_tasks_PassA_parents.csv"),
        parents_rows,
        task_fields,
    )
    write_csv(
        os.path.join(outdir, "odoo_import_month_end_tasks_PassB_children.csv"),
        children_rows,
        task_fields,
    )
    write_csv(
        os.path.join(outdir, "odoo_import_month_end_calendar_events.csv"),
        cal_rows,
        cal_fields,
    )

    print("\nGenerated:")
    for p in [
        "odoo_import_month_end_projects.csv",
        "odoo_import_month_end_stages.csv",
        "odoo_import_month_end_tasks_PassA_parents.csv",
        "odoo_import_month_end_tasks_PassB_children.csv",
        "odoo_import_month_end_calendar_events.csv",
    ]:
        full_path = os.path.join(outdir, p)
        if os.path.exists(full_path):
            print(f"- {full_path}")

    print(f"\nSummary:")
    print(f"- Projects: {len(projects_rows)}")
    print(f"- Stages: {len(stages_rows)}")
    print(f"- Parent tasks (Pass A): {len(parents_rows)}")
    print(f"- Child tasks (Pass B): {len(children_rows)}")
    print(f"- Calendar events: {len(cal_rows)}")


if __name__ == "__main__":
    main()
