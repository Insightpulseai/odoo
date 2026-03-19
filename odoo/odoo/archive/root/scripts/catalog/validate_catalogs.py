#!/usr/bin/env python3
"""
validate_catalogs.py
────────────────────
Validate all *.catalog.json files in docs/catalog/.

Exit codes:
  0  All catalogs valid
  1  Validation error — see output
  2  Usage / system error

Usage:
  python3 scripts/catalog/validate_catalogs.py
  python3 scripts/catalog/validate_catalogs.py --verbose
"""

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
CATALOG_DIR = REPO_ROOT / "docs" / "catalog"

REQUIRED_TOP_KEYS = {"version", "source", "items"}
REQUIRED_SOURCE_KEYS = {"provider", "type", "base_url"}
REQUIRED_ITEM_KEYS = {"id", "title", "url", "tags", "use_cases", "adoption_level", "what_to_lift", "risk", "status", "last_reviewed"}

ALLOWED_PROVIDERS = {"vercel", "supabase"}
ALLOWED_TYPES = {"examples", "templates", "ui", "platform-kit"}
ALLOWED_ADOPTION_LEVELS = {"reference", "harvest", "adopt"}
ALLOWED_RISKS = {"low", "medium", "high"}
ALLOWED_STATUSES = {"candidate", "approved", "deprecated"}
ALLOWED_USE_CASES = {"ops-console", "odoo-runtime", "observability", "platform-kit", "ai-ops-agent", "multi-tenant", "marketing"}

VERBOSE = "--verbose" in sys.argv


def err(msg: str) -> None:
    print(f"  ERROR: {msg}", file=sys.stderr)


def ok(msg: str) -> None:
    if VERBOSE:
        print(f"  ✓ {msg}")


def validate_catalog(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]

    # Top-level keys
    missing_top = REQUIRED_TOP_KEYS - set(data.keys())
    if missing_top:
        errors.append(f"Missing top-level keys: {sorted(missing_top)}")
        return errors  # Can't proceed without these

    # Source block
    source = data.get("source", {})
    missing_src = REQUIRED_SOURCE_KEYS - set(source.keys())
    if missing_src:
        errors.append(f"source: missing keys: {sorted(missing_src)}")
    else:
        if source.get("provider") not in ALLOWED_PROVIDERS:
            errors.append(f"source.provider must be one of {sorted(ALLOWED_PROVIDERS)}, got '{source.get('provider')}'")
        if source.get("type") not in ALLOWED_TYPES:
            errors.append(f"source.type must be one of {sorted(ALLOWED_TYPES)}, got '{source.get('type')}'")

    # Items
    items = data.get("items", [])
    if not isinstance(items, list) or len(items) == 0:
        errors.append("items must be a non-empty list")
        return errors

    seen_ids: set[str] = set()
    seen_urls: set[str] = set()

    for i, item in enumerate(items):
        prefix = f"items[{i}] (id={item.get('id', '?')})"

        missing_item = REQUIRED_ITEM_KEYS - set(item.keys())
        if missing_item:
            errors.append(f"{prefix}: missing keys: {sorted(missing_item)}")
            continue

        item_id = item.get("id", "")
        if not item_id or not item_id.replace("-", "").replace("_", "").isalnum():
            errors.append(f"{prefix}: id must be alphanumeric/hyphen, got '{item_id}'")

        if item_id in seen_ids:
            errors.append(f"{prefix}: duplicate id '{item_id}'")
        seen_ids.add(item_id)

        url = item.get("url", "")
        if url in seen_urls:
            errors.append(f"{prefix}: duplicate url '{url}'")
        seen_urls.add(url)

        if item.get("adoption_level") not in ALLOWED_ADOPTION_LEVELS:
            errors.append(f"{prefix}: adoption_level must be one of {sorted(ALLOWED_ADOPTION_LEVELS)}, got '{item.get('adoption_level')}'")

        if item.get("risk") not in ALLOWED_RISKS:
            errors.append(f"{prefix}: risk must be one of {sorted(ALLOWED_RISKS)}, got '{item.get('risk')}'")

        if item.get("status") not in ALLOWED_STATUSES:
            errors.append(f"{prefix}: status must be one of {sorted(ALLOWED_STATUSES)}, got '{item.get('status')}'")

        bad_use_cases = set(item.get("use_cases", [])) - ALLOWED_USE_CASES
        if bad_use_cases:
            errors.append(f"{prefix}: unknown use_cases: {sorted(bad_use_cases)}")

        what_to_lift = item.get("what_to_lift", [])
        if not isinstance(what_to_lift, list) or len(what_to_lift) == 0:
            errors.append(f"{prefix}: what_to_lift must be a non-empty list")

        ok(f"{item_id}")

    return errors


def main() -> int:
    catalog_files = sorted(CATALOG_DIR.glob("*.catalog.json"))
    if not catalog_files:
        print(f"ERROR: No *.catalog.json files found in {CATALOG_DIR}", file=sys.stderr)
        return 2

    total_errors = 0
    for path in catalog_files:
        rel = path.relative_to(REPO_ROOT)
        errors = validate_catalog(path)
        if errors:
            print(f"\n❌ {rel} ({len(errors)} error(s)):")
            for e in errors:
                err(e)
            total_errors += len(errors)
        else:
            item_count = len(json.loads(path.read_text()).get("items", []))
            print(f"✅ {rel} ({item_count} items)")

    if total_errors > 0:
        print(f"\n{total_errors} validation error(s) found. Fix before committing.", file=sys.stderr)
        return 1

    print(f"\nAll {len(catalog_files)} catalog(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
