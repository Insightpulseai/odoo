#!/usr/bin/env python3
"""Validate ssot/api/unified-api-gateway.yaml against its JSON Schema.

Checks:
  1. YAML parses
  2. JSON Schema validation passes
  3. Route group IDs are unique
  4. Route prefixes are unique
  5. Blocked routes have a `blocker` field
  6. All `rate_limit_tier` values used in route_groups are defined in `rate_limit_tiers`
  7. Authority matrix domains match route group IDs
  8. Status enum is valid

Exit 0 on success, 1 on validation failure.
"""

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (relative to repo root)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
SSOT_YAML = REPO_ROOT / "ssot" / "api" / "unified-api-gateway.yaml"
SCHEMA_JSON = REPO_ROOT / "ssot" / "api" / "unified-api-gateway.schema.json"

# ---------------------------------------------------------------------------
# Imports — stdlib only; fall back gracefully for optional jsonschema
# ---------------------------------------------------------------------------
try:
    import yaml  # PyYAML — available in most Python envs
except ImportError:
    yaml = None

try:
    import jsonschema
except ImportError:
    jsonschema = None


def load_yaml(path: Path) -> dict:
    """Load YAML file, with or without PyYAML."""
    text = path.read_text()
    if yaml is not None:
        return yaml.safe_load(text)
    # Fallback: try json (works if YAML is JSON-compatible)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print("ERROR: PyYAML not installed and file is not JSON-compatible.")
        print("       Install PyYAML: pip install pyyaml")
        sys.exit(1)


VALID_STATUSES = {"planned", "active", "blocked", "deprecated"}


def main() -> int:
    errors: list[str] = []

    # --- Check files exist ---
    if not SSOT_YAML.exists():
        print(f"FAIL: SSOT file not found: {SSOT_YAML}")
        return 1

    if not SCHEMA_JSON.exists():
        print(f"FAIL: Schema file not found: {SCHEMA_JSON}")
        return 1

    # --- Parse ---
    print(f"Parsing {SSOT_YAML.relative_to(REPO_ROOT)} ...")
    data = load_yaml(SSOT_YAML)
    if data is None:
        errors.append("YAML parsed to None (empty file?)")
        _report(errors)
        return 1

    schema = json.loads(SCHEMA_JSON.read_text())

    # --- JSON Schema validation ---
    if jsonschema is not None:
        print("Validating against JSON Schema ...")
        try:
            jsonschema.validate(instance=data, schema=schema)
            print("  schema: PASS")
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed: {e.message} (path: {list(e.absolute_path)})")
    else:
        print("  WARN: jsonschema not installed — skipping schema validation")
        print("        Install: pip install jsonschema")

    route_groups = data.get("route_groups", [])
    if not isinstance(route_groups, list):
        errors.append("'route_groups' must be a list")
        _report(errors)
        return 1

    # --- Unique IDs ---
    print("Checking unique route group IDs ...")
    seen_ids: set[str] = set()
    for rg in route_groups:
        rid = rg.get("id", "<missing>")
        if rid in seen_ids:
            errors.append(f"Duplicate route group id: {rid}")
        seen_ids.add(rid)
    if not any("Duplicate route group id" in e for e in errors):
        print(f"  unique IDs: PASS ({len(seen_ids)} route groups)")

    # --- Unique prefixes ---
    print("Checking unique route prefixes ...")
    seen_prefixes: set[str] = set()
    for rg in route_groups:
        prefix = rg.get("prefix", "<missing>")
        if prefix in seen_prefixes:
            errors.append(f"Duplicate route prefix: {prefix}")
        seen_prefixes.add(prefix)
    if not any("Duplicate route prefix" in e for e in errors):
        print(f"  unique prefixes: PASS ({len(seen_prefixes)} prefixes)")

    # --- Blocked routes must have blocker ---
    print("Checking blocked routes have blocker field ...")
    for rg in route_groups:
        if rg.get("status") == "blocked":
            if not rg.get("blocker"):
                errors.append(
                    f"Route group '{rg.get('id')}' has status=blocked but no 'blocker' field"
                )
    if not any("blocker" in e for e in errors):
        print("  blocked routes: PASS")

    # --- Rate limit tier references ---
    print("Checking rate_limit_tier references ...")
    rate_limit_tiers = data.get("rate_limit_tiers", {})
    defined_tiers = set(rate_limit_tiers.keys()) if isinstance(rate_limit_tiers, dict) else set()
    for rg in route_groups:
        tier = rg.get("rate_limit_tier")
        if tier and tier not in defined_tiers:
            errors.append(
                f"Route group '{rg.get('id')}' uses rate_limit_tier '{tier}' "
                f"which is not defined in rate_limit_tiers. Defined: {sorted(defined_tiers)}"
            )
    if not any("rate_limit_tier" in e for e in errors):
        print(f"  rate limit tiers: PASS ({len(defined_tiers)} tiers defined)")

    # --- Authority matrix domains match route group IDs ---
    print("Checking authority matrix domain coverage ...")
    authority_matrix = data.get("authority_matrix", [])
    if isinstance(authority_matrix, list):
        authority_domains = {entry.get("domain") for entry in authority_matrix}
        for rid in seen_ids:
            if rid not in authority_domains:
                errors.append(
                    f"Route group '{rid}' has no matching entry in authority_matrix"
                )
        for domain in authority_domains:
            if domain not in seen_ids:
                errors.append(
                    f"Authority matrix domain '{domain}' has no matching route group"
                )
    if not any("authority_matrix" in e or "authority matrix" in e.lower() for e in errors):
        print("  authority matrix: PASS")

    # --- Valid status enum ---
    print("Checking status enum values ...")
    for rg in route_groups:
        status = rg.get("status")
        if status and status not in VALID_STATUSES:
            errors.append(
                f"Route group '{rg.get('id')}' has invalid status '{status}'. "
                f"Valid: {sorted(VALID_STATUSES)}"
            )
    if not any("invalid status" in e for e in errors):
        print("  status enum: PASS")

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
