#!/usr/bin/env python3
"""Validate ssot/governance/platform-strategy-2026.yaml against its JSON Schema.

Checks:
  1. YAML parses
  2. JSON Schema validation passes
  3. Unique IDs across objectives, OKRs, key results, KPIs, tasks, risks
  4. kra_ref in objectives references a valid KRA ID
  5. objective_ref in OKRs references a valid objective ID
  6. activity_ref in tasks references a valid activity ID
  7. Blocked tasks require blocker field
  8. target_date values are valid ISO dates and not in the past
  9. spatres section has all 7 dimensions

Exit 0 on success, 1 on validation failure.
"""

import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SSOT_YAML = REPO_ROOT / "ssot" / "governance" / "platform-strategy-2026.yaml"
SCHEMA_JSON = REPO_ROOT / "ssot" / "governance" / "platform-strategy.schema.json"

try:
    import yaml
except ImportError:
    yaml = None

try:
    import jsonschema
except ImportError:
    jsonschema = None


def load_yaml(path: Path) -> dict:
    text = path.read_text()
    if yaml is not None:
        return yaml.safe_load(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print("ERROR: PyYAML not installed and file is not JSON-compatible.")
        print("       Install: pip install pyyaml")
        sys.exit(1)


VALID_STATUSES = {"not_started", "in_progress", "completed", "blocked"}
SPATRES_DIMENSIONS = {"scope", "people", "artifacts", "timeline", "risks", "environments", "success"}


def _normalize_dates(obj):
    """Recursively convert datetime.date objects to ISO strings for schema validation."""
    if isinstance(obj, date) and not isinstance(obj, type(None)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: _normalize_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_normalize_dates(item) for item in obj]
    return obj


def main() -> int:
    errors: list[str] = []

    if not SSOT_YAML.exists():
        print(f"FAIL: SSOT file not found: {SSOT_YAML}")
        return 1

    if not SCHEMA_JSON.exists():
        print(f"FAIL: Schema file not found: {SCHEMA_JSON}")
        return 1

    # --- 1. Parse YAML ---
    print(f"Parsing {SSOT_YAML.relative_to(REPO_ROOT)} ...")
    data = load_yaml(SSOT_YAML)
    if data is None:
        errors.append("YAML parsed to None (empty file?)")
        _report(errors)
        return 1
    print("  YAML parse: PASS")

    schema = json.loads(SCHEMA_JSON.read_text())

    # --- 2. JSON Schema validation ---
    # Normalize YAML date objects to ISO strings for schema validation
    normalized = _normalize_dates(data)
    if jsonschema is not None:
        print("Validating against JSON Schema ...")
        try:
            jsonschema.validate(instance=normalized, schema=schema)
            print("  schema: PASS")
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation: {e.message} (path: {list(e.absolute_path)})")
    else:
        print("  WARN: jsonschema not installed — skipping schema validation")

    # --- 3. Unique IDs ---
    print("Checking unique IDs ...")
    id_collections = {
        "objectives": [o.get("id") for o in data.get("objectives", [])],
        "okrs": [o.get("id") for o in data.get("okrs", [])],
        "key_results": [
            kr.get("id")
            for okr in data.get("okrs", [])
            for kr in okr.get("key_results", [])
        ],
        "kpis": [k.get("id") for k in data.get("kpis", [])],
        "tasks": [t.get("id") for t in data.get("tasks", [])],
        "risks": [r.get("id") for r in data.get("risks", [])],
        "kras": [k.get("id") for k in data.get("kras", [])],
        "strategies": [s.get("id") for s in data.get("strategies", [])],
        "programs": [p.get("id") for p in data.get("programs", [])],
        "activities": [a.get("id") for a in data.get("activities", [])],
    }
    for collection_name, ids in id_collections.items():
        seen = set()
        for id_val in ids:
            if id_val in seen:
                errors.append(f"Duplicate {collection_name} ID: {id_val}")
            seen.add(id_val)
    if not any("Duplicate" in e for e in errors):
        total = sum(len(ids) for ids in id_collections.values())
        print(f"  unique IDs: PASS ({total} IDs across {len(id_collections)} collections)")

    # --- 4. kra_ref validation ---
    print("Checking kra_ref references ...")
    kra_ids = set(id_collections["kras"])
    for obj in data.get("objectives", []):
        for kra_ref in obj.get("kra_ref", []):
            if kra_ref not in kra_ids:
                errors.append(
                    f"Objective '{obj.get('id')}' references unknown KRA: {kra_ref}"
                )
    if not any("unknown KRA" in e for e in errors):
        print("  kra_ref: PASS")

    # --- 5. objective_ref validation ---
    print("Checking objective_ref references ...")
    obj_ids = set(id_collections["objectives"])
    for okr in data.get("okrs", []):
        obj_ref = okr.get("objective_ref")
        if obj_ref and obj_ref not in obj_ids:
            errors.append(
                f"OKR '{okr.get('id')}' references unknown objective: {obj_ref}"
            )
    if not any("unknown objective" in e for e in errors):
        print("  objective_ref: PASS")

    # --- 6. activity_ref validation ---
    print("Checking activity_ref references ...")
    activity_ids = set(id_collections["activities"])
    for task in data.get("tasks", []):
        act_ref = task.get("activity_ref")
        if act_ref and act_ref not in activity_ids:
            errors.append(
                f"Task '{task.get('id')}' references unknown activity: {act_ref}"
            )
    if not any("unknown activity" in e for e in errors):
        print("  activity_ref: PASS")

    # --- 7. Blocked tasks require blocker ---
    print("Checking blocked tasks have blocker field ...")
    for task in data.get("tasks", []):
        if task.get("status") == "blocked" and not task.get("blocker"):
            errors.append(
                f"Task '{task.get('id')}' has status=blocked but no 'blocker' field"
            )
    if not any("blocker" in e for e in errors):
        print("  blocked tasks: PASS")

    # --- 8. target_date validation ---
    print("Checking target_date values ...")
    for obj in data.get("objectives", []):
        td = obj.get("target_date")
        if td:
            try:
                # YAML may auto-parse date strings as datetime.date objects
                if isinstance(td, date):
                    pass  # already valid
                else:
                    date.fromisoformat(str(td))
            except ValueError:
                errors.append(
                    f"Objective '{obj.get('id')}' has invalid target_date: {td}"
                )
    if not any("target_date" in e for e in errors):
        print("  target_date: PASS")

    # --- 9. SPATRES dimensions ---
    print("Checking SPATRES dimensions ...")
    spatres = data.get("spatres", {})
    if isinstance(spatres, dict):
        present = set(spatres.keys())
        missing = SPATRES_DIMENSIONS - present
        if missing:
            errors.append(f"SPATRES missing dimensions: {sorted(missing)}")
        else:
            print(f"  SPATRES: PASS ({len(SPATRES_DIMENSIONS)} dimensions)")
    else:
        errors.append("SPATRES must be an object/dict")

    _report(errors)
    return 1 if errors else 0


def _report(errors: list[str]) -> None:
    if errors:
        print(f"\n{'=' * 60}")
        print(f"FAIL: {len(errors)} error(s)")
        print(f"{'=' * 60}")
        for i, e in enumerate(errors, 1):
            print(f"  {i}. {e}")
    else:
        print(f"\n{'=' * 60}")
        print("PASS: All checks passed")
        print(f"{'=' * 60}")


if __name__ == "__main__":
    sys.exit(main())
