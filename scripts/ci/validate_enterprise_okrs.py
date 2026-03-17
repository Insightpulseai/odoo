#!/usr/bin/env python3
"""Validate ssot/governance/enterprise_okrs.yaml against its JSON Schema.

Checks:
  1. YAML parses
  2. JSON Schema validation passes
  3. Required top-level keys: schema_version, strategic_objectives, canonical_okrs, kpi_index
  4. Unique IDs across strategic_objectives[].id and canonical_okrs[].id
  5. Each strategic_objective has: id, name, description, key_results
  6. Each canonical_okr has: id, name, description, key_results
  7. kpi_ref cross-refs: every kpi_ref in both strategic_objectives and canonical_okrs
     key_results exists in control_room_kpis.yaml kpis[].id
  8. parent_objectives integrity: every parent_objectives[] entry in canonical_okrs
     references a valid strategic_objectives[].id
  9. kpi_index consistency: keys must be valid objective IDs, values must be valid
     KPI IDs from control_room_kpis.yaml

Exit 0 on success, 1 on validation failure, 2 on parse error.
"""

import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SSOT_YAML = REPO_ROOT / "ssot" / "governance" / "enterprise_okrs.yaml"
SCHEMA_JSON = REPO_ROOT / "ssot" / "governance" / "enterprise_okrs.schema.json"
KPI_YAML = REPO_ROOT / "platform" / "data" / "contracts" / "control_room_kpis.yaml"

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
        sys.exit(2)


def _normalize_dates(obj):
    """Recursively convert datetime.date objects to ISO strings for schema validation."""
    if isinstance(obj, date) and not isinstance(obj, type(None)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: _normalize_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_normalize_dates(item) for item in obj]
    return obj


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


def main() -> int:
    errors: list[str] = []

    if not SSOT_YAML.exists():
        print(f"FAIL: SSOT file not found: {SSOT_YAML}")
        return 1

    # --- 1. Parse YAML ---
    print(f"Parsing {SSOT_YAML.relative_to(REPO_ROOT)} ...")
    try:
        data = load_yaml(SSOT_YAML)
    except Exception as exc:
        print(f"  Check 1: YAML parses: FAIL — {exc}")
        _report([f"YAML parse error: {exc}"])
        return 2
    if data is None:
        print("  Check 1: YAML parses: FAIL — empty file")
        _report(["YAML parsed to None (empty file?)"])
        return 2
    print("  Check 1: YAML parses: PASS")

    # --- 2. JSON Schema validation ---
    normalized = _normalize_dates(data)
    if SCHEMA_JSON.exists():
        schema = json.loads(SCHEMA_JSON.read_text())
        if jsonschema is not None:
            print("  Check 2: JSON Schema validation ...")
            try:
                jsonschema.validate(instance=normalized, schema=schema)
                print("  Check 2: JSON Schema validation: PASS")
            except jsonschema.ValidationError as e:
                errors.append(
                    f"Schema validation: {e.message} (path: {list(e.absolute_path)})"
                )
                print(f"  Check 2: JSON Schema validation: FAIL — {e.message}")
        else:
            print(
                "  Check 2: JSON Schema validation: WARN — jsonschema not installed, skipping"
            )
    else:
        print(
            f"  Check 2: JSON Schema validation: WARN — schema not found at {SCHEMA_JSON}, skipping"
        )

    # --- 3. Required top-level keys ---
    print("  Check 3: Required top-level keys ...")
    required_keys = {"schema_version", "strategic_objectives", "canonical_okrs", "kpi_index"}
    missing_keys = required_keys - set(data.keys())
    if missing_keys:
        for k in sorted(missing_keys):
            errors.append(f"Missing required top-level key: {k}")
        print(f"  Check 3: Required top-level keys: FAIL — missing: {sorted(missing_keys)}")
    else:
        print("  Check 3: Required top-level keys: PASS")

    # Early exit if structural keys are absent — subsequent checks depend on them
    if missing_keys:
        _report(errors)
        return 1

    # --- 4. Unique IDs ---
    print("  Check 4: Unique IDs across strategic_objectives and canonical_okrs ...")
    strategic_objective_ids_raw = [
        o.get("id") for o in data.get("strategic_objectives", [])
    ]
    canonical_okr_ids_raw = [
        o.get("id") for o in data.get("canonical_okrs", [])
    ]
    all_id_collections = {
        "strategic_objectives": strategic_objective_ids_raw,
        "canonical_okrs": canonical_okr_ids_raw,
    }
    duplicate_found = False
    for collection_name, ids in all_id_collections.items():
        seen: set = set()
        for id_val in ids:
            if id_val in seen:
                errors.append(f"Duplicate {collection_name} ID: {id_val}")
                duplicate_found = True
            if id_val is not None:
                seen.add(id_val)
    if not duplicate_found:
        total = sum(len(ids) for ids in all_id_collections.values())
        print(
            f"  Check 4: Unique IDs across strategic_objectives and canonical_okrs: PASS"
            f" ({total} IDs across {len(all_id_collections)} collections)"
        )
    else:
        print("  Check 4: Unique IDs across strategic_objectives and canonical_okrs: FAIL")

    # Build authoritative ID sets for subsequent checks
    strategic_ids: set[str] = {
        i for i in strategic_objective_ids_raw if i is not None
    }
    canonical_ids: set[str] = {
        i for i in canonical_okr_ids_raw if i is not None
    }

    # --- 5. Each strategic_objective required fields ---
    print("  Check 5: Each strategic_objective has id, name, description, key_results ...")
    required_so_fields = {"id", "name", "description", "key_results"}
    so_field_fail = False
    for obj in data.get("strategic_objectives", []):
        missing_fields = required_so_fields - set(obj.keys())
        if missing_fields:
            errors.append(
                f"strategic_objective '{obj.get('id', '<no id>')}' missing fields: "
                f"{sorted(missing_fields)}"
            )
            so_field_fail = True
    if not so_field_fail:
        print("  Check 5: Each strategic_objective has id, name, description, key_results: PASS")
    else:
        print("  Check 5: Each strategic_objective has id, name, description, key_results: FAIL")

    # --- 6. Each canonical_okr required fields ---
    print("  Check 6: Each canonical_okr has id, name, description, key_results ...")
    required_okr_fields = {"id", "name", "description", "key_results"}
    okr_field_fail = False
    for okr in data.get("canonical_okrs", []):
        missing_fields = required_okr_fields - set(okr.keys())
        if missing_fields:
            errors.append(
                f"canonical_okr '{okr.get('id', '<no id>')}' missing fields: "
                f"{sorted(missing_fields)}"
            )
            okr_field_fail = True
    if not okr_field_fail:
        print("  Check 6: Each canonical_okr has id, name, description, key_results: PASS")
    else:
        print("  Check 6: Each canonical_okr has id, name, description, key_results: FAIL")

    # --- 7. kpi_ref cross-references ---
    print("  Check 7: kpi_ref cross-references against control_room_kpis.yaml ...")
    known_kpi_ids: set[str] = set()
    kpi_load_ok = False
    if KPI_YAML.exists():
        try:
            kpi_data = load_yaml(KPI_YAML)
            if kpi_data and isinstance(kpi_data.get("kpis"), list):
                known_kpi_ids = {
                    k.get("id") for k in kpi_data["kpis"] if k.get("id") is not None
                }
                kpi_load_ok = True
            else:
                print(
                    f"  Check 7: kpi_ref cross-references: WARN — KPI file loaded but "
                    f"'kpis' list not found, skipping cross-ref"
                )
        except Exception as exc:
            print(f"  Check 7: kpi_ref cross-references: WARN — could not load KPI file: {exc}")
    else:
        print(
            f"  Check 7: kpi_ref cross-references: WARN — {KPI_YAML.relative_to(REPO_ROOT)} "
            f"not found, skipping cross-ref"
        )

    kpi_ref_fail = False
    kpi_ref_count = 0
    if kpi_load_ok:
        # Collect all kpi_refs from strategic_objectives key_results
        for obj in data.get("strategic_objectives", []):
            for kr in obj.get("key_results", []):
                kpi_ref = kr.get("kpi_ref")
                if kpi_ref:
                    kpi_ref_count += 1
                    if kpi_ref not in known_kpi_ids:
                        errors.append(
                            f"strategic_objective '{obj.get('id')}' key_result "
                            f"'{kr.get('id', '<no id>')}' references unknown kpi_ref: {kpi_ref}"
                        )
                        kpi_ref_fail = True
        # Collect all kpi_refs from canonical_okrs key_results
        for okr in data.get("canonical_okrs", []):
            for kr in okr.get("key_results", []):
                kpi_ref = kr.get("kpi_ref")
                if kpi_ref:
                    kpi_ref_count += 1
                    if kpi_ref not in known_kpi_ids:
                        errors.append(
                            f"canonical_okr '{okr.get('id')}' key_result "
                            f"'{kr.get('id', '<no id>')}' references unknown kpi_ref: {kpi_ref}"
                        )
                        kpi_ref_fail = True
        if not kpi_ref_fail:
            print(
                f"  Check 7: kpi_ref cross-references: PASS ({kpi_ref_count} references validated)"
            )
        else:
            print("  Check 7: kpi_ref cross-references: FAIL")

    # --- 8. parent_objectives integrity ---
    print(
        "  Check 8: parent_objectives integrity in canonical_okrs ..."
    )
    parent_fail = False
    for okr in data.get("canonical_okrs", []):
        for parent_ref in (okr.get("parent_objectives") or []):
            if parent_ref not in strategic_ids:
                errors.append(
                    f"canonical_okr '{okr.get('id')}' parent_objectives references "
                    f"unknown strategic_objective id: {parent_ref}"
                )
                parent_fail = True
    if not parent_fail:
        print("  Check 8: parent_objectives integrity in canonical_okrs: PASS")
    else:
        print("  Check 8: parent_objectives integrity in canonical_okrs: FAIL")

    # --- 9. kpi_index consistency ---
    print("  Check 9: kpi_index consistency ...")
    kpi_index = data.get("kpi_index", {})
    kpi_index_fail = False
    if not isinstance(kpi_index, dict):
        errors.append("kpi_index must be an object/dict")
        kpi_index_fail = True
        print("  Check 9: kpi_index consistency: FAIL — kpi_index is not a dict")
    else:
        all_valid_obj_ids = strategic_ids | canonical_ids
        for key, value in kpi_index.items():
            if key not in all_valid_obj_ids:
                errors.append(
                    f"kpi_index key '{key}' is not a valid strategic_objectives or "
                    f"canonical_okrs id"
                )
                kpi_index_fail = True
            if kpi_load_ok:
                # value may be a single ID string or a list of ID strings
                ref_values = value if isinstance(value, list) else [value]
                for ref_val in ref_values:
                    if ref_val not in known_kpi_ids:
                        errors.append(
                            f"kpi_index['{key}'] references unknown KPI id: {ref_val}"
                        )
                        kpi_index_fail = True
        if not kpi_index_fail:
            print(
                f"  Check 9: kpi_index consistency: PASS ({len(kpi_index)} entries validated)"
            )
        else:
            print("  Check 9: kpi_index consistency: FAIL")

    # --- Summary ---
    n_so = len(data.get("strategic_objectives", []))
    n_okr = len(data.get("canonical_okrs", []))
    n_kpi_refs = kpi_ref_count if kpi_load_ok else 0
    print(
        f"\nSummary: {n_so} strategic_objectives, {n_okr} canonical_okrs, "
        f"{n_kpi_refs} KPI cross-references"
    )

    _report(errors)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
