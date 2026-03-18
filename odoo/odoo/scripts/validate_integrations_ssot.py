#!/usr/bin/env python3
"""Validate ssot/integrations/odoo-n8n-supabase.yaml against its JSON Schema.

Checks:
  1. YAML parses
  2. JSON Schema validation passes
  3. Each flow id is unique
  4. active flows have non-placeholder evidence_ref
  5. n8n flows with "replication" in name require exception_reason

Exit 0 on success, 1 on validation failure.
"""

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (relative to repo root)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
SSOT_YAML = REPO_ROOT / "ssot" / "integrations" / "odoo-n8n-supabase.yaml"
SCHEMA_JSON = REPO_ROOT / "ssot" / "integrations" / "odoo-n8n-supabase.schema.json"

# ---------------------------------------------------------------------------
# Imports — stdlib only; fall back gracefully for optional jsonschema
# ---------------------------------------------------------------------------
try:
    import yaml  # PyYAML — available in most Python envs
except ImportError:
    # Minimal YAML subset loader as fallback
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
        # Still do structural checks below

    flows = data.get("flows", [])
    if not isinstance(flows, list):
        errors.append("'flows' must be a list")
        _report(errors)
        return 1

    # --- Unique IDs ---
    print("Checking unique IDs ...")
    seen_ids: set[str] = set()
    for flow in flows:
        fid = flow.get("id", "<missing>")
        if fid in seen_ids:
            errors.append(f"Duplicate flow id: {fid}")
        seen_ids.add(fid)
    if not errors:
        print(f"  unique IDs: PASS ({len(seen_ids)} flows)")

    # --- Active flows need real evidence ---
    print("Checking evidence refs for active flows ...")
    placeholder_refs = {"", "TODO", "docs/evidence/integrations/README.md"}
    for flow in flows:
        if flow.get("state") == "active":
            ref = flow.get("evidence_ref", "")
            if ref in placeholder_refs:
                errors.append(
                    f"Active flow '{flow['id']}' has placeholder evidence_ref: '{ref}'. "
                    f"Provide a real evidence path or change state to 'planned'."
                )
    if not any("evidence_ref" in e for e in errors):
        print("  evidence refs: PASS")

    # --- n8n used for replication needs exception ---
    print("Checking n8n replication rule ...")
    replication_keywords = ["replication", "replicate", "bulk_sync", "etl", "warehouse_load"]
    for flow in flows:
        if flow.get("engine_type") == "n8n":
            name_lower = flow.get("name", "").lower()
            if any(kw in name_lower for kw in replication_keywords):
                if not flow.get("exception_reason"):
                    errors.append(
                        f"Flow '{flow['id']}' uses engine_type=n8n but name suggests "
                        f"canonical replication ('{flow['name']}'). Either change engine_type "
                        f"to supabase_etl or add an 'exception_reason' field."
                    )
    if not any("replication" in e for e in errors):
        print("  n8n replication rule: PASS")

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
