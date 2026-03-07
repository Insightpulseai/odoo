#!/usr/bin/env python3
from __future__ import annotations

"""Validate docs/governance/repository_taxonomy.yaml against its JSON schema.

Checks:
  - YAML file exists and is parseable
  - JSON schema file exists (optional -- falls back to manual checks)
  - All repos have required fields: name, slug, type, status
  - ``type`` is one of the allowed values
  - ``status`` is one of the allowed values
  - No duplicate slugs

Uses PyYAML for parsing. Falls back to a basic manual parser if unavailable.
Uses jsonschema for schema validation if available; otherwise manual checks.

Exit 0 on pass, exit 1 on fail.
"""

import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TAXONOMY_PATH = os.path.join(REPO_ROOT, "docs", "governance", "repository_taxonomy.yaml")
SCHEMA_PATH = os.path.join(REPO_ROOT, "docs", "governance", "repository_taxonomy.schema.json")

ALLOWED_TYPES = {
    "application",
    "library",
    "service",
    "infrastructure",
    "documentation",
    "config",
    "module",
    "platform",
    "tool",
    "agent",
    "monorepo",
    "archive",
}

ALLOWED_STATUSES = {
    "active",
    "deprecated",
    "archived",
    "planned",
    "experimental",
    "maintenance",
}

REQUIRED_FIELDS = ["name", "slug", "type", "status"]


def load_yaml(path: str):
    """Load YAML file, trying PyYAML first, then a minimal fallback."""
    try:
        import yaml  # type: ignore[import-untyped]

        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        # Minimal fallback: read as structured text (only handles flat lists of dicts)
        return _fallback_yaml_load(path)


def _fallback_yaml_load(path: str):
    """Extremely minimal YAML list-of-dicts parser for CI environments without PyYAML."""
    items: list[dict] = []
    current: dict | None = None
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip()
            if not line or line.startswith("#"):
                continue
            # Top-level list item
            if line.startswith("- "):
                if current is not None:
                    items.append(current)
                current = {}
                line = line[2:]
            if current is None:
                # Could be a top-level key wrapping a list; try to handle
                if ":" in line:
                    # e.g., "repositories:"
                    continue
                continue
            line = line.strip()
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip().strip('"').strip("'")
                value = value.strip().strip('"').strip("'")
                if value:
                    current[key] = value
    if current is not None:
        items.append(current)
    # Wrap in expected structure
    if items:
        return {"repositories": items}
    return None


def validate_with_jsonschema(data, schema) -> list[str]:
    """Validate data against JSON Schema. Returns list of error strings."""
    try:
        import jsonschema  # type: ignore[import-untyped]
    except ImportError:
        return ["jsonschema not installed -- skipping schema validation"]

    errors: list[str] = []
    validator = jsonschema.Draft7Validator(schema)
    for error in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        path = ".".join(str(p) for p in error.absolute_path) or "(root)"
        errors.append(f"Schema: {path}: {error.message}")
    return errors


def manual_validate(repos: list) -> list[str]:
    """Run manual field-level checks on the repository list."""
    errors: list[str] = []
    slugs_seen: dict[str, int] = {}

    for idx, repo in enumerate(repos):
        label = repo.get("name") or repo.get("slug") or f"entry[{idx}]"

        # Required fields
        for field in REQUIRED_FIELDS:
            if field not in repo or not repo[field]:
                errors.append(f'Repo "{label}": missing required field "{field}"')

        # Type validation
        repo_type = repo.get("type", "")
        if repo_type and repo_type not in ALLOWED_TYPES:
            errors.append(
                f'Repo "{label}": type "{repo_type}" not in allowed values: '
                f'{sorted(ALLOWED_TYPES)}'
            )

        # Status validation
        repo_status = repo.get("status", "")
        if repo_status and repo_status not in ALLOWED_STATUSES:
            errors.append(
                f'Repo "{label}": status "{repo_status}" not in allowed values: '
                f'{sorted(ALLOWED_STATUSES)}'
            )

        # Duplicate slug tracking
        slug = repo.get("slug", "")
        if slug:
            if slug in slugs_seen:
                errors.append(
                    f'Duplicate slug "{slug}" found at entries {slugs_seen[slug]} and {idx}'
                )
            else:
                slugs_seen[slug] = idx

    return errors


def main() -> int:
    errors: list[str] = []
    info: list[str] = []

    # ------------------------------------------------------------------
    # 1. Check taxonomy file exists
    # ------------------------------------------------------------------
    if not os.path.isfile(TAXONOMY_PATH):
        errors.append(f"Taxonomy file missing: {TAXONOMY_PATH}")
        return _report(errors, info)

    # ------------------------------------------------------------------
    # 2. Load YAML
    # ------------------------------------------------------------------
    try:
        data = load_yaml(TAXONOMY_PATH)
    except Exception as exc:
        errors.append(f"Failed to parse YAML: {exc}")
        return _report(errors, info)

    if data is None:
        errors.append("Taxonomy file is empty or unparseable")
        return _report(errors, info)

    # ------------------------------------------------------------------
    # 3. Extract repository list
    # ------------------------------------------------------------------
    repos: list | None = None
    if isinstance(data, list):
        repos = data
    elif isinstance(data, dict):
        repos = data.get("repositories") or data.get("repos")
        if repos is None:
            # Try first list-valued key
            for v in data.values():
                if isinstance(v, list):
                    repos = v
                    break
    if not repos or not isinstance(repos, list):
        errors.append(
            "Taxonomy must contain a list of repositories (top-level list or 'repositories' key)"
        )
        return _report(errors, info)

    info.append(f"Found {len(repos)} repositories in taxonomy")

    # ------------------------------------------------------------------
    # 4. JSON Schema validation (if schema file exists)
    # ------------------------------------------------------------------
    if os.path.isfile(SCHEMA_PATH):
        try:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema = json.load(f)
            schema_errors = validate_with_jsonschema(data, schema)
            errors.extend(schema_errors)
            if not schema_errors:
                info.append("JSON Schema validation passed")
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in schema file: {exc}")
    else:
        info.append(f"Schema file not found ({SCHEMA_PATH}), using manual checks only")

    # ------------------------------------------------------------------
    # 5. Manual field-level validation (always runs)
    # ------------------------------------------------------------------
    manual_errors = manual_validate(repos)
    errors.extend(manual_errors)

    return _report(errors, info)


def _report(errors: list[str], info: list[str]) -> int:
    print("=" * 60)
    print("Repository Taxonomy Validator")
    print("=" * 60)

    if info:
        for i in info:
            print(f"  INFO: {i}")

    if errors:
        print()
        for e in errors:
            print(f"  FAIL: {e}")
        print()
        print(f"Result: FAILED ({len(errors)} error(s))")
        print("=" * 60)
        return 1

    print()
    print("  All taxonomy checks passed.")
    print()
    print("Result: PASSED")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
