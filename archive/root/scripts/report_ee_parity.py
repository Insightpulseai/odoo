#!/usr/bin/env python3
"""
Generate EE Parity Report from Mapping YAML

Summarizes the parity mapping by strategy, priority, and status.
"""

import json
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

MAPPING_PATH = Path("config/ee_parity/ee_parity_mapping.yml")


def get_strategy(item: dict) -> str:
    """Extract strategy from mapping item."""
    for key in ("strategy", "replacement", "parity_strategy", "type"):
        if key in item:
            return str(item[key]).strip()
    return "UNKNOWN"


def get_priority(item: dict) -> str:
    """Extract priority from mapping item."""
    return item.get("priority", "unset")


def get_status(item: dict) -> str:
    """Extract status from mapping item."""
    return item.get("status", "unmapped")


def main():
    if not MAPPING_PATH.exists():
        print(f"ERROR: Mapping file not found: {MAPPING_PATH}")
        sys.exit(1)

    data = yaml.safe_load(MAPPING_PATH.read_text(encoding="utf-8"))

    # Extract features list (try multiple keys)
    features = data.get("features", []) or data.get("mapping", [])
    if not features:
        # Fallback: try to parse as list directly
        if isinstance(data, list):
            features = data

    if not features:
        print(f"WARNING: No features found in {MAPPING_PATH}")
        sys.exit(0)

    total = len(features)

    # Count by strategy
    strategy_counts = Counter(get_strategy(f) for f in features)

    # Count by priority
    priority_counts = Counter(get_priority(f) for f in features)

    # Count by status
    status_counts = Counter(get_status(f) for f in features)

    # Calculate implementation progress
    implemented = sum(
        1 for f in features
        if get_status(f) in ("verified", "installed", "implemented")
    )
    planned = sum(1 for f in features if get_status(f) == "planned")
    unmapped = sum(
        1 for f in features
        if get_status(f) in ("unmapped", "unknown")
    )

    # Print report
    print("=" * 60)
    print("ODOO EE PARITY MAPPING REPORT")
    print("=" * 60)
    print(f"File: {MAPPING_PATH}")
    print(f"Total mapped features: {total}")
    print()

    print("BY STRATEGY:")
    for strategy, count in strategy_counts.most_common():
        pct = (count / total * 100) if total else 0
        print(f"  {strategy:20s}: {count:3d} ({pct:5.1f}%)")
    print()

    print("BY PRIORITY:")
    for priority, count in sorted(priority_counts.items()):
        pct = (count / total * 100) if total else 0
        print(f"  {priority:20s}: {count:3d} ({pct:5.1f}%)")
    print()

    print("BY STATUS:")
    for status, count in status_counts.most_common():
        pct = (count / total * 100) if total else 0
        print(f"  {status:20s}: {count:3d} ({pct:5.1f}%)")
    print()

    # Implementation summary
    impl_pct = (implemented / total * 100) if total else 0
    print("IMPLEMENTATION SUMMARY:")
    print(f"  Implemented/Verified: {implemented:3d} ({impl_pct:.1f}%)")
    print(f"  Planned:              {planned:3d}")
    print(f"  Unmapped:             {unmapped:3d}")
    print()

    # Target check
    target = 80.0
    if impl_pct >= target:
        print(f"STATUS: PASS - Parity target {target}% met ({impl_pct:.1f}%)")
        sys.exit(0)
    else:
        gap = target - impl_pct
        needed = int(gap * total / 100) + 1
        print(f"STATUS: IN PROGRESS - {impl_pct:.1f}% < {target}% target")
        print(f"  Need ~{needed} more features implemented to reach target")
        sys.exit(0)  # Don't fail - this is informational


if __name__ == "__main__":
    main()
