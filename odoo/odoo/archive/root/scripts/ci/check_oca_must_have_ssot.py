#!/usr/bin/env python3
"""
check_oca_must_have_ssot.py — Validate OCA must-have base modules SSOT registry.

Checks:
  1. YAML parses successfully
  2. Top-level schema field matches expected value
  3. Top-level version field matches expected value
  4. No unknown top-level keys
  5. source block present with expected keys (name, url)
  6. modules list is non-empty
  7. Each module entry has exactly {technical_name, repo, rationale} — no extra keys
  8. technical_name values are unique

Exit codes:
  0 — all checks pass (PASS)
  2 — SSOT file missing or YAML/import error
  3 — validation error
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

SSOT_REL_PATH = "ssot/oca/must_have_base.yaml"
SCHEMA_EXPECTED = "ssot.oca.must_have_base.v1"
VERSION_EXPECTED = "1.0"

TOP_LEVEL_ALLOWED = {"schema", "version", "source", "modules", "notes"}
SOURCE_ALLOWED = {"name", "url"}
MODULE_REQUIRED = {"technical_name", "repo", "rationale"}


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


def validate(data: dict, path_label: str) -> list[str]:
    errors = []

    # 1. No unknown top-level keys
    unknown = set(data.keys()) - TOP_LEVEL_ALLOWED
    if unknown:
        errors.append(f"{path_label}: unknown top-level keys: {sorted(unknown)}")

    # 2. schema field
    schema = data.get("schema", "")
    if schema != SCHEMA_EXPECTED:
        errors.append(
            f"{path_label}: 'schema' must be '{SCHEMA_EXPECTED}', got '{schema}'"
        )

    # 3. version field
    version = data.get("version", "")
    if version != VERSION_EXPECTED:
        errors.append(
            f"{path_label}: 'version' must be '{VERSION_EXPECTED}', got '{version}'"
        )

    # 4. source block
    source = data.get("source")
    if not isinstance(source, dict):
        errors.append(f"{path_label}: 'source' must be a mapping")
    else:
        unknown_src = set(source.keys()) - SOURCE_ALLOWED
        if unknown_src:
            errors.append(
                f"{path_label}.source: unknown keys: {sorted(unknown_src)}"
            )
        for field in SOURCE_ALLOWED:
            if not source.get(field):
                errors.append(
                    f"{path_label}.source: missing or empty field '{field}'"
                )

    # 5. modules list
    modules = data.get("modules")
    if not isinstance(modules, list) or len(modules) == 0:
        errors.append(f"{path_label}: 'modules' must be a non-empty list")
        return errors

    seen_names: set[str] = set()
    for i, mod in enumerate(modules):
        if not isinstance(mod, dict):
            errors.append(f"{path_label}.modules[{i}]: entry must be a mapping")
            continue

        # Unknown keys
        extra = set(mod.keys()) - MODULE_REQUIRED
        if extra:
            errors.append(
                f"{path_label}.modules[{i}] ({mod.get('technical_name', '?')}): "
                f"unknown keys: {sorted(extra)}"
            )

        # Required keys
        for field in MODULE_REQUIRED:
            if not mod.get(field):
                errors.append(
                    f"{path_label}.modules[{i}] ({mod.get('technical_name', '?')}): "
                    f"missing or empty required field '{field}'"
                )

        # Uniqueness
        name = mod.get("technical_name")
        if name:
            if name in seen_names:
                errors.append(
                    f"{path_label}: duplicate technical_name '{name}'"
                )
            seen_names.add(name)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate OCA must-have base SSOT registry"
    )
    parser.add_argument("--repo-root", default=os.getcwd(), help="Path to repo root")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    ssot_path = repo_root / SSOT_REL_PATH

    data = load_yaml(ssot_path)
    errors = validate(data, SSOT_REL_PATH)

    if errors:
        if not args.quiet:
            print(
                f"FAIL: oca-must-have-ssot validation failed ({len(errors)} errors):"
            )
            for err in errors:
                print(f"  {err}")
        sys.exit(3)

    n = len(data.get("modules", []))
    if not args.quiet:
        print(f"PASS: oca-must-have-ssot validated ({n} modules) — {SSOT_REL_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
