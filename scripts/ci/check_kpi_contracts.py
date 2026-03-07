#!/usr/bin/env python3
from __future__ import annotations

"""Validate platform/data/contracts/ KPI and event contract files.

Checks:
  - control_room_kpis.yaml exists and is parseable
  - control_room_events.yaml exists and is parseable
  - KPIs have required fields: id, name, owner, source, target
  - Events have required fields: id, name, source, schema
  - All KPI IDs are unique
  - All event IDs are unique
  - Event kpi_linkage references (if present) point to valid KPI IDs

Exit 0 on pass, exit 1 on fail.
"""

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONTRACTS_DIR = os.path.join(REPO_ROOT, "platform", "data", "contracts")

KPI_FILE = os.path.join(CONTRACTS_DIR, "control_room_kpis.yaml")
EVENTS_FILE = os.path.join(CONTRACTS_DIR, "control_room_events.yaml")

KPI_REQUIRED_FIELDS = ["id", "name", "owner", "source", "target"]
EVENT_REQUIRED_FIELDS = ["id", "name", "source", "schema"]


def load_yaml(path: str):
    """Load YAML file using PyYAML if available, otherwise minimal fallback."""
    try:
        import yaml  # type: ignore[import-untyped]

        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        return _fallback_yaml_load(path)


def _fallback_yaml_load(path: str):
    """Minimal YAML parser for flat list-of-dicts structures."""
    items: list[dict] = []
    current: dict | None = None
    top_key: str | None = None
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip()
            if not line or line.startswith("#"):
                continue
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            # Top-level key (e.g., "kpis:" or "events:")
            if indent == 0 and stripped.endswith(":") and not stripped.startswith("-"):
                top_key = stripped[:-1].strip()
                continue
            # List item start
            if stripped.startswith("- "):
                if current is not None:
                    items.append(current)
                current = {}
                stripped = stripped[2:]
            if current is None:
                continue
            stripped = stripped.strip()
            if ":" in stripped:
                key, _, value = stripped.partition(":")
                key = key.strip().strip('"').strip("'")
                value = value.strip().strip('"').strip("'")
                if value:
                    current[key] = value
    if current is not None:
        items.append(current)
    if top_key and items:
        return {top_key: items}
    return items if items else None


def extract_items(data, *keys: str) -> list | None:
    """Try to extract a list from data, trying given dict keys or direct list."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in keys:
            if k in data and isinstance(data[k], list):
                return data[k]
        # Try first list value
        for v in data.values():
            if isinstance(v, list):
                return v
    return None


def validate_items(
    items: list,
    required_fields: list[str],
    item_type: str,
) -> tuple[list[str], set[str]]:
    """Validate a list of items for required fields and uniqueness.

    Returns (errors, set_of_ids).
    """
    errors: list[str] = []
    ids_seen: dict[str, int] = {}
    all_ids: set[str] = set()

    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{item_type}[{idx}]: expected a mapping/dict, got {type(item).__name__}")
            continue

        label = item.get("name") or item.get("id") or f"{item_type}[{idx}]"

        # Required fields
        for field in required_fields:
            if field not in item or not item[field]:
                errors.append(f'{item_type} "{label}": missing required field "{field}"')

        # ID uniqueness
        item_id = item.get("id")
        if item_id:
            item_id_str = str(item_id)
            all_ids.add(item_id_str)
            if item_id_str in ids_seen:
                errors.append(
                    f'{item_type}: duplicate ID "{item_id_str}" '
                    f"at entries {ids_seen[item_id_str]} and {idx}"
                )
            else:
                ids_seen[item_id_str] = idx

    return errors, all_ids


def validate_kpi_linkage(events: list, valid_kpi_ids: set[str]) -> list[str]:
    """Check that event kpi_linkage references point to valid KPI IDs."""
    errors: list[str] = []

    for idx, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        label = event.get("name") or event.get("id") or f"event[{idx}]"

        linkage = event.get("kpi_linkage")
        if linkage is None:
            continue

        # kpi_linkage can be a single string or a list
        if isinstance(linkage, str):
            refs = [linkage]
        elif isinstance(linkage, list):
            refs = linkage
        else:
            refs = [str(linkage)]

        for ref in refs:
            ref_str = str(ref).strip()
            if ref_str and ref_str not in valid_kpi_ids:
                errors.append(
                    f'Event "{label}": kpi_linkage references unknown KPI ID "{ref_str}". '
                    f"Valid IDs: {sorted(valid_kpi_ids)}"
                )

    return errors


def main() -> int:
    errors: list[str] = []
    info: list[str] = []

    # ------------------------------------------------------------------
    # 1. Check contracts directory
    # ------------------------------------------------------------------
    if not os.path.isdir(CONTRACTS_DIR):
        errors.append(f"Contracts directory missing: {CONTRACTS_DIR}")
        return _report(errors, info)

    # ------------------------------------------------------------------
    # 2. Load and validate KPIs
    # ------------------------------------------------------------------
    kpi_ids: set[str] = set()

    if not os.path.isfile(KPI_FILE):
        errors.append(f"KPI contract file missing: {KPI_FILE}")
    else:
        try:
            kpi_data = load_yaml(KPI_FILE)
        except Exception as exc:
            errors.append(f"Failed to parse KPI YAML: {exc}")
            kpi_data = None

        if kpi_data is not None:
            kpis = extract_items(kpi_data, "kpis", "metrics", "indicators")
            if kpis is None:
                errors.append("KPI file must contain a list of KPIs")
            else:
                info.append(f"Found {len(kpis)} KPIs")
                kpi_errors, kpi_ids = validate_items(kpis, KPI_REQUIRED_FIELDS, "KPI")
                errors.extend(kpi_errors)
        else:
            errors.append("KPI file is empty or unparseable")

    # ------------------------------------------------------------------
    # 3. Load and validate events
    # ------------------------------------------------------------------
    if not os.path.isfile(EVENTS_FILE):
        errors.append(f"Events contract file missing: {EVENTS_FILE}")
    else:
        try:
            events_data = load_yaml(EVENTS_FILE)
        except Exception as exc:
            errors.append(f"Failed to parse events YAML: {exc}")
            events_data = None

        if events_data is not None:
            events = extract_items(events_data, "events", "event_contracts")
            if events is None:
                errors.append("Events file must contain a list of events")
            else:
                info.append(f"Found {len(events)} events")
                event_errors, _ = validate_items(events, EVENT_REQUIRED_FIELDS, "Event")
                errors.extend(event_errors)

                # Cross-reference: kpi_linkage -> valid KPI IDs
                if kpi_ids:
                    linkage_errors = validate_kpi_linkage(events, kpi_ids)
                    errors.extend(linkage_errors)
                elif not kpi_ids and any(
                    isinstance(e, dict) and e.get("kpi_linkage") for e in events
                ):
                    info.append(
                        "Events reference KPI linkages but no valid KPIs were loaded -- "
                        "linkage validation skipped"
                    )
        else:
            errors.append("Events file is empty or unparseable")

    return _report(errors, info)


def _report(errors: list[str], info: list[str]) -> int:
    print("=" * 60)
    print("KPI Contracts Validator")
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
    print("  All KPI contract checks passed.")
    print()
    print("Result: PASSED")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
