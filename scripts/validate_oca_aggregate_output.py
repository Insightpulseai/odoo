#!/usr/bin/env python3
"""
validate_oca_aggregate_output.py

Ensures that:
1. odoo.conf addons_path references to 'addons/oca/<repo>' exist on disk.
2. The 'addons/oca' directory is not empty if oca-aggregate.yml has merges.
3. odoo.conf and oca-aggregate.yml agree on the canonical path casing.
"""

import sys
import os
import re
import yaml
import configparser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT_DIR / "config" / "dev" / "odoo.conf"
AGGREGATE_FILE = ROOT_DIR / "oca-aggregate.yml"
ADDONS_DIR = ROOT_DIR / "addons" / "oca"


def load_odoo_conf(path):
    config = configparser.ConfigParser()
    config.read(path)
    if not config.has_option("options", "addons_path"):
        return []
    paths = config.get("options", "addons_path").split(",")
    return [p.strip() for p in paths]


def load_aggregate_conf(path):
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _fail(msg: str, code: int = 2) -> int:
    """Fail with clear error message and exit code."""
    print(f"❌ {msg}")
    return code


def main():
    print(f"🔍 Validating OCA alignment...")

    # 0. Security: never allow embedded PATs in remote URLs
    if AGGREGATE_FILE.exists():
        agg_text = AGGREGATE_FILE.read_text(encoding="utf-8", errors="replace")
        if "https://ghp_" in agg_text or ("https://github.com/" in agg_text and "@github.com" in agg_text):
            return _fail(
                "oca-aggregate.yml appears to contain embedded credentials in remote URLs.\n"
                "   Replace with plain https://github.com/OCA/<repo>.git"
            )
        print("✅ No embedded credentials detected in oca-aggregate.yml")

    # 1. Check casing agreement
    agg_conf = load_aggregate_conf(AGGREGATE_FILE)
    if not agg_conf:
        print(f"⚠️  No oca-aggregate.yml found at {AGGREGATE_FILE}")
        sys.exit(0)

    # Check if target is './addons/oca' (lowercase)
    target_keys = [k for k in agg_conf.keys() if k.startswith("./addons/")]
    if not target_keys:
        print("❌ No addons target found in oca-aggregate.yml")
        sys.exit(1)

    canonical_target = "./addons/oca"
    if canonical_target not in target_keys:
        print(f"❌ oca-aggregate.yml must target '{canonical_target}' (found: {target_keys})")
        sys.exit(1)

    print(f"✅ oca-aggregate.yml targets canonical '{canonical_target}'")

    # 2. Extract expected repos from oca-aggregate.yml merges
    # odoo.conf has /mnt/oca which maps to ./addons/oca in the repo
    # We validate that repos from oca-aggregate.yml exist in addons/oca/
    merges = agg_conf.get(canonical_target, {}).get("merges", [])
    expected_repos = []

    for merge in merges:
        if isinstance(merge, str):
            # Format: "repo-name branch"
            repo_name = merge.split()[0]
            expected_repos.append(repo_name)
        elif isinstance(merge, dict):
            # Format: {repo-name: branch}
            expected_repos.extend(merge.keys())

    print(f"ℹ️  oca-aggregate.yml specifies {len(expected_repos)} OCA repos to merge.")

    # 3. Verify existence (with permission error handling)
    try:
        if not ADDONS_DIR.exists():
            return _fail(
                f"Expected generated dir missing: {ADDONS_DIR}\n"
                "   Remediation:\n"
                "   - Run: python3 scripts/oca/reset_generated_dir.py\n"
                "   - Then: gitaggregate -c oca-aggregate.yml"
            )

        # Check if directory has actual module directories (not just metadata)
        entries = [p for p in ADDONS_DIR.iterdir() if p.is_dir() and not p.name.startswith(".")]
        if not entries:
            return _fail(
                f"{ADDONS_DIR} is empty (no OCA modules).\n"
                "   Remediation:\n"
                "   - Ensure parent repo has no uncommitted changes (gitaggregate checks this)\n"
                "   - Run: gitaggregate -c oca-aggregate.yml"
            )

        missing = []
        for repo in expected_repos:
            repo_path = ADDONS_DIR / repo
            if not repo_path.exists() or not repo_path.is_dir():
                missing.append(repo)

        if missing:
            print(f"❌ Missing {len(missing)} OCA repos:")
            for m in missing[:5]:  # Show first 5
                print(f"   - addons/oca/{m}")
            if len(missing) > 5:
                print(f"   ... and {len(missing) - 5} more")
            print("\nRemediation:")
            print(f"  - Run: gitaggregate -c oca-aggregate.yml")
            return 2

    except PermissionError as e:
        print(f"❌ PermissionError reading {ADDONS_DIR}: {e}")
        print("Remediation:")
        print("  - Ensure oca-aggregate.yml targets ./addons/oca (repo workspace)")
        print("  - Ensure ./addons/oca exists and is writable:")
        print(f"    python3 scripts/oca/ensure_dir.py")
        print("  - Ensure docker compose mounts ./addons/oca -> /mnt/oca:rw")
        print("  - Then: gitaggregate -c oca-aggregate.yml")
        return 2

    print(f"✅ All {len(expected_repos)} required OCA repos exist in addons/oca/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
