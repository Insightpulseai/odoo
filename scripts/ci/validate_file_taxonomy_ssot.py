#!/usr/bin/env python3
"""Validate file_taxonomy.yaml SSOT structure."""
import sys
import yaml
from pathlib import Path

TAXONOMY_PATH = Path(__file__).resolve().parents[2] / "ssot" / "governance" / "file_taxonomy.yaml"

REQUIRED_KEYS = ["version", "canonical_names", "fixed_files", "placement_rules", "historical_name_policy"]
REQUIRED_SPEC_FILES = {"constitution.md", "prd.md", "plan.md", "tasks.md"}


def main():
    errors = []

    if not TAXONOMY_PATH.exists():
        print(f"FAIL: {TAXONOMY_PATH} does not exist")
        return 1

    try:
        data = yaml.safe_load(TAXONOMY_PATH.read_text())
    except yaml.YAMLError as e:
        print(f"FAIL: YAML parse error: {e}")
        return 1

    if not isinstance(data, dict):
        print("FAIL: Root must be a mapping")
        return 1

    for key in REQUIRED_KEYS:
        if key not in data:
            errors.append(f"Missing required key: {key}")

    # Check spec bundle required names
    spec_names = set()
    try:
        spec_names = set(data["fixed_files"]["spec_bundle"]["required_names"])
    except (KeyError, TypeError):
        errors.append("Missing fixed_files.spec_bundle.required_names")

    if spec_names and spec_names != REQUIRED_SPEC_FILES:
        errors.append(f"Spec bundle required_names mismatch: got {spec_names}, expected {REQUIRED_SPEC_FILES}")

    # Check for duplicate aliases
    all_aliases = []
    for section in ("repos", "paths"):
        items = (data.get("canonical_names") or {}).get(section) or {}
        for name, cfg in items.items():
            for alias in (cfg or {}).get("forbidden_aliases", []):
                if alias in all_aliases:
                    errors.append(f"Duplicate forbidden alias: {alias}")
                all_aliases.append(alias)

    if errors:
        print("FAIL: file_taxonomy.yaml validation errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PASS: file_taxonomy.yaml valid (version={data.get('version')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
