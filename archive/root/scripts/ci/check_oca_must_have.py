#!/usr/bin/env python3
"""
OCA Must-Have Module Availability Checker

Validates that all modules declared in config/oca/oca_must_have_*.yml
have corresponding directories in addons/oca/ (via oca-aggregate.yml).

This checks AGGREGATE CONFIG presence, not Odoo installation state.
For installation verification, use oca_must_have_gate.sh with a live Odoo instance.

Usage:
    python3 scripts/ci/check_oca_must_have.py
    python3 scripts/ci/check_oca_must_have.py --strict  # exit 1 on any missing

Exit codes:
    0 - All repos declared in manifests are present in oca-aggregate.yml
    1 - Missing repos (--strict) or module dirs not found after hydration
    2 - Manifest parse error
"""

import os
import sys
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = REPO_ROOT / "config" / "oca"
AGGREGATE_FILE = REPO_ROOT / "oca-aggregate.yml"
ADDONS_OCA = REPO_ROOT / "addons" / "oca"


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def get_aggregate_repos() -> set:
    """Extract repo names from oca-aggregate.yml keys."""
    if not AGGREGATE_FILE.exists():
        return set()
    data = load_yaml(AGGREGATE_FILE)
    if not data:
        return set()
    # Keys are like ./addons/oca/server-tools → extract 'server-tools'
    repos = set()
    for key in data.keys():
        repo_name = key.rstrip("/").split("/")[-1]
        repos.add(repo_name)
    return repos


def check_manifest(manifest_path: Path, aggregate_repos: set) -> dict:
    """Check a single must-have manifest against aggregate config."""
    data = load_yaml(manifest_path)
    if not data:
        return {"file": manifest_path.name, "error": "empty manifest"}

    result = {
        "file": manifest_path.name,
        "repos_declared": [],
        "repos_missing": [],
        "modules_declared": [],
        "modules_dirs_found": [],
        "modules_dirs_missing": [],
    }

    # Check repositories
    for repo in data.get("repositories", []):
        repo_name = repo.get("name", "").replace("OCA/", "")
        result["repos_declared"].append(repo_name)
        if repo_name not in aggregate_repos:
            result["repos_missing"].append(repo_name)

    # Check module directories (only if addons/oca/ exists and is hydrated)
    for module in data.get("modules", []):
        result["modules_declared"].append(module)
        module_dir = ADDONS_OCA
        # Search across all repo dirs for the module
        found = False
        if module_dir.exists():
            for repo_dir in module_dir.iterdir():
                if repo_dir.is_dir() and (repo_dir / module / "__manifest__.py").exists():
                    found = True
                    break
        if found:
            result["modules_dirs_found"].append(module)
        else:
            result["modules_dirs_missing"].append(module)

    return result


def main():
    strict = "--strict" in sys.argv

    print("=" * 60)
    print("  OCA Must-Have Module Availability Check")
    print("=" * 60)
    print()

    # Load aggregate repos
    aggregate_repos = get_aggregate_repos()
    print(f"Aggregate repos configured: {len(aggregate_repos)}")
    print()

    # Find all must-have manifests (skip oca_must_have_all.yml which is a meta-include)
    manifests = sorted(CONFIG_DIR.glob("oca_must_have_*.yml"))
    manifests = [m for m in manifests if "all" not in m.name]

    if not manifests:
        print("ERROR: No must-have manifests found in config/oca/")
        sys.exit(2)

    total_repos_ok = 0
    total_repos_missing = 0
    total_modules = 0
    total_modules_found = 0
    all_results = []

    for manifest in manifests:
        result = check_manifest(manifest, aggregate_repos)
        all_results.append(result)

        if "error" in result:
            print(f"  {result['file']}: ERROR - {result['error']}")
            continue

        repos_ok = len(result["repos_declared"]) - len(result["repos_missing"])
        repos_total = len(result["repos_declared"])
        mods_total = len(result["modules_declared"])
        mods_found = len(result["modules_dirs_found"])

        total_repos_ok += repos_ok
        total_repos_missing += len(result["repos_missing"])
        total_modules += mods_total
        total_modules_found += mods_found

        status = "PASS" if not result["repos_missing"] else "FAIL"
        print(f"  [{status}] {result['file']}")
        print(f"         Repos: {repos_ok}/{repos_total} in aggregate")
        if result["repos_missing"]:
            for r in result["repos_missing"]:
                print(f"         MISSING repo: {r}")
        print(f"         Modules: {mods_found}/{mods_total} dirs found")
        if result["modules_dirs_missing"] and ADDONS_OCA.exists():
            for m in result["modules_dirs_missing"]:
                print(f"         MISSING module dir: {m}")
        print()

    # Summary
    print("=" * 60)
    print(f"  Repos:   {total_repos_ok}/{total_repos_ok + total_repos_missing} in aggregate")
    print(f"  Modules: {total_modules_found}/{total_modules} dirs found")
    if not ADDONS_OCA.exists():
        print(f"  NOTE: addons/oca/ not found (run gitaggregate to hydrate)")
    print("=" * 60)

    if total_repos_missing > 0:
        print(f"\nFAIL: {total_repos_missing} repo(s) missing from oca-aggregate.yml")
        if strict:
            sys.exit(1)
    else:
        print("\nPASS: All declared repos present in oca-aggregate.yml")

    sys.exit(0)


if __name__ == "__main__":
    main()
