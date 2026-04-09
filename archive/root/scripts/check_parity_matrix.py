#!/usr/bin/env python3
"""
Parity Matrix Contract Gate

Validates ssot/parity/ee_to_oca_proof_matrix.yaml:
  1. All entries have required fields (ee_feature_id, parity_path, route, odoo18_support)
  2. Entries with parity_path oca_direct|oca_partial have non-empty oca_repo and oca_modules
  3. Entries with parity_path bridge have at least one evidence_link pointing to ipai_*
  4. Summary counts match actual entry counts
  5. All route values are in the allowed set
  6. All parity_path values are in the allowed set

Exit 0 = PASS, exit 1 = validation error, exit 2 = file/parse error.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. pip install pyyaml")
    sys.exit(2)

MATRIX_PATH = Path("ssot/parity/ee_to_oca_proof_matrix.yaml")

ALLOWED_PARITY_PATHS = {"oca_direct", "oca_partial", "bridge", "gap"}
ALLOWED_ROUTES = {"adopt_oca", "port_then_adopt", "bridge", "build_ipai", "accept_gap"}
ALLOWED_ODOO18 = {"yes", "needs_port", "unknown", "n/a"}
REQUIRED_FIELDS = ["ee_feature_id", "parity_path", "route", "odoo18_support"]


def main() -> int:
    if not MATRIX_PATH.exists():
        print(f"FAIL: {MATRIX_PATH} not found")
        return 2

    try:
        data = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        print(f"FAIL: YAML parse error: {e}")
        return 2

    entries = data.get("entries", [])
    if not isinstance(entries, list) or not entries:
        print("FAIL: No entries found")
        return 2

    summary = data.get("summary", {})
    errors: list[str] = []

    # Count accumulators
    parity_counts: dict[str, int] = {}
    route_counts: dict[str, int] = {}
    milestone_counts: dict[str, int] = {}

    for i, entry in enumerate(entries):
        fid = entry.get("ee_feature_id", f"<entry {i}>")

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in entry or entry[field] is None:
                errors.append(f"{fid}: missing required field '{field}'")

        # Check parity_path values
        pp = entry.get("parity_path")
        if pp and pp not in ALLOWED_PARITY_PATHS:
            errors.append(f"{fid}: invalid parity_path '{pp}'")
        if pp:
            parity_counts[pp] = parity_counts.get(pp, 0) + 1

        # Check route values
        route = entry.get("route")
        if route and route not in ALLOWED_ROUTES:
            errors.append(f"{fid}: invalid route '{route}'")
        if route:
            route_counts[route] = route_counts.get(route, 0) + 1

        # Check odoo18_support values
        o19 = str(entry.get("odoo18_support", ""))
        if o19 and o19 not in ALLOWED_ODOO18:
            errors.append(f"{fid}: invalid odoo18_support '{o19}'")

        # Count milestones
        ms = entry.get("milestone")
        if ms:
            milestone_counts[ms] = milestone_counts.get(ms, 0) + 1

        # OCA entries must have oca_repo and oca_modules
        if pp in ("oca_direct", "oca_partial"):
            if not entry.get("oca_repo"):
                errors.append(f"{fid}: parity_path={pp} but oca_repo is empty/null")
            mods = entry.get("oca_modules", [])
            if not mods or (isinstance(mods, list) and len(mods) == 0):
                errors.append(f"{fid}: parity_path={pp} but oca_modules is empty")

        # Bridge entries must have evidence_link with ipai_*
        if pp == "bridge":
            links = entry.get("evidence_links", [])
            has_ipai = any("ipai" in str(link.get("url", "")) for link in links if isinstance(link, dict))
            if not has_ipai:
                errors.append(f"{fid}: parity_path=bridge but no evidence_link references ipai_*")

    # Validate summary counts
    total = len(entries)
    if summary.get("total_entries") != total:
        errors.append(f"summary.total_entries={summary.get('total_entries')} but actual={total}")

    by_pp = summary.get("by_parity_path", {})
    for pp_key in ALLOWED_PARITY_PATHS:
        expected = by_pp.get(pp_key, 0)
        actual = parity_counts.get(pp_key, 0)
        if expected != actual:
            errors.append(f"summary.by_parity_path.{pp_key}={expected} but actual={actual}")

    by_route = summary.get("by_route", {})
    for rt_key in ALLOWED_ROUTES:
        expected = by_route.get(rt_key, 0)
        actual = route_counts.get(rt_key, 0)
        if expected != actual:
            errors.append(f"summary.by_route.{rt_key}={expected} but actual={actual}")

    if errors:
        print(f"FAIL: {len(errors)} validation error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"Parity matrix gate PASS ({total} entries, {len(parity_counts)} parity paths, {len(route_counts)} routes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
