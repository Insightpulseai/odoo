#!/usr/bin/env python3
"""
Validate the repository structure against a defined schema (repo_structure_rules.json).
Enforces required directories, allowed top-level items, and forbidden patterns.
"""

import argparse
import fnmatch
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

ROOT_DIR = Path(__file__).resolve().parents[1]
RULES_FILE = ROOT_DIR / "docs" / "architecture" / "repo_structure_rules.json"


def load_rules() -> Dict[str, Any]:
    if not RULES_FILE.exists():
        print(f"Error: Rules file not found at {RULES_FILE}")
        sys.exit(1)
    try:
        with open(RULES_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in rules file: {e}")
        sys.exit(1)


def validate_structure(profile: str, rules: Dict[str, Any]) -> bool:
    print(f"Validating repository structure for profile: {profile}")

    if profile not in rules["repo_profiles"]:
        print(f"Error: Profile '{profile}' not found in rules.")
        return False

    profile_rules = rules["repo_profiles"][profile]
    required_dirs = profile_rules.get("required_dirs", [])
    allowed_top_level = set(profile_rules.get("allowed_top_level", []))
    forbidden_globs = profile_rules.get("forbidden_globs", [])

    success = True

    # 1. Check Required Directories
    print("\n[1/3] Checking Required Directories...")
    for d in required_dirs:
        path = ROOT_DIR / d
        if not path.is_dir():
            print(f"  ❌ Missing required directory: {d}/")
            success = False
        else:
            print(f"  ✅ Found {d}/")

    # 2. Check Allowed Top-Level Items
    print("\n[2/3] Checking Top-Level Structure...")
    # Get actual top-level items (files and dirs), excluding hidden .git
    actual_items = [
        item.name for item in ROOT_DIR.iterdir() if item.name != ".git" and item.name != ".DS_Store"
    ]

    unexpected_items = []
    for item in actual_items:
        if item not in allowed_top_level:
            unexpected_items.append(item)

    if unexpected_items:
        print(f"  ❌ Unexpected items in root directory:")
        for item in unexpected_items:
            print(f"     - {item}")
        print(f"  ℹ️  Allowed items: {', '.join(sorted(allowed_top_level))}")
        success = False
    else:
        print("  ✅ Top-level structure is compliant.")

    # 3. Check Forbidden Patterns
    print("\n[3/3] Checking Forbidden Patterns...")
    forbidden_found = []

    # We walk the tree, respecting .gitignore would be ideal but simple walk is safer for "forbidden" checks
    # limiting depth to avoid massive traversals if node_modules existed (not expected in root of odoo repo)

    for glob_pattern in forbidden_globs:
        # Recursive glob search
        # fnmatch doesn't support recursive ** well with os.walk manually,
        # using Path.rglob is better but need to match pattern style

        # Simple approach: rglob('*') and match against forbidden globs
        # But that is slow for large repos.
        # Let's try explicit checks for top-level forbidden first?
        # No, requirements say "forbidden patterns" like "**/.env"

        # We will use keys:
        # "config/*.env" -> specific path check
        # "**/.env" -> recursive check

        matches = list(ROOT_DIR.glob(glob_pattern))
        if matches:
            for m in matches:
                # Filter out if it matches but is actually inside a .git directory or something we assume ignored?
                # ideally we want to catch .env anywhere.
                rel_path = m.relative_to(ROOT_DIR)
                print(f"  ❌ Found forbidden file/dir: {rel_path} (Matches '{glob_pattern}')")
                success = False

    if success:
        print("\n✅ Repository structure validation passed!")
    else:
        print("\n❌ Repository structure validation failed.")

    return success


def main():
    parser = argparse.ArgumentParser(description="Validate repository structure.")
    parser.add_argument(
        "--profile", default="odoo", help="Repository profile to validate against (default: odoo)"
    )
    args = parser.parse_args()

    rules = load_rules()
    if validate_structure(args.profile, rules):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
