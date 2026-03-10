#!/usr/bin/env python3
"""
Validate Feature and Integration registry entries against JSON schemas.

Usage:
    python scripts/validate_registries.py
    python scripts/validate_registries.py --verbose
    python scripts/validate_registries.py --features-only
    python scripts/validate_registries.py --integrations-only
"""

import argparse
import glob
import json
import os
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, ValidationError
except ImportError:
    print("ERROR: jsonschema package required. Install with: pip install jsonschema")
    sys.exit(1)


def load_json(path: str) -> dict:
    """Load a JSON file and return its contents."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_entries(
    pattern: str,
    schema: dict,
    entry_type: str,
    verbose: bool = False
) -> tuple[int, int]:
    """
    Validate all JSON files matching pattern against schema.

    Returns:
        Tuple of (pass_count, fail_count)
    """
    validator = Draft202012Validator(schema)
    files = glob.glob(pattern)

    if not files:
        print(f"WARNING: No {entry_type} files found matching {pattern}")
        return 0, 0

    pass_count = 0
    fail_count = 0

    for filepath in sorted(files):
        filename = os.path.basename(filepath)
        try:
            data = load_json(filepath)
            errors = list(validator.iter_errors(data))

            if errors:
                fail_count += 1
                print(f"[FAIL] {entry_type}/{filename}")
                for error in errors:
                    path = " -> ".join(str(p) for p in error.path) or "(root)"
                    print(f"       {path}: {error.message}")
            else:
                pass_count += 1
                if verbose:
                    print(f"[PASS] {entry_type}/{filename}")

        except json.JSONDecodeError as e:
            fail_count += 1
            print(f"[FAIL] {entry_type}/{filename}: Invalid JSON - {e}")
        except Exception as e:
            fail_count += 1
            print(f"[FAIL] {entry_type}/{filename}: {e}")

    return pass_count, fail_count


def check_unique_ids(pattern: str, entry_type: str) -> int:
    """
    Check that all entries have unique IDs.

    Returns:
        Number of duplicate ID errors
    """
    files = glob.glob(pattern)
    ids_seen = {}
    duplicates = 0

    for filepath in files:
        try:
            data = load_json(filepath)
            entry_id = data.get("id")
            if entry_id:
                if entry_id in ids_seen:
                    print(f"[FAIL] Duplicate ID '{entry_id}' in {filepath}")
                    print(f"       First seen in: {ids_seen[entry_id]}")
                    duplicates += 1
                else:
                    ids_seen[entry_id] = filepath
        except Exception:
            pass  # Already reported in validate_entries

    return duplicates


def check_related_assets(features_pattern: str, integrations_pattern: str) -> int:
    """
    Check that related_assets references exist.

    Returns:
        Number of broken reference errors
    """
    # Collect all valid IDs
    valid_ids = set()

    for pattern in [features_pattern, integrations_pattern]:
        for filepath in glob.glob(pattern):
            try:
                data = load_json(filepath)
                if "id" in data:
                    valid_ids.add(data["id"])
            except Exception:
                pass

    # Check related_assets references
    broken_refs = 0
    for filepath in glob.glob(features_pattern):
        try:
            data = load_json(filepath)
            related = data.get("related_assets", [])
            for ref in related:
                if ref not in valid_ids:
                    print(f"[WARN] Broken reference '{ref}' in {filepath}")
                    # Warning only, not a failure
        except Exception:
            pass

    return broken_refs


def main():
    parser = argparse.ArgumentParser(
        description="Validate registry entries against JSON schemas"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show passing entries"
    )
    parser.add_argument(
        "--features-only",
        action="store_true",
        help="Only validate features"
    )
    parser.add_argument(
        "--integrations-only",
        action="store_true",
        help="Only validate integrations"
    )
    args = parser.parse_args()

    # Determine repo root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    # Load schemas
    feature_schema_path = repo_root / "schemas" / "feature.schema.json"
    integration_schema_path = repo_root / "schemas" / "integration.schema.json"

    if not feature_schema_path.exists():
        print(f"ERROR: Feature schema not found at {feature_schema_path}")
        sys.exit(1)
    if not integration_schema_path.exists():
        print(f"ERROR: Integration schema not found at {integration_schema_path}")
        sys.exit(1)

    feature_schema = load_json(str(feature_schema_path))
    integration_schema = load_json(str(integration_schema_path))

    # Patterns
    features_pattern = str(repo_root / "registry" / "features" / "*.json")
    integrations_pattern = str(repo_root / "registry" / "integrations" / "*.json")

    total_pass = 0
    total_fail = 0

    print("=" * 60)
    print("Registry Validation")
    print("=" * 60)

    # Validate features
    if not args.integrations_only:
        print("\n--- Features ---")
        pass_count, fail_count = validate_entries(
            features_pattern, feature_schema, "features", args.verbose
        )
        total_pass += pass_count
        total_fail += fail_count

        # Check unique IDs
        total_fail += check_unique_ids(features_pattern, "features")

    # Validate integrations
    if not args.features_only:
        print("\n--- Integrations ---")
        pass_count, fail_count = validate_entries(
            integrations_pattern, integration_schema, "integrations", args.verbose
        )
        total_pass += pass_count
        total_fail += fail_count

        # Check unique IDs
        total_fail += check_unique_ids(integrations_pattern, "integrations")

    # Check related asset references (warning only)
    if not args.features_only and not args.integrations_only:
        print("\n--- Cross-references ---")
        check_related_assets(features_pattern, integrations_pattern)

    # Summary
    print("\n" + "=" * 60)
    print(f"SUMMARY: {total_pass} passed, {total_fail} failed")
    print("=" * 60)

    if total_fail > 0:
        print("\nValidation FAILED")
        sys.exit(1)
    else:
        print("\nValidation PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
