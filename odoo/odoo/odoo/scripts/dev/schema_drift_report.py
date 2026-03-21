#!/usr/bin/env python3
"""Schema drift report: compare source-declared models against runtime tables.

Loads the source model index (ODOO_MODEL_INDEX.json) and runtime schema
(odoo_schema.json), converts Odoo model names to PostgreSQL table names
(dots to underscores), and reports which source models exist in the runtime
database and which are missing.

Exit code is always 0 -- this is informational, not a CI gate.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def model_name_to_table(model_name: str) -> str:
    """Convert Odoo model name to PostgreSQL table name.

    Odoo convention: dots become underscores.
    Example: 'account.move' -> 'account_move'
    """
    return model_name.replace(".", "_")


def load_json(path: Path) -> dict:
    """Load and parse a JSON file, exiting with a clear message on failure."""
    if not path.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(0)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    # Resolve paths relative to the repo root (three levels up from this script)
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent  # scripts/dev -> scripts -> repo root

    source_path = repo_root / "docs" / "data-model" / "ODOO_MODEL_INDEX.json"
    runtime_path = repo_root / "docs" / "data-model" / "runtime" / "odoo_schema.json"
    output_path = repo_root / "docs" / "data-model" / "runtime" / "drift_report.json"

    # Load both files
    source_data = load_json(source_path)
    runtime_data = load_json(runtime_path)

    # Extract source models: list of dicts with 'name' and 'table' keys
    source_models = source_data.get("models", [])

    # Extract runtime table names (keys of the 'tables' dict), lowercased for comparison
    runtime_tables_raw = set(runtime_data.get("tables", {}).keys())
    runtime_tables_lower = {t.lower() for t in runtime_tables_raw}

    # Build comparison sets
    # Each source model has a declared table name; use it if present, else derive
    matched = []
    missing = []

    for model in source_models:
        model_name = model.get("name", "")
        declared_table = model.get("table") or model_name_to_table(model_name)
        module = model.get("module", "unknown")

        entry = {
            "model": model_name,
            "expected_table": declared_table,
            "module": module,
        }

        # Check case-insensitive match against runtime tables
        if declared_table.lower() in runtime_tables_lower:
            matched.append(entry)
        else:
            missing.append(entry)

    # Sort for stable output
    matched.sort(key=lambda x: x["model"])
    missing.sort(key=lambda x: x["model"])

    # Build report
    now = datetime.now(timezone.utc).isoformat()
    report = {
        "generated_at": now,
        "source_file": str(source_path.relative_to(repo_root)),
        "runtime_file": str(runtime_path.relative_to(repo_root)),
        "summary": {
            "source_models_total": len(source_models),
            "runtime_tables_total": len(runtime_tables_raw),
            "matched": len(matched),
            "missing_from_runtime": len(missing),
            "parity_pct": round(
                len(matched) / len(source_models) * 100, 1
            ) if source_models else 0.0,
        },
        "matched_models": matched,
        "missing_from_runtime": missing,
    }

    # Print summary to stdout
    s = report["summary"]
    print("=" * 60)
    print("  Schema Drift Report")
    print("=" * 60)
    print(f"  Generated:            {now}")
    print(f"  Source models:        {s['source_models_total']}")
    print(f"  Runtime tables:       {s['runtime_tables_total']}")
    print(f"  Matched (parity):     {s['matched']} ({s['parity_pct']}%)")
    print(f"  Missing from runtime: {s['missing_from_runtime']}")
    print("=" * 60)

    if matched:
        print(f"\nMATCHED ({len(matched)} models confirmed in runtime):")
        for m in matched:
            print(f"  [OK] {m['model']:40s} -> {m['expected_table']}")

    if missing:
        print(f"\nMISSING ({len(missing)} models not found in runtime):")
        for m in missing:
            print(f"  [--] {m['model']:40s} -> {m['expected_table']}  (module: {m['module']})")

    print()

    # Save detailed JSON report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Detailed report saved to: {output_path.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
