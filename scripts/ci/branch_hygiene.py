#!/usr/bin/env python3
"""
scripts/ci/branch_hygiene.py
---
Prune stale agent-generated branches with no open PR.

Policy source: ssot/policy/branch_hygiene.yaml
Report output: reports/ci/branch_hygiene_report.json

Environment variables (all required):
  GH_TOKEN        GitHub token with contents:write + pull-requests:read
  REPO            owner/repo  (e.g. Insightpulseai/odoo)
  DRY_RUN         "true"|"false"  — if true, log only, no deletions
  MAX_AGE_DAYS    integer — delete branches older than this with no open PR

Exit codes:
  0 — success (even if branches deleted)
  1 — fatal error (e.g. API auth failed, policy file missing)
"""

import datetime
import json
import os
import subprocess
import sys
import time

# ---------------------------------------------------------------------------
# Auto-delete candidate prefixes (hardened from ssot/policy/branch_hygiene.yaml)
# These are branches created by automated agents / bots
# ---------------------------------------------------------------------------
AUTO_DELETE_PREFIXES = [
    "claude/",
    "codex/",
    "bot/",
    "dependabot/",
    "renovate/",
]

# Never delete — regardless of age or open PRs
PROTECTED_EXACT = {"main", "master", "develop"}
PROTECTED_PREFIXES = [
    "release/",
    "hotfix/",
    "chore/",
    "feat/",
    "fix/",
    "docs/",
    "test/",
    "refactor/",
]


def gh_api(path: str, method: str = "GET", timeout: int = 20) -> dict | list:
    cmd = ["gh", "api"]
    if method != "GET":
        cmd += ["--method", method]
    cmd.append(path)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"gh api {path} failed: {result.stderr.strip()}")
    return json.loads(result.stdout or "null")


def fetch_all_branches(repo: str) -> list:
    branches = []
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
    results = gh_api(
        f"repos/{repo}/pulls?state=open&head={owner}:{branch}&per_page=1"
    )
    return isinstance(results, list) and len(results) > 0


def delete_branch(repo: str, branch: str) -> None:
    gh_api(f"repos/{repo}/git/refs/heads/{branch}", method="DELETE")


def main() -> int:
    repo = os.environ.get("REPO", "")
    dry_run_str = os.environ.get("DRY_RUN", "true").lower()
    dry_run = dry_run_str not in ("false", "0", "no")
    max_age_days = int(os.environ.get("MAX_AGE_DAYS", "14"))

    if not repo:
        print("ERROR: REPO env var not set", file=sys.stderr)
        return 1

    now = int(time.time())
    cutoff_ts = now - max_age_days * 86400

    print(f"Branch Hygiene — {repo}")
    print(f"  Mode: {'DRY RUN (no deletions)' if dry_run else 'LIVE (deletions active)'}")
    print(f"  Max age: {max_age_days} days")
    print()

    report: dict = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repo": repo,
        "dry_run": dry_run,
        "max_age_days": max_age_days,
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
        return 1

    print(f"Total branches: {len(branches)}")
    print()

    for branch in branches:
        name = branch["name"]
        sha = branch["commit"]["sha"]

        # Skip protected exact names
        if name in PROTECTED_EXACT:
            report["skipped_other"].append({"name": name, "reason": "protected_exact"})
            continue

        # Skip protected prefixes
        if any(name.startswith(p) for p in PROTECTED_PREFIXES):
            report["skipped_other"].append({"name": name, "reason": "protected_prefix"})
            continue

        # Only process auto-delete candidate prefixes
        if not any(name.startswith(p) for p in AUTO_DELETE_PREFIXES):
            continue

        # Get commit age
        try:
            commit_ts = get_commit_timestamp(repo, sha)
        except Exception as e:
            print(f"  ERROR  {name}: failed to get commit date — {e}")
            report["errors"].append({"name": name, "error": str(e)})
            continue

        age_days = (now - commit_ts) // 86400

        if commit_ts >= cutoff_ts:
            print(f"  NEW    {name} (age={age_days}d) — too new, skip")
            report["skipped_too_new"].append({"name": name, "age_days": age_days})
            continue

        # Check for open PRs
        try:
            open_pr = has_open_pr(repo, name)
        except Exception as e:
            print(f"  ERROR  {name}: PR check failed — {e}")
            report["errors"].append({"name": name, "error": f"PR check: {e}"})
            continue

        if open_pr:
            print(f"  SKIP   {name} (age={age_days}d) — has open PR")
            report["skipped_open_pr"].append({"name": name, "age_days": age_days})
            continue

        # Delete (or flag in dry-run)
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
                print(f"  ERROR  {name}: delete failed — {e}")
                report["errors"].append({"name": name, "error": str(e)})

    # Write report
    report_path = "reports/ci/branch_hygiene_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print()
    print("=== Summary ===")
    label = "Would delete" if dry_run else "Deleted"
    print(f"  {label}: {len(report['deleted'])}")
    print(f"  Skipped (open PR): {len(report['skipped_open_pr'])}")
    print(f"  Skipped (too new): {len(report['skipped_too_new'])}")
    print(f"  Errors: {len(report['errors'])}")
    print(f"  Report: {report_path}")

    if report["errors"]:
        print("\nErrors:")
        for e in report["errors"]:
            print(f"  - {e['name']}: {e['error']}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
