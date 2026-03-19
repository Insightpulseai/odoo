#!/usr/bin/env python3
"""Render OCA install plan from SSOT without executing anything.

Pure read-only tool. Reads oca_repos.yaml + oca_lock.yaml and outputs
a formatted install plan. Used by CI dry-run and humans.

Usage:
  python scripts/odoo/render_oca_install_plan.py [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from install_oca_from_ssot import (
    DEFAULT_LOCK,
    DEFAULT_REGISTRY,
    DEFAULT_TARGET,
    load_lock,
    load_registry,
    print_plan_table,
    resolve_plan,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render OCA install plan from SSOT (read-only)"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--registry", type=Path, default=DEFAULT_REGISTRY,
        help="Path to oca_repos.yaml",
    )
    parser.add_argument(
        "--lock", type=Path, default=DEFAULT_LOCK,
        help="Path to oca_lock.yaml",
    )
    args = parser.parse_args()

    try:
        registry = load_registry(args.registry)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    lock = load_lock(args.lock)
    plan = resolve_plan(registry, lock, DEFAULT_TARGET, strict=False)

    if args.json:
        print(json.dumps(plan.to_dict(), indent=2))
    else:
        print_plan_table(plan)

    return 1 if plan.errors else 0


if __name__ == "__main__":
    sys.exit(main())
