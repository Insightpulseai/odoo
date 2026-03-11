#!/usr/bin/env python3
"""
scripts/ci/branch_hygiene.py
---
Prune stale agent-generated branches with no open PR.

Safety model (two locks):
  Lock 1 — Workflow: scheduled runs always pass --dry-run=true regardless of inputs.
  Lock 2 — Script:   --dry-run=false requires --confirm=YES or BRANCH_HYGIENE_CONFIRM=YES
                     env var. Any other value raises SystemExit(4).

Policy source: ssot/policy/branch_hygiene.yaml
Report output: reports/ci/branch_hygiene_report.json  (always written, even on dry-run)

CLI arguments:
  --dry-run     "true"|"false"  (default: "true")
  --confirm     confirm token; must equal "YES" when --dry-run=false
  --max-age-days  integer days (default: 14)

Environment variables (also accepted; CLI args take precedence):
  GH_TOKEN        GitHub token with contents:write + pull-requests:read
  REPO            owner/repo  (e.g. Insightpulseai/odoo)
  DRY_RUN         "true"|"false"
  CONFIRM         confirm token
  MAX_AGE_DAYS    integer

Exit codes:
  0 — success (including clean dry-run)
  2 — misconfiguration (missing REPO, bad arguments)
  3 — API failure (could not list branches)
  4 — refused unsafe delete (--dry-run=false without --confirm YES)
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import time

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CONFIRM_TOKEN = "YES"
REPORT_PATH = "reports/ci/branch_hygiene_report.json"

# Auto-delete candidate prefixes — ONLY these are subject to pruning
AUTO_DELETE_PREFIXES: list[str] = [
    "claude/",
    "codex/",
    "bot/",
    "dependabot/",
    "renovate/",
]

# Exact branch names that are NEVER deleted
PROTECTED_EXACT: set[str] = {"main", "master", "develop", "gh-pages"}

# Prefix anchors that are NEVER deleted
PROTECTED_PREFIXES: list[str] = [
    "release/",
    "hotfix/",
    "prod/",
    "staging/",
    "chore/",
    "feat/",
    "fix/",
    "docs/",
    "test/",
    "refactor/",
]


# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------
def gh_api(path: str, method: str = "GET", timeout: int = 20):
    cmd = ["gh", "api"]
    if method != "GET":
        cmd += ["--method", method]
    cmd.append(path)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"gh api {path} → {result.returncode}: {result.stderr.strip()}")
    return json.loads(result.stdout or "null")


def fetch_all_branches(repo: str) -> list:
    branches: list = []
    page = 1
    while True:
        chunk = gh_api(f"repos/{repo}/branches?per_page=100&page={page}")
        if not chunk:
            break
        branches.extend(chunk)
        page += 1
    return branches


def get_commit_timestamp(repo: str, sha: str) -> int:
    data = gh_api(f"repos/{repo}/commits/{sha}")
    date_str = data["commit"]["committer"]["date"].rstrip("Z")
    dt = datetime.datetime.fromisoformat(date_str)
    return int(dt.timestamp())


def has_open_pr(repo: str, branch: str) -> bool:
    owner = repo.split("/")[0]
    results = gh_api(f"repos/{repo}/pulls?state=open&head={owner}:{branch}&per_page=1")
    return isinstance(results, list) and len(results) > 0


def delete_branch(repo: str, branch: str) -> None:
    gh_api(f"repos/{repo}/git/refs/heads/{branch}", method="DELETE")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Branch hygiene — prune stale agent-generated branches"
    )
    ap.add_argument(
        "--dry-run",
        default=os.environ.get("DRY_RUN", "true"),
        help='true|false (default: true). Scheduled CI always forces true.',
    )
    ap.add_argument(
        "--confirm",
        default=os.environ.get("CONFIRM", ""),
        help=f'Must equal "{CONFIRM_TOKEN}" when --dry-run=false (safety double-lock).',
    )
    ap.add_argument(
        "--max-age-days",
        type=int,
        default=int(os.environ.get("MAX_AGE_DAYS", "14")),
        help="Delete branches older than N days with no open PR (default: 14).",
    )
    return ap.parse_args()


def main() -> int:
    args = parse_args()

    # Normalise dry_run to bool
    dry_run = str(args.dry_run).lower() not in ("false", "0", "no")

    # Safety double-lock: refuse live deletions without explicit confirm token
    if not dry_run:
        if args.confirm != CONFIRM_TOKEN:
            print(
                f"REFUSING_DELETE: --dry-run=false requires --confirm={CONFIRM_TOKEN}.\n"
                "Pass --confirm=YES explicitly (workflow_dispatch only).\n"
                "Scheduled runs are always dry-run.",
                file=sys.stderr,
            )
            return 4

    repo = os.environ.get("REPO", "")
    if not repo:
        print("ERROR: REPO env var not set", file=sys.stderr)
        return 2

    now = int(time.time())
    cutoff_ts = now - args.max_age_days * 86400

    print(f"Branch Hygiene — {repo}")
    print(f"  Mode      : {'DRY RUN (report only)' if dry_run else 'LIVE (will delete; confirmed with token)'}")
    print(f"  Max age   : {args.max_age_days} days")
    print(f"  Cutoff    : {datetime.datetime.utcfromtimestamp(cutoff_ts).isoformat()}Z")
    print()

    report: dict = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repo": repo,
        "dry_run": dry_run,
        "max_age_days": args.max_age_days,
        "deleted": [],
        "skipped_open_pr": [],
        "skipped_other": [],
        "skipped_too_new": [],
        "errors": [],
    }

    try:
        branches = fetch_all_branches(repo)
    except RuntimeError as e:
        print(f"FATAL: failed to list branches: {e}", file=sys.stderr)
        _write_report(report)
        return 3

    print(f"Total branches: {len(branches)}")
    print()

    for branch in branches:
        name: str = branch["name"]
        sha: str = branch["commit"]["sha"]

        # Lock — never touch protected exact names or special branches
        if name in PROTECTED_EXACT:
            report["skipped_other"].append({"name": name, "reason": "protected_exact"})
            continue

        # Lock — never touch protected prefix anchors
        if any(name.startswith(p) for p in PROTECTED_PREFIXES):
            report["skipped_other"].append({"name": name, "reason": "protected_prefix"})
            continue

        # Only candidates matching auto-delete prefixes are processed further
        if not any(name.startswith(p) for p in AUTO_DELETE_PREFIXES):
            continue

        # Get commit age
        try:
            commit_ts = get_commit_timestamp(repo, sha)
        except Exception as e:
            msg = f"failed to get commit date: {e}"
            print(f"  ERROR  {name}: {msg}")
            report["errors"].append({"name": name, "error": msg})
            continue

        age_days = (now - commit_ts) // 86400

        if commit_ts >= cutoff_ts:
            print(f"  NEW    {name} (age={age_days}d) — too new, skip")
            report["skipped_too_new"].append({"name": name, "age_days": age_days})
            continue

        # Open-PR guard — NEVER delete a branch that has an open PR
        try:
            open_pr = has_open_pr(repo, name)
        except Exception as e:
            msg = f"PR check failed: {e}"
            print(f"  ERROR  {name}: {msg}")
            report["errors"].append({"name": name, "error": msg})
            continue

        if open_pr:
            print(f"  SKIP   {name} (age={age_days}d) — has open PR")
            report["skipped_open_pr"].append({"name": name, "age_days": age_days})
            continue

        entry = {"name": name, "age_days": age_days, "sha": sha}

        if dry_run:
            print(f"  DRY    {name} (age={age_days}d) — would delete")
            entry["dry_run"] = True
            report["deleted"].append(entry)
        else:
            try:
                delete_branch(repo, name)
                print(f"  DELETED {name} (age={age_days}d)")
                report["deleted"].append(entry)
            except Exception as e:
                msg = f"delete failed: {e}"
                print(f"  ERROR  {name}: {msg}")
                report["errors"].append({"name": name, "error": msg})

    _write_report(report)

    label = "Would delete" if dry_run else "Deleted"
    print()
    print("=== Summary ===")
    print(f"  {label}: {len(report['deleted'])}")
    print(f"  Skipped (open PR): {len(report['skipped_open_pr'])}")
    print(f"  Skipped (protected): {len(report['skipped_other'])}")
    print(f"  Skipped (too new): {len(report['skipped_too_new'])}")
    print(f"  Errors: {len(report['errors'])}")
    print(f"  Report: {REPORT_PATH}")

    if report["errors"]:
        print("\nErrors:")
        for e in report["errors"]:
            print(f"  - {e['name']}: {e['error']}")
        return 3

    return 0


def _write_report(report: dict) -> None:
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    sys.exit(main())
