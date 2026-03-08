#!/usr/bin/env python3
"""Validate OCA aggregate YAML against lock JSON.

Compares repo lists in oca-aggregate.yml and vendor/oca.lock.ce19.json,
reports discrepancies, and optionally fixes them.

Usage:
    python3 scripts/oca/validate_aggregate.py              # strict mode (exit 1 on diff)
    python3 scripts/oca/validate_aggregate.py --warn-only  # report only (exit 0)
    python3 scripts/oca/validate_aggregate.py --fix        # add missing entries (additive)
    python3 scripts/oca/validate_aggregate.py --json       # output JSON report to stdout
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


def find_repo_root() -> Path:
    """Walk up from script location to find the repo root containing oca-aggregate.yml."""
    candidate = Path(__file__).resolve().parent
    for _ in range(10):
        if (candidate / "oca-aggregate.yml").exists():
            return candidate
        candidate = candidate.parent
    # Fallback: current working directory
    cwd = Path.cwd()
    if (cwd / "oca-aggregate.yml").exists():
        return cwd
    raise FileNotFoundError(
        "Cannot locate oca-aggregate.yml. Run from repo root or ensure the file exists."
    )


def parse_aggregate_repos(aggregate_path: Path) -> set[str]:
    """Extract repo names from oca-aggregate.yml without requiring PyYAML.

    Parses lines matching the pattern: ./addons/oca/<repo-name>:
    This is robust against YAML structure and does not need a YAML library.
    """
    repos = set()
    pattern = re.compile(r"^\./addons/oca/([a-zA-Z0-9_-]+):\s*$")
    with open(aggregate_path) as f:
        for line in f:
            match = pattern.match(line)
            if match:
                repos.add(match.group(1))
    return repos


def parse_lock_repos(lock_path: Path) -> set[str]:
    """Extract repo names from vendor/oca.lock.ce19.json.

    Reads repos[].name fields like 'OCA/server-tools' and extracts 'server-tools'.
    """
    repos = set()
    with open(lock_path) as f:
        data = json.load(f)
    for repo in data.get("repos", []):
        name = repo.get("name", "")
        if "/" in name:
            repos.add(name.split("/", 1)[1])
        else:
            repos.add(name)
    return repos


def build_report(
    aggregate_repos: set[str], lock_repos: set[str]
) -> dict:
    """Build a comparison report between aggregate and lock repos."""
    in_both = sorted(aggregate_repos & lock_repos)
    aggregate_only = sorted(aggregate_repos - lock_repos)
    lock_only = sorted(lock_repos - aggregate_repos)
    in_sync = len(aggregate_only) == 0 and len(lock_only) == 0

    return {
        "in_sync": in_sync,
        "aggregate_count": len(aggregate_repos),
        "lock_count": len(lock_repos),
        "in_both_count": len(in_both),
        "in_both": in_both,
        "aggregate_only_count": len(aggregate_only),
        "aggregate_only": aggregate_only,
        "lock_only_count": len(lock_only),
        "lock_only": lock_only,
    }


def fix_lock(lock_path: Path, missing_repos: list[str]) -> int:
    """Add missing repos to the lock JSON (additive only). Returns count added."""
    if not missing_repos:
        return 0

    with open(lock_path) as f:
        data = json.load(f)

    existing_names = {r["name"] for r in data.get("repos", [])}
    added = 0

    for repo_name in sorted(missing_repos):
        full_name = f"OCA/{repo_name}"
        if full_name in existing_names:
            continue
        data["repos"].append(
            {
                "name": full_name,
                "url": f"https://github.com/OCA/{repo_name}.git",
                "ref": "19.0",
                "commit": "HEAD",
                "modules": [],
                "ee_parity": [],
            }
        )
        added += 1

    with open(lock_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return added


def fix_aggregate(aggregate_path: Path, missing_repos: list[str]) -> int:
    """Add missing repos to the aggregate YAML (additive only). Returns count added."""
    if not missing_repos:
        return 0

    with open(aggregate_path) as f:
        content = f.read()

    added = 0
    for repo_name in sorted(missing_repos):
        entry_marker = f"./addons/oca/{repo_name}:"
        if entry_marker in content:
            continue
        block = (
            f"\n./addons/oca/{repo_name}:\n"
            f"  remotes:\n"
            f"    oca: https://github.com/OCA/{repo_name}.git\n"
            f"  merges:\n"
            f"    - oca 19.0\n"
        )
        content = content.rstrip() + "\n" + block
        added += 1

    with open(aggregate_path, "w") as f:
        f.write(content)

    return added


def print_report_text(report: dict) -> None:
    """Print human-readable report to stderr."""
    print("=" * 60, file=sys.stderr)
    print("OCA Aggregate vs Lock Validation Report", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(
        f"Aggregate repos: {report['aggregate_count']}  |  "
        f"Lock repos: {report['lock_count']}  |  "
        f"In both: {report['in_both_count']}",
        file=sys.stderr,
    )
    print(file=sys.stderr)

    if report["aggregate_only"]:
        print(
            f"In aggregate only ({report['aggregate_only_count']}):",
            file=sys.stderr,
        )
        for r in report["aggregate_only"]:
            print(f"  + {r}", file=sys.stderr)
        print(file=sys.stderr)

    if report["lock_only"]:
        print(
            f"In lock only ({report['lock_only_count']}):", file=sys.stderr
        )
        for r in report["lock_only"]:
            print(f"  + {r}", file=sys.stderr)
        print(file=sys.stderr)

    if report["in_sync"]:
        print("RESULT: IN SYNC", file=sys.stderr)
    else:
        print("RESULT: DISCREPANCIES FOUND", file=sys.stderr)
    print("=" * 60, file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate OCA aggregate YAML against lock JSON."
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Report discrepancies but exit 0 regardless.",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Add missing entries to both files (additive only).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output JSON report to stdout.",
    )
    parser.add_argument(
        "--aggregate",
        type=str,
        default=None,
        help="Path to oca-aggregate.yml (auto-detected if omitted).",
    )
    parser.add_argument(
        "--lock",
        type=str,
        default=None,
        help="Path to vendor/oca.lock.ce19.json (auto-detected if omitted).",
    )
    args = parser.parse_args()

    try:
        root = find_repo_root()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    aggregate_path = Path(args.aggregate) if args.aggregate else root / "oca-aggregate.yml"
    lock_path = Path(args.lock) if args.lock else root / "vendor" / "oca.lock.ce19.json"

    if not aggregate_path.exists():
        print(f"ERROR: {aggregate_path} not found.", file=sys.stderr)
        return 1
    if not lock_path.exists():
        print(f"ERROR: {lock_path} not found.", file=sys.stderr)
        return 1

    aggregate_repos = parse_aggregate_repos(aggregate_path)
    lock_repos = parse_lock_repos(lock_path)
    report = build_report(aggregate_repos, lock_repos)

    if args.fix:
        lock_added = fix_lock(lock_path, report["aggregate_only"])
        agg_added = fix_aggregate(aggregate_path, report["lock_only"])
        print(
            f"Fixed: added {lock_added} repos to lock, {agg_added} repos to aggregate.",
            file=sys.stderr,
        )
        # Re-parse after fix
        aggregate_repos = parse_aggregate_repos(aggregate_path)
        lock_repos = parse_lock_repos(lock_path)
        report = build_report(aggregate_repos, lock_repos)

    print_report_text(report)

    if args.output_json:
        json.dump(report, sys.stdout, indent=2)
        print()

    if report["in_sync"] or args.warn_only:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
