#!/usr/bin/env python3
"""Finance PPM Seed Audit — deterministic XML record counter.

Reads umbrella module seed XMLs and emits canonical counts to
artifacts/finance_ppm_seed_audit.json.  Used by CI tier-0 gate
to enforce seed completeness without guesswork.
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "addons" / "ipai_finance_ppm_umbrella" / "data"

FILES = {
    "employees": "01_employees.xml",
    "logframe": "02_logframe_complete.xml",
    "bir": "03_bir_schedule.xml",
    "tasks": "04_closing_tasks.xml",
    "raci": "05_raci_assignments.xml",
}


def count_records(path: Path, model: str | None = None) -> int:
    root = ET.parse(path).getroot()
    n = 0
    for rec in root.iter("record"):
        if model is None or rec.attrib.get("model") == model:
            n += 1
    return n


def unique_field_values(path: Path, model: str, field_name: str) -> list[str]:
    root = ET.parse(path).getroot()
    out: set[str] = set()
    for rec in root.iter("record"):
        if rec.attrib.get("model") != model:
            continue
        for f in rec.iter("field"):
            if f.attrib.get("name") == field_name and (f.text or "").strip():
                out.add((f.text or "").strip())
    return sorted(out)


def unique_record_ids(path: Path, model: str | None = None) -> list[str]:
    root = ET.parse(path).getroot()
    out: set[str] = set()
    for rec in root.iter("record"):
        if model is None or rec.attrib.get("model") == model:
            rid = rec.attrib.get("id", "")
            if rid:
                out.add(rid)
    return sorted(out)


def main() -> None:
    errors: list[str] = []

    # Check all seed files exist
    missing = [k for k, v in FILES.items() if not (DATA / v).exists()]
    if missing:
        print(f"FAIL: missing seed files: {missing}", file=sys.stderr)
        sys.exit(1)

    counts: dict[str, object] = {}

    # Employees
    emp_count = count_records(DATA / FILES["employees"], model="res.users")
    emp_names = unique_field_values(
        DATA / FILES["employees"], "res.users", "name"
    )
    counts["employees_count"] = emp_count
    counts["employees_names"] = emp_names

    # Logframe
    counts["logframe_count"] = count_records(DATA / FILES["logframe"])

    # BIR schedule
    bir_count = count_records(DATA / FILES["bir"])
    counts["bir_count"] = bir_count

    # Closing tasks
    task_count = count_records(DATA / FILES["tasks"], model="project.task")
    counts["tasks_count"] = task_count

    # RACI assignments
    raci_count = count_records(DATA / FILES["raci"])
    counts["raci_count"] = raci_count

    # Sanity checks
    if emp_count < 8:
        errors.append(f"employees={emp_count}, expected >=8")
    if bir_count < 20:
        errors.append(f"bir_records={bir_count}, expected >=20")
    if task_count < 30:
        errors.append(f"tasks={task_count}, expected >=30")
    if raci_count < 8:
        errors.append(f"raci={raci_count}, expected >=8")

    counts["errors"] = errors
    counts["pass"] = len(errors) == 0

    # Write artifact
    out = REPO / "artifacts" / "finance_ppm_seed_audit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(counts, indent=2))

    if errors:
        print(f"\nFAIL: {len(errors)} sanity checks failed", file=sys.stderr)
        sys.exit(1)
    else:
        print("\nPASS: all seed sanity checks passed")


if __name__ == "__main__":
    main()
