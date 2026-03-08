#!/usr/bin/env python3
"""Validate enterprise OKR YAML against KPI contracts.

Checks:
  1. ssot/governance/enterprise_okrs.yaml has required structure
  2. Every kpi_ref matches an ID in platform/data/contracts/control_room_kpis.yaml
  3. parent_objectives references are valid objective IDs

Exit codes:
  0 = PASS
  1 = FAIL (validation errors)
  2 = ERROR (file not found, parse error)
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FAIL: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(2)


def load_yaml(path: Path) -> dict:
    """Load and parse a YAML file."""
    if not path.exists():
        print(f"ERROR: File not found: {path}")
        sys.exit(2)
    with open(path) as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"ERROR: YAML parse error in {path}: {e}")
            sys.exit(2)


def validate():
    """Run all validation checks."""
    repo_root = Path(__file__).resolve().parent.parent.parent

    okr_path = repo_root / "ssot" / "governance" / "enterprise_okrs.yaml"
    kpi_path = repo_root / "platform" / "data" / "contracts" / "control_room_kpis.yaml"

    okr_data = load_yaml(okr_path)
    kpi_data = load_yaml(kpi_path)

    errors = []

    # -- Check 1: Required top-level keys --
    required_keys = ["schema_version", "strategic_objectives", "canonical_okrs", "kpi_index"]
    for key in required_keys:
        if key not in okr_data:
            errors.append(f"Missing required top-level key: {key}")

    if errors:
        # Can't continue without required structure
        for e in errors:
            print(f"FAIL: {e}")
        return False

    # -- Build valid KPI ID set --
    valid_kpi_ids = set()
    for kpi in kpi_data.get("kpis", []):
        kpi_id = kpi.get("id")
        if kpi_id:
            valid_kpi_ids.add(kpi_id)

    if not valid_kpi_ids:
        errors.append("No KPI IDs found in control_room_kpis.yaml")

    # -- Build valid objective ID set --
    valid_obj_ids = set()
    for obj in okr_data.get("strategic_objectives", []):
        obj_id = obj.get("id")
        if obj_id:
            valid_obj_ids.add(obj_id)
        else:
            errors.append("Strategic objective missing 'id' field")

        # Validate kpi_ref in key_results
        for kr in obj.get("key_results", []):
            kpi_ref = kr.get("kpi_ref")
            if kpi_ref and kpi_ref not in valid_kpi_ids:
                errors.append(
                    f"Objective {obj_id}: kpi_ref '{kpi_ref}' not found in "
                    f"control_room_kpis.yaml (valid: {sorted(valid_kpi_ids)})"
                )

    # -- Check 2: Validate strategic objectives have required fields --
    for obj in okr_data.get("strategic_objectives", []):
        for field in ["id", "name", "description", "key_results"]:
            if field not in obj:
                errors.append(f"Objective {obj.get('id', '?')}: missing field '{field}'")

    # -- Check 3: Validate canonical OKRs --
    for okr in okr_data.get("canonical_okrs", []):
        okr_id = okr.get("id", "?")

        for field in ["id", "name", "description", "key_results"]:
            if field not in okr:
                errors.append(f"OKR {okr_id}: missing field '{field}'")

        # Validate parent_objectives
        for parent in okr.get("parent_objectives", []):
            if parent not in valid_obj_ids:
                errors.append(
                    f"OKR {okr_id}: parent_objective '{parent}' not found "
                    f"(valid: {sorted(valid_obj_ids)})"
                )

        # Validate kpi_ref in key_results
        for kr in okr.get("key_results", []):
            kpi_ref = kr.get("kpi_ref")
            if kpi_ref and kpi_ref not in valid_kpi_ids:
                errors.append(
                    f"OKR {okr_id}: kpi_ref '{kpi_ref}' not found in "
                    f"control_room_kpis.yaml"
                )

    # -- Check 4: Validate kpi_index --
    kpi_index = okr_data.get("kpi_index", {})
    for obj_id, kpis in kpi_index.items():
        if obj_id not in valid_obj_ids:
            errors.append(f"kpi_index: objective '{obj_id}' not in strategic_objectives")
        for kpi_ref in kpis:
            if kpi_ref not in valid_kpi_ids:
                errors.append(f"kpi_index[{obj_id}]: kpi_ref '{kpi_ref}' not valid")

    # -- Report --
    if errors:
        print(f"FAIL: {len(errors)} validation error(s):")
        for e in errors:
            print(f"  - {e}")
        return False

    print("PASS: Enterprise OKR YAML validation successful")
    print(f"  - {len(okr_data['strategic_objectives'])} strategic objectives")
    print(f"  - {len(okr_data['canonical_okrs'])} canonical OKRs")
    print(f"  - {len(valid_kpi_ids)} KPI IDs cross-referenced")
    return True


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
