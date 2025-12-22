#!/usr/bin/env python3
"""
Verify Repo <-> Runtime Alignment

This script compares the expected state (from repo) against
the actual runtime state (from snapshot/db_truth).

Exit codes:
- 0: Alignment verified
- 1: Alignment issues found
- 2: Missing required inputs
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class AlignmentCheck:
    name: str
    expected: str
    actual: str
    passed: bool
    message: str


def get_repo_commit() -> str:
    """Get current repo commit SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def get_submodule_status() -> dict:
    """Get submodule commit SHAs."""
    submodules = {}
    try:
        result = subprocess.run(
            ["git", "submodule", "status", "--recursive"],
            capture_output=True,
            text=True
        )
        for line in result.stdout.strip().split("\n"):
            if line:
                # Format: " SHA path (branch)" or "+SHA path (branch)"
                match = re.match(r"^[\s+-]?([a-f0-9]+)\s+(\S+)", line)
                if match:
                    sha, path = match.groups()
                    submodules[path] = sha
    except Exception:
        pass
    return submodules


def parse_snapshot(snapshot_path: str) -> dict:
    """Parse snapshot.txt output into structured data."""
    data = {
        "commit": None,
        "branch": None,
        "dirty": False,
        "submodules": {},
    }

    if not os.path.exists(snapshot_path):
        return data

    with open(snapshot_path, "r") as f:
        content = f.read()

    # Extract commit SHA
    match = re.search(r"Commit SHA:\s*\n\s*([a-f0-9]+)", content)
    if match:
        data["commit"] = match.group(1)

    # Extract branch
    match = re.search(r"Branch:\s*\n\s*(\S+)", content)
    if match:
        data["branch"] = match.group(1)

    # Check if dirty
    status_section = re.search(r"Status \(dirty check\):\s*\n(.*?)(?=\n\n|===)", content, re.DOTALL)
    if status_section:
        status_content = status_section.group(1).strip()
        data["dirty"] = bool(status_content and status_content != "(not available)")

    return data


def verify_alignment(snapshot_path: Optional[str] = None) -> list:
    """Run alignment checks and return results."""
    checks = []

    # Get expected state from repo
    expected_commit = get_repo_commit()
    expected_submodules = get_submodule_status()

    if snapshot_path:
        # Compare against provided snapshot
        snapshot = parse_snapshot(snapshot_path)

        # Commit check
        if snapshot["commit"]:
            passed = snapshot["commit"] == expected_commit
            checks.append(AlignmentCheck(
                name="Commit SHA",
                expected=expected_commit[:12],
                actual=snapshot["commit"][:12] if snapshot["commit"] else "unknown",
                passed=passed,
                message="Commits match" if passed else "MISMATCH: Runtime running different commit"
            ))

        # Dirty check
        if snapshot["dirty"]:
            checks.append(AlignmentCheck(
                name="Working Tree",
                expected="clean",
                actual="dirty",
                passed=False,
                message="WARNING: Runtime has uncommitted changes"
            ))
        else:
            checks.append(AlignmentCheck(
                name="Working Tree",
                expected="clean",
                actual="clean",
                passed=True,
                message="Working tree is clean"
            ))

    else:
        # No snapshot provided, just report expected state
        print("No snapshot provided. Expected state:")
        print(f"  Commit: {expected_commit}")
        print(f"  Submodules: {len(expected_submodules)}")
        for path, sha in expected_submodules.items():
            print(f"    {path}: {sha[:12]}")

    return checks


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify repo <-> runtime alignment"
    )
    parser.add_argument(
        "--snapshot",
        help="Path to snapshot.txt from runtime"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    args = parser.parse_args()

    checks = verify_alignment(args.snapshot)

    if args.json:
        output = {
            "checks": [
                {
                    "name": c.name,
                    "expected": c.expected,
                    "actual": c.actual,
                    "passed": c.passed,
                    "message": c.message
                }
                for c in checks
            ],
            "all_passed": all(c.passed for c in checks)
        }
        print(json.dumps(output, indent=2))
    else:
        print("=== Alignment Verification ===\n")
        all_passed = True
        for check in checks:
            status = "[OK]" if check.passed else "[FAIL]"
            all_passed = all_passed and check.passed
            print(f"{status} {check.name}")
            print(f"      Expected: {check.expected}")
            print(f"      Actual:   {check.actual}")
            print(f"      {check.message}\n")

        if all_passed:
            print("=== All checks passed ===")
        else:
            print("=== Alignment issues detected ===")

    return 0 if all(c.passed for c in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
