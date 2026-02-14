#!/usr/bin/env python3
"""
OCA Must-Have CE19 Overlap Filter

Deterministic filtering algorithm that excludes modules absorbed into Odoo 19 CE core.

Usage:
    python check_overlap.py --dry-run          # Show JSON output without changes
    python check_overlap.py --test-exclusions  # Run unit tests
    python check_overlap.py --strict           # Exit 1 if any exclusions found

Design:
    - Explicit exclusion dictionary (single source of truth)
    - Deterministic: same input → same output every time
    - Evidence-based: each exclusion has rationale string
    - CI-ready: exit codes for automated validation

Exclusions:
    - web_advanced_search: Absorbed into CE17+ core search functionality
    - mail_activity_plan: Absorbed into CE17+ core activity planning
"""

import argparse
import json
import sys
from typing import List, Dict, Tuple

# Explicit Exclusion List (Single Source of Truth)
EXCLUDED_MODULES = {
    "web_advanced_search": "Absorbed into CE17+ core search functionality",
    "mail_activity_plan": "Absorbed into CE17+ core activity planning"
}


def filter_modules(candidate_list: List[str]) -> Tuple[List[str], Dict]:
    """Filter candidate modules, excluding CE19 overlaps.

    Args:
        candidate_list: List of candidate OCA module names

    Returns:
        Tuple of (included_modules, excluded_modules_with_rationale)
    """
    included = []
    excluded = {}

    for module in candidate_list:
        if module in EXCLUDED_MODULES:
            excluded[module] = EXCLUDED_MODULES[module]
        else:
            included.append(module)

    return included, excluded


def main():
    parser = argparse.ArgumentParser(
        description="Filter OCA modules for CE19 overlap",
        epilog="Exit codes: 0=success, 1=validation failure"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show output without writing files (JSON format)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if any exclusions found (CI validation mode)"
    )
    parser.add_argument(
        "--test-exclusions",
        action="store_true",
        help="Run unit tests on exclusion list"
    )
    args = parser.parse_args()

    # Test mode
    if args.test_exclusions:
        try:
            assert "web_advanced_search" in EXCLUDED_MODULES, \
                "web_advanced_search must be in EXCLUDED_MODULES"
            assert "mail_activity_plan" in EXCLUDED_MODULES, \
                "mail_activity_plan must be in EXCLUDED_MODULES"
            assert len(EXCLUDED_MODULES) == 2, \
                f"Expected 2 exclusions, got {len(EXCLUDED_MODULES)}"

            # Verify rationale strings exist
            for module, rationale in EXCLUDED_MODULES.items():
                assert isinstance(rationale, str) and len(rationale) > 0, \
                    f"Module {module} must have non-empty rationale string"

            print("✅ Exclusion tests passed")
            print(f"   - {len(EXCLUDED_MODULES)} exclusions validated")
            print(f"   - All rationale strings present")
            return 0
        except AssertionError as e:
            print(f"❌ Exclusion test failed: {e}")
            return 1

    # Dry-run mode: output JSON
    if args.dry_run:
        result = {
            "excluded_modules": EXCLUDED_MODULES,
            "exclusion_count": len(EXCLUDED_MODULES),
            "policy": "explicit_ce19_overlap",
            "validation": "deterministic_hardcoded_list"
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    # Strict mode: fail if any exclusions
    if args.strict:
        if len(EXCLUDED_MODULES) > 0:
            print(f"❌ Strict mode: {len(EXCLUDED_MODULES)} exclusions found", file=sys.stderr)
            for module, rationale in EXCLUDED_MODULES.items():
                print(f"   - {module}: {rationale}", file=sys.stderr)
            return 1
        else:
            print("✅ Strict mode: No exclusions found")
            return 0

    # Normal mode: show exclusions
    print(f"OCA Must-Have CE19 Overlap Filter")
    print(f"  Total exclusions: {len(EXCLUDED_MODULES)}")
    print(f"  Policy: Explicit hardcoded list")
    print()

    for module, rationale in sorted(EXCLUDED_MODULES.items()):
        print(f"  ⚠️  {module}")
        print(f"      Rationale: {rationale}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
