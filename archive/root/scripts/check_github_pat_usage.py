#!/usr/bin/env python3
"""GitHub PAT usage scanner — enforces zero-PAT auth surface policy.

Scans workflows, scripts, SSOT files, and Edge Functions for references
to deprecated Personal Access Tokens. Fails if any non-allowlisted PAT
reference is found.

SSOT:   ssot/auth/github_auth_surface.yaml
Guard:  .github/workflows/github-auth-surface-contract.yml
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent

SCAN_PATHS = [
    ".github/workflows/**/*.yml",
    "scripts/**/*.py",
    "scripts/**/*.sh",
    "ssot/**/*.yaml",
    "ssot/**/*.yml",
    "supabase/functions/**/*.ts",
    "supabase/functions/**/*.js",
]

# Patterns that signal PAT-backed secret usage in GitHub Actions
SECRET_PATTERNS = [
    # PAT-backed secrets (secrets.XYZ in workflow YAML)
    # GH_PAT_SUPERSET is matched here too — allowlist logic handles it
    (
        r"secrets\.(GH_PAT\w*)",
        "PAT-backed secret",
    ),
    (
        r"secrets\.(GITHUB_PAT\w+)",
        "PAT-backed secret",
    ),
    (
        r"secrets\.(ADMIN_PAT\w*)",
        "Deprecated admin PAT secret",
    ),
    (
        r"secrets\.(ORG_TOKEN)\b",
        "Deprecated org token secret",
    ),
    (
        r"secrets\.(CR_PAT)\b",
        "Deprecated container registry PAT secret",
    ),
    (
        r"secrets\.(PROJECTS_TOKEN)\b",
        "Deprecated projects token secret",
    ),
]

# Patterns that signal hardcoded PATs in source
HARDCODED_PATTERNS = [
    (
        r'Authorization["\s:]*(?:Bearer\s+|token\s+)?ghp_[A-Za-z0-9_]+',
        "Hardcoded classic PAT in Authorization header",
    ),
    (
        r'Authorization["\s:]*(?:Bearer\s+|token\s+)?github_pat_[A-Za-z0-9_]+',
        "Hardcoded fine-grained PAT in Authorization header",
    ),
]

# Allowlisted patterns — these are approved exceptions
ALLOWLIST = {
    "GH_PAT_SUPERSET": {
        "reason": "Cross-repo dispatch to jgtolentino/superset",
        "expires": "2026-06-30",
        "consumer": ".github/workflows/notify-superset.yml",
    },
}

# Files that are part of the auth enforcement infra itself (self-references OK)
INFRA_FILES = {
    "github-auth-surface-guard.yml",
    "github-auth-surface-contract.yml",
    "check_github_pat_usage.py",
    "github_auth_surface.yaml",
    "registry.yaml",
}


# ── Scanner ──────────────────────────────────────────────────────────────────


def gather_files() -> list[Path]:
    """Collect all files matching scan paths."""
    files: list[Path] = []
    for glob_pattern in SCAN_PATHS:
        files.extend(REPO_ROOT.glob(glob_pattern))
    return sorted(set(files))


def is_infra_file(path: Path) -> bool:
    """Check if file is part of auth enforcement infrastructure."""
    return path.name in INFRA_FILES


def is_comment_or_doc_line(line: str, path: Path) -> bool:
    """Check if a line is a comment or documentation (not executable)."""
    stripped = line.strip()
    suffix = path.suffix

    if suffix in (".yml", ".yaml"):
        return stripped.startswith("#")
    if suffix == ".py":
        return stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''")
    if suffix == ".sh":
        return stripped.startswith("#")
    if suffix in (".ts", ".js"):
        return stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*")
    return False


def check_allowlist(secret_name: str) -> bool:
    """Check if a secret is on the allowlist and not expired."""
    entry = ALLOWLIST.get(secret_name)
    if not entry:
        return False
    expires = datetime.strptime(entry["expires"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    if now > expires:
        return False  # Allowlist entry expired
    return True


def scan_file(path: Path) -> list[dict]:
    """Scan a single file for PAT references. Returns list of findings."""
    findings = []
    rel_path = path.relative_to(REPO_ROOT)

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return findings

    for line_num, line in enumerate(content.splitlines(), start=1):
        # Skip infra self-references (the guard/scanner files themselves)
        if is_infra_file(path):
            continue

        # Check secret patterns
        for pattern, description in SECRET_PATTERNS:
            match = re.search(pattern, line)
            if match:
                secret_name = match.group(1)
                if check_allowlist(secret_name):
                    findings.append({
                        "file": str(rel_path),
                        "line": line_num,
                        "secret": secret_name,
                        "description": f"ALLOWLISTED: {description}",
                        "content": line.strip(),
                        "severity": "info",
                        "allowlisted": True,
                    })
                else:
                    findings.append({
                        "file": str(rel_path),
                        "line": line_num,
                        "secret": secret_name,
                        "description": description,
                        "content": line.strip(),
                        "severity": "error",
                        "allowlisted": False,
                    })

        # Check hardcoded patterns (always an error, never allowlisted)
        for pattern, description in HARDCODED_PATTERNS:
            if re.search(pattern, line):
                findings.append({
                    "file": str(rel_path),
                    "line": line_num,
                    "secret": "HARDCODED_TOKEN",
                    "description": description,
                    "content": line.strip()[:120] + ("..." if len(line.strip()) > 120 else ""),
                    "severity": "critical",
                    "allowlisted": False,
                })

    return findings


def write_report(findings: list[dict], report_path: Path) -> None:
    """Write JSON report to evidence directory."""
    report_path.parent.mkdir(parents=True, exist_ok=True)

    errors = [f for f in findings if f["severity"] in ("error", "critical")]
    warnings = [f for f in findings if f["severity"] == "info"]

    report = {
        "schema": "ssot.auth.pat_usage_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": "zero-pat",
        "ssot": "ssot/auth/github_auth_surface.yaml",
        "summary": {
            "total_findings": len(findings),
            "errors": len(errors),
            "allowlisted": len(warnings),
            "pass": len(errors) == 0,
        },
        "findings": findings,
    }

    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    files = gather_files()
    all_findings: list[dict] = []

    for f in files:
        all_findings.extend(scan_file(f))

    errors = [f for f in all_findings if f["severity"] in ("error", "critical")]
    allowlisted = [f for f in all_findings if f["allowlisted"]]

    # Write report
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    report_path = REPO_ROOT / f"docs/evidence/auth_surface/{run_id}/pat_usage_report.json"
    write_report(all_findings, report_path)

    # Console output
    print(f"GitHub PAT Usage Scanner")
    print(f"========================")
    print(f"Policy:      Zero-PAT (App + GITHUB_TOKEN only)")
    print(f"SSOT:        ssot/auth/github_auth_surface.yaml")
    print(f"Files:       {len(files)} scanned")
    print(f"Findings:    {len(all_findings)} total")
    print(f"Errors:      {len(errors)}")
    print(f"Allowlisted: {len(allowlisted)}")
    print(f"Report:      {report_path.relative_to(REPO_ROOT)}")
    print()

    if allowlisted:
        print("Allowlisted (temporary exceptions):")
        for f in allowlisted:
            entry = ALLOWLIST.get(f["secret"], {})
            print(f"  {f['file']}:{f['line']} — {f['secret']} (expires {entry.get('expires', '?')})")
        print()

    if errors:
        print("VIOLATIONS:")
        for f in errors:
            print(f"  {f['severity'].upper()} {f['file']}:{f['line']}")
            print(f"    Secret: {f['secret']}")
            print(f"    Reason: {f['description']}")
            print(f"    Line:   {f['content']}")
            print(f"    Fix:    Use secrets.GITHUB_TOKEN or github_app_ipai_integrations")
            print()
        print(f"FAIL  {len(errors)} PAT reference(s) violate zero-PAT policy")
        return 1

    print("PASS  No unauthorized PAT references found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
