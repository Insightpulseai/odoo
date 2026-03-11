#!/usr/bin/env python3
"""
enforce_top_level_allowlist.py — Enforce canonical top-level directory structure.

Reads ssot/repo/top_level_allowlist.yaml and scans the repo root.
Fails (exit 1) if any top-level directory exists that is not in the allowlist.
Warns (exit 0) for Tier 2/3 dirs that should be rehomed but are currently grandfathered.

Usage:
    python3 scripts/repo/enforce_top_level_allowlist.py
    python3 scripts/repo/enforce_top_level_allowlist.py --strict   # fail on Tier 2/3 too
    python3 scripts/repo/enforce_top_level_allowlist.py --warn-only  # never exit 1
    python3 scripts/repo/enforce_top_level_allowlist.py --repo-root /path/to/repo

Exit codes:
    0 — All top-level dirs are allowlisted (or warn-only mode)
    1 — Unknown dir(s) found that are not in the allowlist
    2 — Runtime error (missing YAML, bad format, etc.)
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


def load_allowlist(yaml_path: Path) -> dict:
    """Load and parse the allowlist YAML. Returns structured data."""
    if not yaml_path.exists():
        print(f"ERROR: Allowlist not found: {yaml_path}", file=sys.stderr)
        sys.exit(2)
    with open(yaml_path) as f:
        return yaml.safe_load(f)


def build_allowed_sets(allowlist: dict) -> tuple[set[str], set[str], set[str], set[str]]:
    """
    Extract sets of dir names by category.
    Returns: (tier0, tier1, tier2_deprecated, tier3_deprecated)
    """
    tier0: set[str] = set()
    tier1: set[str] = set()
    tier2: set[str] = set()
    tier3: set[str] = set()
    hidden: set[str] = set()
    generated: set[str] = set()

    for entry in allowlist.get("tier0", {}).get("dirs", []):
        tier0.add(entry["name"])

    for entry in allowlist.get("tier1", {}).get("dirs", []):
        tier1.add(entry["name"])

    for entry in allowlist.get("tier2", {}).get("dirs", []):
        tier2.add(entry["name"])

    for entry in allowlist.get("tier3", {}).get("dirs", []):
        tier3.add(entry["name"])

    for name in allowlist.get("hidden", {}).get("dirs", []):
        hidden.add(name)

    for name in allowlist.get("generated", {}).get("dirs", []):
        generated.add(name)

    return tier0, tier1, tier2, tier3, hidden, generated


def get_migrate_map(allowlist: dict) -> dict[str, str]:
    """Build {dirname: migrate_to} map for Tier 2/3 dirs."""
    result: dict[str, str] = {}
    for tier in ("tier2", "tier3"):
        for entry in allowlist.get(tier, {}).get("dirs", []):
            if "migrate_to" in entry:
                result[entry["name"]] = entry["migrate_to"]
    return result


def scan_root(repo_root: Path, generated: set[str]) -> list[str]:
    """Return list of top-level entry names (dirs only, excluding known generated)."""
    entries = []
    for item in sorted(repo_root.iterdir()):
        if not item.is_dir():
            continue
        if item.name in generated:
            continue
        entries.append(item.name)
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enforce canonical top-level directory allowlist"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repo root path (default: two levels up from this script)",
    )
    parser.add_argument(
        "--allowlist",
        type=Path,
        default=None,
        help="Path to allowlist YAML (default: ssot/repo/top_level_allowlist.yaml)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on Tier 2/3 dirs too (not just unknown dirs)",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Never exit 1 — print warnings but always succeed",
    )
    args = parser.parse_args()

    # Resolve paths
    script_dir = Path(__file__).resolve().parent
    repo_root = args.repo_root or script_dir.parents[1]
    allowlist_path = args.allowlist or (repo_root / "ssot" / "repo" / "top_level_allowlist.yaml")

    print(f"Repo root: {repo_root}")
    print(f"Allowlist: {allowlist_path}")
    print()

    # Load allowlist
    allowlist = load_allowlist(allowlist_path)
    tier0, tier1, tier2, tier3, hidden, generated = build_allowed_sets(allowlist)
    migrate_map = get_migrate_map(allowlist)

    all_known = tier0 | tier1 | tier2 | tier3 | hidden | generated
    canonical = tier0 | tier1
    grandfathered = tier2 | tier3

    # Scan root
    actual_dirs = scan_root(repo_root, generated)

    # Classify
    violations: list[str] = []          # Not in allowlist at all → FAIL
    deprecation_warnings: list[str] = [] # In tier2/3 → WARN
    hidden_dirs: list[str] = []          # Dot-prefix → always ok
    ok_dirs: list[str] = []              # Tier 0/1 → clean

    for name in actual_dirs:
        if name.startswith("."):
            # Hidden dirs — check against hidden allowlist but always pass
            hidden_dirs.append(name)
        elif name in canonical:
            ok_dirs.append(name)
        elif name in grandfathered:
            deprecation_warnings.append(name)
        elif name in generated:
            pass  # filtered above
        else:
            violations.append(name)

    # Report
    print(f"{'─' * 60}")
    print(f"  {'CATEGORY':<20} {'COUNT':>5}")
    print(f"{'─' * 60}")
    print(f"  {'Tier 0/1 (canonical)':<20} {len(ok_dirs):>5}  ✅")
    print(f"  {'Hidden (dot-prefix)':<20} {len(hidden_dirs):>5}  ✅")
    print(f"  {'Tier 2/3 (legacy)':<20} {len(deprecation_warnings):>5}  ⚠️")
    print(f"  {'Unknown (violations)':<20} {len(violations):>5}  {'❌' if violations else '✅'}")
    print(f"{'─' * 60}")
    print()

    # Detail: deprecation warnings
    if deprecation_warnings:
        print("⚠️  Legacy/deprecated directories (grandfathered — consolidation needed):")
        for name in sorted(deprecation_warnings):
            suggestion = migrate_map.get(name, "archive/ (if unused)")
            tier = "Tier 2" if name in tier2 else "Tier 3"
            print(f"   {tier}  {name}/  →  migrate to: {suggestion}")
        print()

    # Detail: violations
    if violations:
        print("❌  Unknown directories NOT in allowlist:")
        for name in sorted(violations):
            print(f"   {name}/")
            print(f"     → Add to ssot/repo/top_level_allowlist.yaml (with tier + purpose + owner)")
            print(f"     → Or migrate to an existing canonical boundary:")
            print(f"       infra/, platform/, web/, agents/, apps/, docs/, spec/, scripts/, supabase/")
        print()

    # Strict mode: also fail on legacy dirs
    if args.strict and deprecation_warnings:
        print("❌  Strict mode: Tier 2/3 dirs are also violations in strict mode.")
        violations.extend(deprecation_warnings)

    # Final verdict
    if violations:
        if args.warn_only:
            print("⚠️  WARN-ONLY mode: violations found but exit 0 (--warn-only)")
            return 0
        print(
            f"❌ FAIL — {len(violations)} unknown top-level director"
            f"{'y' if len(violations) == 1 else 'ies'} found.\n"
            f"   Update ssot/repo/top_level_allowlist.yaml to register them,\n"
            f"   or migrate them to an existing canonical boundary."
        )
        return 1

    if deprecation_warnings and not args.strict:
        print(
            f"✅ PASS — No unknown directories.\n"
            f"   {len(deprecation_warnings)} legacy dir(s) are grandfathered but should be rehomed.\n"
            f"   Run with --strict to treat Tier 2/3 as failures."
        )
    else:
        print("✅ PASS — All top-level directories are allowlisted.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
