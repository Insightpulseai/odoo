#!/usr/bin/env python3
"""
scan_oca_repos.py — OCA-19 Readiness Gate Scanner
===================================================
Scans addons/oca/<repo>/ for installability on Odoo 19:
  - Reports branch, module count, manifest version prefix
  - Flags empty repos (0 manifests)
  - Flags repos on non-19.0 branch
  - Flags manifest version mismatches
  - Emits machine-readable JSON artifact

Exit codes:
  0 — all repos clean (no empties, no blocked repos)
  1 — warnings only (blocked repos present but --warn-only passed)
  2 — fatal: empty repos or 18.x-pinned repos found in addons_path

Usage:
  python3 scripts/ci/scan_oca_repos.py [--oca-dir addons/oca] [--json out.json] [--warn-only]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

TARGET_BRANCH = "19.0"
EMPTY_REPOS_FATAL = True  # treat empty repos as hard failures


def get_git_branch(repo_path: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else "no-git"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "no-git"


def get_git_sha(repo_path: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "unknown"


def scan_modules(repo_path: Path) -> list[dict]:
    """Return list of {name, version, version_prefix} for each module in repo."""
    modules = []
    for manifest in sorted(repo_path.glob("*/__manifest__.py")):
        module_name = manifest.parent.name
        version = "unknown"
        version_prefix = "?"
        try:
            text = manifest.read_text(errors="replace")
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith('"version"') or stripped.startswith("'version'"):
                    # Extract version value
                    for delim in ('"', "'"):
                        parts = stripped.split(delim)
                        if len(parts) >= 4:
                            version = parts[3]
                            version_prefix = ".".join(version.split(".")[:2])
                            break
                    break
        except OSError:
            pass
        modules.append({"name": module_name, "version": version, "version_prefix": version_prefix})
    return modules


def classify_repo(
    name: str,
    branch: str,
    sha: str,
    modules: list[dict],
) -> dict:
    module_count = len(modules)
    issues = []

    # Empty repo
    if module_count == 0:
        issues.append("EMPTY: no modules found")

    # Branch check — _git_aggregated is acceptable (aggregated submodule)
    branch_ok = branch in (TARGET_BRANCH, "_git_aggregated")
    if not branch_ok:
        issues.append(f"BRANCH_MISMATCH: on {branch!r}, expected {TARGET_BRANCH!r} or _git_aggregated")

    # Manifest version check
    bad_versions = [
        m for m in modules
        if m["version_prefix"] not in (TARGET_BRANCH, "?", "unknown")
    ]
    if bad_versions:
        bad_names = [f"{m['name']}@{m['version']}" for m in bad_versions]
        issues.append(f"VERSION_MISMATCH: {', '.join(bad_names)}")

    if issues:
        status = "empty" if module_count == 0 else "blocked"
    elif branch == TARGET_BRANCH:
        status = "pinned-ok"   # explicitly on 19.0 branch
    else:
        status = "ok"          # _git_aggregated with 19.0.x manifests

    return {
        "repo": name,
        "branch": branch,
        "sha": sha,
        "module_count": module_count,
        "status": status,
        "issues": issues,
        "modules": modules,
    }


def print_table(results: list[dict]) -> None:
    header = f"{'REPO':<28} {'BRANCH':<20} {'SHA':<8} {'MODS':>4}  {'STATUS':<12}  ISSUES"
    print(header)
    print("-" * len(header))
    for r in results:
        issues_str = "; ".join(r["issues"]) if r["issues"] else ""
        status_icon = {
            "ok": "✅",
            "pinned-ok": "✅",
            "blocked": "❌",
            "empty": "🚫",
        }.get(r["status"], "⚠️")
        print(
            f"{r['repo']:<28} {r['branch']:<20} {r['sha']:<8} "
            f"{r['module_count']:>4}  {status_icon} {r['status']:<10}  {issues_str}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="OCA-19 Readiness Scanner")
    parser.add_argument("--oca-dir", default="addons/oca", help="Path to addons/oca/")
    parser.add_argument("--json", dest="json_out", default=None, help="Write JSON report to file")
    parser.add_argument("--warn-only", action="store_true", help="Exit 0 even on blocked repos")
    args = parser.parse_args()

    oca_root = Path(args.oca_dir)
    if not oca_root.is_dir():
        print(f"ERROR: OCA directory not found: {oca_root}", file=sys.stderr)
        return 2

    results = []
    for repo_dir in sorted(d for d in oca_root.iterdir() if d.is_dir()):
        branch = get_git_branch(repo_dir)
        sha = get_git_sha(repo_dir)
        modules = scan_modules(repo_dir)
        result = classify_repo(repo_dir.name, branch, sha, modules)
        results.append(result)

    # Summary counts
    total = len(results)
    empty_count = sum(1 for r in results if r["status"] == "empty")
    blocked_count = sum(1 for r in results if r["status"] == "blocked")
    ok_count = sum(1 for r in results if r["status"] in ("ok", "pinned-ok"))
    total_modules = sum(r["module_count"] for r in results)

    print(f"\n=== OCA-19 Readiness Report ===")
    print(f"Target: Odoo {TARGET_BRANCH}\n")
    print_table(results)
    print(f"\nSummary: {total} repos | {total_modules} modules | "
          f"✅ {ok_count} ok | ❌ {blocked_count} blocked | 🚫 {empty_count} empty\n")

    # Write JSON artifact
    report = {
        "target_version": TARGET_BRANCH,
        "total_repos": total,
        "total_modules": total_modules,
        "ok": ok_count,
        "blocked": blocked_count,
        "empty": empty_count,
        "repos": results,
    }

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2))
        print(f"JSON report written to: {out_path}")

    # Exit code
    if empty_count > 0:
        print(f"FATAL: {empty_count} empty repo(s) must be removed from addons_path.", file=sys.stderr)
        empty_names = [r["repo"] for r in results if r["status"] == "empty"]
        print(f"  Empty: {', '.join(empty_names)}", file=sys.stderr)
        return 2

    if blocked_count > 0:
        blocked_names = [r["repo"] for r in results if r["status"] == "blocked"]
        print(f"BLOCKED: {blocked_count} repo(s) not compatible with Odoo {TARGET_BRANCH}:", file=sys.stderr)
        for r in results:
            if r["status"] == "blocked":
                print(f"  {r['repo']}: {'; '.join(r['issues'])}", file=sys.stderr)
        if args.warn_only:
            print("(--warn-only: exiting 0)", file=sys.stderr)
            return 0
        return 1

    print(f"All {ok_count} repos are Odoo {TARGET_BRANCH} ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
