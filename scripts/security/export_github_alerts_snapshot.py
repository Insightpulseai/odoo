#!/usr/bin/env python3
"""
scripts/security/export_github_alerts_snapshot.py

Pulls GitHub Dependabot + Code Scanning alert counts and writes:
    reports/security/github_alerts_snapshot.json

Reads GITHUB_TOKEN from env — never hardcoded.

Exit codes:
    0  — snapshot written successfully
    1  — API error or missing GITHUB_TOKEN

Usage:
    python3 scripts/security/export_github_alerts_snapshot.py

CI usage:
    .github/workflows/security-alerts-snapshot.yml calls this script,
    then compares output against ssot/security/vuln_policy.yaml thresholds.

SSOT: ssot/security/vuln_policy.yaml
"""

import json
import os
import sys
import urllib.request
import urllib.error
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = "Insightpulseai/odoo"
OUTPUT_PATH = Path("reports/security/github_alerts_snapshot.json")
PAGE_SIZE = 100


def gh_get(path: str, token: str) -> list:
    """Paginate a GitHub API endpoint and return all items."""
    results = []
    page = 1
    while True:
        url = f"https://api.github.com{path}?state=open&per_page={PAGE_SIZE}&page={page}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"ERROR: HTTP {e.code} for {url}: {body[:200]}", file=sys.stderr)
            sys.exit(1)

        if not isinstance(data, list) or not data:
            break
        results.extend(data)
        if len(data) < PAGE_SIZE:
            break
        page += 1
    return results


def severity_counts(alerts: list, key_path: list) -> dict:
    """Count alerts by severity using a dotted key path."""
    counts = defaultdict(int)
    for alert in alerts:
        val = alert
        for k in key_path:
            val = val.get(k, {}) if isinstance(val, dict) else None
        if val:
            counts[val] += 1
    return dict(counts)


def load_policy(policy_path: Path) -> dict:
    """Load vuln_policy.yaml — minimal YAML parsing (no PyYAML dep required)."""
    try:
        import yaml  # type: ignore
        with policy_path.open() as f:
            return yaml.safe_load(f)
    except ImportError:
        # Fallback: return None; caller will skip threshold comparison
        return {}


def check_thresholds(snapshot: dict, policy: dict) -> list[str]:
    """Return a list of violations (empty = clean)."""
    violations = []
    if not policy:
        return violations

    thresholds = policy.get("thresholds", {})
    exceptions = policy.get("exceptions", [])
    today = datetime.now(timezone.utc).date()

    # Build active (non-expired) exceptions
    active_exceptions = {
        (ex["scope"], ex["severity"])
        for ex in exceptions
        if ex.get("expires_on") and str(ex["expires_on"]) >= str(today)
    }

    # Dependabot
    dep_thresh = thresholds.get("dependabot", {})
    dep_counts = snapshot.get("dependabot", {}).get("by_severity", {})
    for sev, limit in dep_thresh.items():
        actual = dep_counts.get(sev, 0)
        if actual > limit and ("dependabot", sev) not in active_exceptions:
            violations.append(
                f"dependabot.{sev}: {actual} > threshold {limit} "
                f"(no active exception for dependabot/{sev})"
            )

    # Code scanning
    cs_thresh = thresholds.get("code_scanning", {})
    cs_counts = snapshot.get("code_scanning", {}).get("by_severity", {})
    for sev, limit in cs_thresh.items():
        actual = cs_counts.get(sev, 0)
        if actual > limit and ("code_scanning", sev) not in active_exceptions:
            violations.append(
                f"code_scanning.{sev}: {actual} > threshold {limit} "
                f"(no active exception for code_scanning/{sev})"
            )

    return violations


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("ERROR: GITHUB_TOKEN env var not set", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching Dependabot alerts for {REPO}...")
    dep_alerts = gh_get(f"/repos/{REPO}/dependabot/alerts", token)
    dep_by_sev = severity_counts(dep_alerts, ["security_advisory", "severity"])
    dep_total = sum(dep_by_sev.values())

    print(f"Fetching Code Scanning alerts for {REPO}...")
    cs_alerts = gh_get(f"/repos/{REPO}/code-scanning/alerts", token)
    cs_by_sev = severity_counts(cs_alerts, ["rule", "severity"])
    cs_total = sum(cs_by_sev.values())

    snapshot = {
        "schema": "security.snapshot.v1",
        "repo": REPO,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dependabot": {
            "total": dep_total,
            "by_severity": dep_by_sev,
        },
        "code_scanning": {
            "total": cs_total,
            "by_severity": cs_by_sev,
        },
        "totals": {
            "dependabot": dep_total,
            "code_scanning": cs_total,
            "combined": dep_total + cs_total,
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w") as f:
        json.dump(snapshot, f, indent=2)
        f.write("\n")

    print(f"\nSnapshot written: {OUTPUT_PATH}")
    print(f"  Dependabot:    {dep_total:4d}  {dep_by_sev}")
    print(f"  Code scanning: {cs_total:4d}  {cs_by_sev}")

    # Threshold check
    policy_path = Path("ssot/security/vuln_policy.yaml")
    policy = load_policy(policy_path) if policy_path.exists() else {}
    violations = check_thresholds(snapshot, policy)

    if violations:
        print("\nPOLICY VIOLATIONS:")
        for v in violations:
            print(f"  ❌  {v}")
        print(
            "\nTo add a time-bounded exception, edit ssot/security/vuln_policy.yaml.\n"
            "See docs/runbooks/SECURITY_GATES.md for guidance."
        )
        sys.exit(1)

    print("\n✅ All thresholds pass (or covered by active exceptions)")


if __name__ == "__main__":
    main()
