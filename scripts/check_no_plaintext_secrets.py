#!/usr/bin/env python3
"""
check_no_plaintext_secrets.py — Scan staged/changed files for plaintext secrets.

Detects common secret patterns in file diffs and repo content. Designed to run
as a pre-commit hook and in CI (secrets-scan-gate.yml).

Permitted forms (never flagged):
  ${ENV_VAR_NAME}              — shell env var reference
  ${{ secrets.NAME }}          — GitHub Actions secret reference
  vault.decrypted_secrets      — Supabase Vault reference
  <from keychain>              — keychain placeholder
  <placeholder>                — generic placeholder
  keychain_ref: <label>        — documented keychain reference

Exit codes:
  0 — no secrets detected
  1 — one or more secrets detected (see output for details)

Usage:
  # Scan git diff (CI mode — only changed files):
  git diff --name-only HEAD~1 | python3 scripts/check_no_plaintext_secrets.py --diff

  # Scan specific files:
  python3 scripts/check_no_plaintext_secrets.py path/to/file.py

  # Scan all tracked files (expensive; use for audits):
  python3 scripts/check_no_plaintext_secrets.py --all
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Secret patterns — (name, regex, severity)
# ---------------------------------------------------------------------------
SECRET_PATTERNS: List[Tuple[str, re.Pattern, str]] = [
    # GitHub tokens
    ("GitHub Personal Access Token (classic)", re.compile(r"\bghp_[A-Za-z0-9]{36}\b"), "CRITICAL"),
    ("GitHub OAuth token", re.compile(r"\bgho_[A-Za-z0-9]{36}\b"), "CRITICAL"),
    ("GitHub App token", re.compile(r"\bghs_[A-Za-z0-9]{36}\b"), "CRITICAL"),
    ("GitHub Actions token", re.compile(r"\bghr_[A-Za-z0-9]{36}\b"), "CRITICAL"),
    ("GitHub Fine-Grained PAT", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{59}\b"), "CRITICAL"),

    # Bearer tokens (generic long tokens)
    ("Bearer token (long)", re.compile(r"\bBearer\s+[A-Za-z0-9_\-\.]{40,}\b"), "HIGH"),

    # JWT (non-expiry check — any JWT in a source file is a red flag)
    ("JWT token (hardcoded)", re.compile(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\b"), "HIGH"),

    # Supabase / Postgres credentials
    ("Supabase service role key (JWT)", re.compile(r"\beyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\b"), "CRITICAL"),

    # API keys — common patterns
    ("OpenAI API key", re.compile(r"\bsk-[A-Za-z0-9]{32,}\b"), "CRITICAL"),
    ("Anthropic API key", re.compile(r"\bsk-ant-api[A-Za-z0-9\-_]{20,}\b"), "CRITICAL"),
    ("Stripe secret key", re.compile(r"\bsk_(live|test)_[A-Za-z0-9]{24,}\b"), "CRITICAL"),
    ("Mailgun API key", re.compile(r"\bkey-[0-9a-f]{32}\b"), "HIGH"),
    ("Cloudflare API token (40 char hex+)", re.compile(r"\b[A-Za-z0-9_\-]{37,40}Q[A-Za-z0-9_\-]{1,5}\b"), "MEDIUM"),  # CF tokens end in specific format
    ("DigitalOcean PAT (dop_v1)", re.compile(r"\bdop_v1_[A-Za-z0-9]{64}\b"), "CRITICAL"),

    # Generic high-entropy passwords in assignments
    ("Hardcoded password assignment", re.compile(
        r'(?i)(password|passwd|pwd|secret|token|api_key|apikey|access_key|auth_token)\s*[:=]\s*["\'][A-Za-z0-9!@#$%^&*()_+\-=\[\]{};:,./?~`]{12,}["\']'
    ), "HIGH"),

    # Private keys
    ("RSA/EC private key", re.compile(r"-----BEGIN (RSA|EC|OPENSSH|DSA|PGP) PRIVATE KEY-----"), "CRITICAL"),
    ("Private key (generic)", re.compile(r"-----BEGIN PRIVATE KEY-----"), "CRITICAL"),
]

# ---------------------------------------------------------------------------
# Allowlist — patterns that override false positives
# Match against the full line content.
# ---------------------------------------------------------------------------
ALLOWLIST_PATTERNS: List[re.Pattern] = [
    # Shell/Python env var references
    re.compile(r'\$\{[A-Z_][A-Z0-9_]*\}'),
    # GitHub Actions secret references
    re.compile(r'\$\{\{[^}]*secrets\.[A-Z_][A-Z0-9_]*[^}]*\}\}'),
    # Supabase Vault references
    re.compile(r'vault\.decrypted_secrets'),
    re.compile(r'vault_secret_name:'),
    re.compile(r'supabase_vault_ref:'),
    # Keychain/placeholder markers
    re.compile(r'<from keychain>'),
    re.compile(r'<placeholder>'),
    re.compile(r'keychain_ref:'),
    # Example/template markers
    re.compile(r'(EXAMPLE|example|placeholder|your[-_]|<YOUR_|MY_TOKEN|REPLACE_ME)'),
    # Test/fixture markers
    re.compile(r'(test_secret|fake_token|dummy_key|mock_key|test_key|sample_key|example_key)'),
    # Documentation patterns (the scanner itself explains patterns)
    re.compile(r'(re\.compile|r"\\b|r\'\\b)'),
    # .example files are documentation — not enforced
    # (handled at file-level, not line-level)
    # Hash-preceded lines in YAML (key names only, no values)
    re.compile(r'^\s*#'),
]

# ---------------------------------------------------------------------------
# File extensions / names to always skip
# ---------------------------------------------------------------------------
SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".tar", ".gz",
    ".woff", ".woff2", ".ttf", ".eot", ".svg", ".lock", ".sum",
}
SKIP_FILENAMES = {
    "pnpm-lock.yaml", "yarn.lock", "package-lock.json", "poetry.lock",
    "go.sum", "Pipfile.lock",
}
SKIP_PATH_PATTERNS = [
    re.compile(r"\.example$"),          # .env.example, etc.
    re.compile(r"\.example\."),         # file.example.yaml
    re.compile(r"/tests?/fixtures?/"),  # test fixtures
    re.compile(r"SECRETS_SSOT\.md$"),   # secrets runbook (documents patterns)
    re.compile(r"check_no_plaintext_secrets\.py$"),  # this script itself
]


def should_skip_file(path: str) -> bool:
    p = Path(path)
    if p.suffix.lower() in SKIP_EXTENSIONS:
        return True
    if p.name in SKIP_FILENAMES:
        return True
    for pat in SKIP_PATH_PATTERNS:
        if pat.search(path):
            return True
    return False


def line_is_allowed(line: str) -> bool:
    """Return True if the line matches any allowlist pattern."""
    for pat in ALLOWLIST_PATTERNS:
        if pat.search(line):
            return True
    return False


def scan_file(filepath: str) -> List[Tuple[int, str, str, str]]:
    """
    Scan a file for secret patterns.
    Returns list of (line_number, pattern_name, severity, line_content).
    """
    if should_skip_file(filepath):
        return []

    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except (OSError, PermissionError):
        return []

    findings = []
    for lineno, line in enumerate(lines, start=1):
        # Skip comment lines and allowlisted lines early
        stripped = line.strip()
        if not stripped:
            continue
        if line_is_allowed(line):
            continue

        for name, pattern, severity in SECRET_PATTERNS:
            if pattern.search(line):
                # Double-check: if after removing env-var refs the match disappears, allow it
                cleaned = re.sub(r'\$\{[A-Z_][A-Z0-9_]*\}', 'ENVREF', line)
                cleaned = re.sub(r'\$\{\{[^}]*\}\}', 'GHSECREF', cleaned)
                if not pattern.search(cleaned):
                    continue  # was an env var ref that happened to match the pattern shape
                findings.append((lineno, name, severity, line.rstrip()))
                break  # one finding per line is enough

    return findings


def get_changed_files_from_git() -> List[str]:
    """Get list of files changed vs HEAD~1 (CI mode)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1"],
            capture_output=True, text=True, check=True,
        )
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        return [f for f in files if os.path.isfile(f)]
    except subprocess.CalledProcessError:
        # Fallback: staged files (pre-commit mode)
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True,
        )
        return [f.strip() for f in result.stdout.splitlines() if f.strip() and os.path.isfile(f.strip())]


def get_all_tracked_files() -> List[str]:
    """Get all files tracked by git."""
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True, text=True,
    )
    return [f.strip() for f in result.stdout.splitlines() if f.strip() and os.path.isfile(f.strip())]


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan files for plaintext secrets.")
    parser.add_argument("files", nargs="*", help="Files to scan (positional)")
    parser.add_argument("--diff", action="store_true", help="Scan git-changed files vs HEAD~1")
    parser.add_argument("--all", action="store_true", help="Scan all tracked files")
    parser.add_argument("--no-fail", action="store_true", help="Report but exit 0 (audit mode)")
    args = parser.parse_args()

    if args.diff:
        files = get_changed_files_from_git()
    elif args.all:
        files = get_all_tracked_files()
    elif args.files:
        files = args.files
    else:
        # Default: scan git-changed files (suitable for CI)
        files = get_changed_files_from_git()

    if not files:
        print("No files to scan.")
        sys.exit(0)

    total_findings = 0
    has_critical = False

    for filepath in files:
        findings = scan_file(filepath)
        if not findings:
            continue

        print(f"\n{'='*60}")
        print(f"FILE: {filepath}")
        print(f"{'='*60}")
        for lineno, name, severity, line_content in findings:
            total_findings += 1
            if severity == "CRITICAL":
                has_critical = True
            preview = line_content[:120] + ("..." if len(line_content) > 120 else "")
            print(f"  [{severity}] Line {lineno}: {name}")
            print(f"           {preview}")

    if total_findings == 0:
        print(f"✅ No plaintext secrets detected in {len(files)} file(s).")
        sys.exit(0)

    print(f"\n{'='*60}")
    print(f"RESULT: {total_findings} potential secret(s) detected.")
    print(f"{'='*60}")
    print("")
    print("Approved alternatives:")
    print("  Local dev:  store in OS keychain; inject as env var at shell start")
    print("  CI:         GitHub Actions secret  ${{ secrets.NAME }}")
    print("  Platform:   Supabase Vault         vault_secret_name: <key>")
    print("  Reference:  docs/runbooks/SECRETS_SSOT.md")
    print("")

    if args.no_fail:
        print("(--no-fail mode: exiting 0 despite findings)")
        sys.exit(0)

    sys.exit(1)


if __name__ == "__main__":
    main()
