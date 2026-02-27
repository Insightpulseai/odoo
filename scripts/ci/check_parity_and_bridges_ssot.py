#!/usr/bin/env python3
"""
check_parity_and_bridges_ssot.py — Validate EE parity matrix and bridge catalog.

Checks:
  1. YAML parses successfully
  2. Required schema field present
  3. schema_rules.required_fields exist in every entry
  4. gap_type/status values are in allowed set (if defined in schema_rules)

Exit codes:
  0 — all checks pass
  1 — validation errors found
  2 — SSOT file missing or YAML parse error
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

PARITY_PATH = "ssot/parity/ee_to_oca_matrix.yaml"
BRIDGES_PATH = "ssot/bridges/catalog.yaml"


def load_yaml(path: Path) -> dict:
    if not path.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(2)
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"ERROR: YAML parse error in {path}: {e}", file=sys.stderr)
        sys.exit(2)


def validate_entries(data: dict, file_path: str, entry_key: str = "entries") -> list[str]:
    errors = []
    schema_rules = data.get("schema_rules", {})
    required_fields = schema_rules.get("required_fields", [])
    allowed_values: dict[str, list] = {}

    # Build allowed-values map from schema_rules
    for key, val in schema_rules.items():
        if key.endswith("_values") and isinstance(val, list):
            field = key.replace("_values", "")
            allowed_values[field] = val

    entries = data.get(entry_key, [])
    if not isinstance(entries, list):
        errors.append(f"{file_path}: '{entry_key}' must be a list")
        return errors

    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"{file_path}[{i}]: entry must be a mapping")
            continue

        # Check required fields
        for field in required_fields:
            if field not in entry:
                errors.append(
                    f"{file_path}[{i}] ({entry.get('name') or entry.get('ee_feature') or f'entry {i}'}): "
                    f"missing required field '{field}'"
                )

        # Check allowed values
        for field, allowed in allowed_values.items():
            if field in entry and entry[field] not in allowed:
                errors.append(
                    f"{file_path}[{i}] ({entry.get('name') or entry.get('ee_feature') or f'entry {i}'}): "
                    f"field '{field}' = '{entry[field]}' not in allowed values {allowed}"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Parity and bridges SSOT validator")
    parser.add_argument("--repo-root", default=os.getcwd(), help="Path to repo root")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    all_errors = []

    # Validate parity matrix
    parity_file = repo_root / PARITY_PATH
    parity_data = load_yaml(parity_file)

    schema = parity_data.get("schema", "")
    if not schema.startswith("ssot.parity"):
        all_errors.append(f"{PARITY_PATH}: missing or invalid 'schema' field (got '{schema}')")

    all_errors.extend(validate_entries(parity_data, PARITY_PATH, entry_key="entries"))

    # Validate bridge catalog
    bridges_file = repo_root / BRIDGES_PATH
    bridges_data = load_yaml(bridges_file)

    schema = bridges_data.get("schema", "")
    if not schema.startswith("ssot.bridges"):
        all_errors.append(f"{BRIDGES_PATH}: missing or invalid 'schema' field (got '{schema}')")

    all_errors.extend(validate_entries(bridges_data, BRIDGES_PATH, entry_key="bridges"))

    if not args.quiet:
        if all_errors:
            print(f"Parity/bridges SSOT validation failed ({len(all_errors)} errors):")
            for err in all_errors:
                print(f"  {err}")
        else:
            print("Parity/bridges SSOT validation passed — all entries valid")

    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
