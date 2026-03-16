#!/usr/bin/env python3
"""
Sanity-check for Odoo Editions parity seed YAML.

Goal:
- Catch silent parser degradation (markup changes) that still produces "some rows".
- Fail fast in CI with actionable error messages.

Usage:
  python scripts/parity_seed_sanity_check.py spec/parity/odoo_editions_parity_seed.yaml
Env:
  PARITY_SEED_MIN_ROWS (default: 20)
  PARITY_SEED_MIN_AREAS (default: 8)
  PARITY_SEED_MIN_APPS (default: 20)
  PARITY_SEED_REQUIRE_AREAS (default: "Finance,Sales,HR,Websites")
  PARITY_SEED_REQUIRE_APPS (default: "Accounting,CRM,Inventory,Website")
"""

from __future__ import annotations

import os
import sys
from collections import Counter
from typing import Any, Dict, List

try:
    import yaml  # PyYAML
except Exception as e:
    print(f"ERROR: Missing dependency PyYAML. Install with: python -m pip install pyyaml\n{e}")
    sys.exit(2)


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}")
    sys.exit(code)


def warn(msg: str) -> None:
    print(f"WARNING: {msg}")


def read_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default)).strip()
    try:
        return int(raw)
    except ValueError:
        die(f"Env {name} must be int, got: {raw}", 2)
    return default


def parse_csv_env(name: str, default_csv: str) -> List[str]:
    raw = os.environ.get(name, default_csv)
    items = [x.strip() for x in raw.split(",") if x.strip()]
    return items


def main() -> None:
    if len(sys.argv) != 2:
        die("Usage: python scripts/parity_seed_sanity_check.py <path-to-yaml>", 2)

    path = sys.argv[1]
    data = read_yaml(path)

    # Accept parity_seed wrapper
    if "parity_seed" in data:
        data = data["parity_seed"]

    # Accept either schema:
    # - {"meta": {...}, "rows": [...]}
    # - {"metadata": {...}, "rows": [...]}
    rows = data.get("rows")
    if not isinstance(rows, list):
        die(f"YAML missing 'rows' list: {path}", 1)

    min_rows = get_env_int("PARITY_SEED_MIN_ROWS", 20)
    min_areas = get_env_int("PARITY_SEED_MIN_AREAS", 8)
    min_apps = get_env_int("PARITY_SEED_MIN_APPS", 20)

    req_areas = parse_csv_env("PARITY_SEED_REQUIRE_AREAS", "Finance,Sales,HR,Websites")
    req_apps = parse_csv_env("PARITY_SEED_REQUIRE_APPS", "Accounting,CRM,Inventory,Website")

    # Basic row count
    if len(rows) < min_rows:
        die(f"Too few rows: got {len(rows)}, expected ≥{min_rows}. Parser likely failed.", 1)

    # Shape checks
    areas = []
    apps = []
    feature_rows = 0
    app_rows = 0

    for i, r in enumerate(rows, start=1):
        if not isinstance(r, dict):
            die(f"Row {i} is not a dict.", 1)
        area = (r.get("area") or "").strip()
        app = (r.get("app") or "").strip()
        feature = r.get("feature")

        if not area or not app:
            die(f"Row {i} missing required fields area/app: {r}", 1)

        areas.append(area)
        apps.append(app)

        if feature is None:
            app_rows += 1
        else:
            if not isinstance(feature, str) or not feature.strip():
                die(f"Row {i} has empty feature.", 1)
            feature_rows += 1

    uniq_areas = sorted(set(areas))
    uniq_apps = sorted(set(apps))

    if len(uniq_areas) < min_areas:
        die(f"Too few unique areas: got {len(uniq_areas)}, expected ≥{min_areas}. Areas={uniq_areas}", 1)

    if len(uniq_apps) < min_apps:
        die(f"Too few unique apps: got {len(uniq_apps)}, expected ≥{min_apps}. Apps sample={uniq_apps[:30]}", 1)

    # Require a few canonical areas/apps to appear (catch markup shifts that change headings)
    missing_areas = [a for a in req_areas if a not in set(uniq_areas)]
    if missing_areas:
        die(f"Missing required areas: {missing_areas}. Seen areas={uniq_areas}", 1)

    missing_apps = [a for a in req_apps if a not in set(uniq_apps)]
    if missing_apps:
        die(f"Missing required apps: {missing_apps}. Seen apps sample={uniq_apps[:30]}", 1)

    # Ratio sanity: we expect many features; if nearly all rows are apps, parsing is wrong
    if feature_rows == 0:
        die("No feature rows detected (feature_rows=0). Parser likely failed.", 1)

    # Heuristic: features should be >= apps (usually a lot more)
    if feature_rows < app_rows:
        warn(f"Feature rows ({feature_rows}) < app rows ({app_rows}). This is suspicious; review output.")

    # Print a short summary (useful in CI logs)
    area_counts = Counter(areas).most_common(8)
    app_counts = Counter(apps).most_common(8)

    print("OK: parity seed sanity check passed")
    print(f"- rows: {len(rows)} (apps={app_rows}, features={feature_rows})")
    print(f"- unique areas: {len(uniq_areas)} | top: {area_counts}")
    print(f"- unique apps: {len(uniq_apps)} | top: {app_counts}")


if __name__ == "__main__":
    main()
