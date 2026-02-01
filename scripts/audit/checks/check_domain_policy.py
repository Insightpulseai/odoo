#!/usr/bin/env python3
"""
Domain Policy Audit Check

Hard policy: No insightpulseai.net references allowed anywhere in the repo.
All domains must use insightpulseai.com.

This check FAILS the audit if any .net references are found.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import CheckResult, IntegrationResult, redact_dict


# Directories to skip
SKIP_DIRS = {
    '.git',
    'node_modules',
    '.venv',
    'venv',
    'dist',
    'build',
    '.next',
    '__pycache__',
    '.pytest_cache',
    'coverage'
}

# File extensions to check
CHECK_EXTENSIONS = {
    '.py', '.sh', '.yaml', '.yml', '.json', '.md', '.txt',
    '.conf', '.toml', '.ini', '.env', '.example', '.template',
    '.ts', '.tsx', '.js', '.jsx', '.html', '.css', '.scss'
}


def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else "policy_audit.json"

    result = IntegrationResult(
        name="Domain Policy",
        status="SKIP",
        risk_tier="critical",
        checks=[],
        recommendations=[]
    )

    checks = []

    # Check 1: No .net references in codebase
    check = run_forbidden_domain_check()
    checks.append(check)

    # Check 2: Verify canonical domains are used
    check = run_canonical_domain_check()
    checks.append(check)

    # Calculate result
    result.checks = checks
    result.pass_count = sum(1 for c in checks if c.status == "PASS")
    result.error_count = sum(1 for c in checks if c.status == "FAIL")

    if result.error_count == 0:
        result.status = "PASS"
        result.access_level = "ok"
    else:
        result.status = "FAIL"
        result.access_level = "insufficient"
        result.recommendations.append("Run: sed -i 's/insightpulseai\\.net/insightpulseai.com/g' <files>")

    save_result(result, output_file)


def run_forbidden_domain_check() -> CheckResult:
    """Check that no insightpulseai.net references exist."""
    check = CheckResult(
        name="forbidden_domain",
        integration="policy",
        description="No insightpulseai.net references allowed",
        status="FAIL"
    )

    # Try using ripgrep first (faster)
    matches = []
    try:
        result = subprocess.run(
            ["rg", "-n", "--hidden", "--no-ignore-vcs",
             "-g", "!.git", "-g", "!node_modules", "-g", "!.venv",
             "insightpulseai\\.net", "."],
            capture_output=True, text=True, timeout=60, cwd=get_repo_root()
        )
        if result.stdout.strip():
            matches = result.stdout.strip().split('\n')[:50]  # Limit to 50 matches
    except FileNotFoundError:
        # Fallback to grep
        try:
            result = subprocess.run(
                ["grep", "-rn", "--include=*.py", "--include=*.sh",
                 "--include=*.yaml", "--include=*.yml", "--include=*.json",
                 "--include=*.md", "--include=*.conf", "--include=*.txt",
                 "insightpulseai\\.net", "."],
                capture_output=True, text=True, timeout=120, cwd=get_repo_root()
            )
            if result.stdout.strip():
                matches = result.stdout.strip().split('\n')[:50]
        except Exception as e:
            check.error = f"Could not run grep: {e}"
            return check
    except subprocess.TimeoutExpired:
        check.error = "Search timed out"
        return check
    except Exception as e:
        check.error = f"Search failed: {e}"
        return check

    if matches:
        check.status = "FAIL"
        check.error = f"Found {len(matches)} forbidden .net references"
        check.evidence = {
            "match_count": len(matches),
            "matches": matches[:20],  # Only show first 20
            "truncated": len(matches) > 20
        }
        check.recommendations = [
            "Replace all .net with .com:",
            "find . -type f -name '*.py' -o -name '*.yaml' | xargs sed -i 's/insightpulseai\\.net/insightpulseai.com/g'"
        ]
    else:
        check.status = "PASS"
        check.evidence = {"match_count": 0, "policy": "no insightpulseai.net"}

    return check


def run_canonical_domain_check() -> CheckResult:
    """Verify canonical .com domains are properly used."""
    check = CheckResult(
        name="canonical_domains",
        integration="policy",
        description="Verify canonical .com domains are used",
        status="FAIL"
    )

    canonical_domains = [
        "erp.insightpulseai.com",
        "n8n.insightpulseai.com",
        "superset.insightpulseai.com",
        "mg.insightpulseai.com"
    ]

    found_domains = []
    try:
        for domain in canonical_domains:
            result = subprocess.run(
                ["grep", "-rn", "--include=*.py", "--include=*.yaml",
                 "--include=*.yml", "--include=*.json", "--include=*.conf",
                 domain, "."],
                capture_output=True, text=True, timeout=30, cwd=get_repo_root()
            )
            if result.stdout.strip():
                found_domains.append(domain)
    except Exception:
        pass

    check.status = "PASS"
    check.evidence = {
        "canonical_domains": canonical_domains,
        "found_in_repo": found_domains
    }

    return check


def get_repo_root() -> str:
    """Get the repository root directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() or "."
    except Exception:
        return "."


def save_result(result, output_file):
    """Save result to file."""
    data = result.to_dict()
    data = redact_dict(data)

    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2, default=str)

    print(f"Domain Policy audit: {result.status} ({result.pass_count} passed, {result.error_count} failed)")


if __name__ == "__main__":
    main()
