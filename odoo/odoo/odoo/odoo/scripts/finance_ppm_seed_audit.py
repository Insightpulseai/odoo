#!/usr/bin/env python3
"""Finance PPM Seed Audit — deterministic CSV record counter.

Reads canonical seed CSVs from data/finance_seed/ and emits counts to
artifacts/finance_ppm_seed_audit.json.  Used by CI tier-0 gate
to enforce seed completeness without guesswork.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "finance_seed"

FILES = {
    "tags": "01_project.tags.csv",
    "projects": "02_project.project.csv",
    "month_end_tasks": "03_project.task.month_end.csv",
    "bir_tax_tasks": "04_project.task.bir_tax.csv",
    "expense_categories": "05_expense_categories.csv",
    "approval_rules": "06_approval_thresholds.csv",
}

THRESHOLDS = {
    "tags": 36,
    "projects": 2,
    "month_end_tasks": 36,
    "bir_tax_tasks": 33,
    "expense_categories": 18,
    "approval_rules": 11,
}


def count_csv_rows(path: Path) -> int:
    """Count data rows in a CSV file (excludes header)."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return sum(1 for _ in reader)


def main() -> None:
    errors: list[str] = []

    # Check all seed files exist
    missing = [k for k, v in FILES.items() if not (DATA / v).exists()]
    if missing:
        print(f"FAIL: missing seed files: {missing}", file=sys.stderr)
        sys.exit(1)

    counts: dict[str, object] = {}

    for key, filename in FILES.items():
        path = DATA / filename
        row_count = count_csv_rows(path)
        counts[f"{key}_count"] = row_count

        threshold = THRESHOLDS.get(key, 0)
        if row_count < threshold:
            errors.append(f"{key}={row_count}, expected >={threshold}")

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
