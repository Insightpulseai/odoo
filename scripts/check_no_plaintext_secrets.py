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

  See also: ssot/secrets/allowlist_regex.txt (SSOT allowlist — loaded at runtime)

Exit codes:
  0 — no secrets detected
  1 — one or more secrets detected (see output for details)

Output format (stable, grep-compatible):
  path:line:SEVERITY:pattern_name

Usage:
  # Scan git diff (CI mode — only changed files):
  python3 scripts/check_no_plaintext_secrets.py --diff

  # Scan specific files:
  python3 scripts/check_no_plaintext_secrets.py path/to/file.py

  # Scan all tracked files (expensive; use for audits):
  python3 scripts/check_no_plaintext_secrets.py --all

  # Audit mode (report but exit 0):
  python3 scripts/check_no_plaintext_secrets.py --all --no-fail
"""

CONTRACT_VERSION = "1.1.0"  # Must match SECRETS_SSOT.md "Contract version:" line

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
    ("github-pat-classic", re.compile(r"\bghp_[A-Za-z0-9]{36}\b"), "CRITICAL"),
    ("github-oauth-token", re.compile(r"\bgho_[A-Za-z0-9]{36}\b"), "CRITICAL"),
    ("github-app-token", re.compile(r"\bghs_[A-Za-z0-9]{36}\b"), "CRITICAL"),
    ("github-actions-token", re.compile(r"\bghr_[A-Za-z0-9]{36}\b"), "CRITICAL"),
    ("github-fine-grained-pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{59}\b"), "CRITICAL"),

    # Bearer tokens (generic long tokens)
    ("bearer-token-long", re.compile(r"\bBearer\s+[A-Za-z0-9_\-\.]{40,}\b"), "HIGH"),

    # JWT (any hardcoded JWT in source is a red flag)
    ("jwt-hardcoded", re.compile(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\b"), "HIGH"),

    # Supabase service role key (JWT with known header)
    ("supabase-service-role-key", re.compile(
        r"\beyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\b"
    ), "CRITICAL"),

    # API keys — common providers
    ("openai-api-key", re.compile(r"\bsk-[A-Za-z0-9]{32,}\b"), "CRITICAL"),
    ("anthropic-api-key", re.compile(r"\bsk-ant-api[A-Za-z0-9\-_]{20,}\b"), "CRITICAL"),
    ("stripe-secret-key", re.compile(r"\bsk_(live|test)_[A-Za-z0-9]{24,}\b"), "CRITICAL"),
    ("mailgun-api-key", re.compile(r"\bkey-[0-9a-f]{32}\b"), "HIGH"),
    ("digitalocean-pat", re.compile(r"\bdop_v1_[A-Za-z0-9]{64}\b"), "CRITICAL"),

    # Generic password/secret assignments
    ("hardcoded-password-assignment", re.compile(
        r'(?i)(password|passwd|pwd|secret|token|api_key|apikey|access_key|auth_token)'
        r'\s*[:=]\s*["\'][A-Za-z0-9!@#$%^&*()_+\-=\[\]{};:,./?~`]{12,}["\']'
    ), "HIGH"),

    # Private keys
    ("rsa-private-key", re.compile(r"-----BEGIN (RSA|EC|OPENSSH|DSA|PGP) PRIVATE KEY-----"), "CRITICAL"),
    ("generic-private-key", re.compile(r"-----BEGIN PRIVATE KEY-----"), "CRITICAL"),
]

# ---------------------------------------------------------------------------
# Built-in allowlist (loaded first; SSOT file adds to this at runtime)
# ---------------------------------------------------------------------------
_BUILTIN_ALLOWLIST: List[re.Pattern] = [
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
    re.compile(r'(EXAMPLE|example|placeholder|your[-_]|<YOUR_|MY_TOKEN|REPLACE_ME|CHANGEME|__REPLACE__)'),
    # Test/fixture markers
    re.compile(r'(test_secret|fake_token|dummy_key|mock_key|test_key|sample_key|example_key|fixture_key)'),
    # Documentation patterns (the scanner itself explains patterns)
    re.compile(r'(re\.compile|r"\\b|r\'\\b)'),
    # Hash-preceded comment lines in YAML (key names only, no values)
    re.compile(r'^\s*#'),
]

ALLOWLIST_PATTERNS: List[re.Pattern] = list(_BUILTIN_ALLOWLIST)


def load_ssot_allowlist(repo_root: str) -> None:
    """Load additional allowlist regexes from ssot/secrets/allowlist_regex.txt."""
    allowlist_path = Path(repo_root) / "ssot" / "secrets" / "allowlist_regex.txt"
    if not allowlist_path.exists():
        return  # SSOT file optional; built-in allowlist is the minimum

    with open(allowlist_path, encoding="utf-8") as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                ALLOWLIST_PATTERNS.append(re.compile(line))
            except re.error as exc:
                # Non-fatal: warn but continue
                print(
                    f"Warning: allowlist_regex.txt line {lineno}: invalid regex '{line}': {exc}",
                    file=sys.stderr,
                )


# ---------------------------------------------------------------------------
# File extensions / names to always skip
# ---------------------------------------------------------------------------
SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".tar", ".gz",
    ".woff", ".woff2", ".ttf", ".eot", ".svg", ".lock", ".sum",
    ".pyc", ".pyo",
}
SKIP_FILENAMES = {
    "pnpm-lock.yaml", "yarn.lock", "package-lock.json", "poetry.lock",
    "go.sum", "Pipfile.lock",
}

# ---------------------------------------------------------------------------
# Directory prefixes to always skip (vendored / generated / build outputs)
# These generate excessive false positives and are not canonical source paths.
# ---------------------------------------------------------------------------
SKIP_DIR_PREFIXES = (
    "addons/odoo/",       # Odoo CE core — not our source
    "addons/oca/",        # OCA vendored modules
    "node_modules/",
    ".pnpm-store/",
    "vendor/",
    ".next/",
    "dist/",
    "build/",
    "__pycache__/",
    ".tox/",
    ".venv/",
    "venv/",
)

SKIP_PATH_PATTERNS = [
    re.compile(r"\.example$"),          # .env.example, etc.
    re.compile(r"\.example\."),         # file.example.yaml
    re.compile(r"/tests?/fixtures?/"),  # test fixtures
    re.compile(r"SECRETS_SSOT\.md$"),   # secrets runbook (documents patterns)
    re.compile(r"check_no_plaintext_secrets\.py$"),  # this script itself
    re.compile(r"allowlist_regex\.txt$"),            # SSOT allowlist file itself
]


def should_skip_file(path: str) -> bool:
    p = Path(path)
    if p.suffix.lower() in SKIP_EXTENSIONS:
        return True
    if p.name in SKIP_FILENAMES:
        return True
    # Normalise to forward-slash for prefix matching
    norm = path.replace("\\", "/")
    for prefix in SKIP_DIR_PREFIXES:
        if norm.startswith(prefix) or ("/" + prefix) in norm:
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
    Returns list of (line_number, pattern_id, severity, line_content).
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
        stripped = line.strip()
        if not stripped:
            continue
        if line_is_allowed(line):
            continue

        for name, pattern, severity in SECRET_PATTERNS:
            if pattern.search(line):
                # Double-check: if after substituting env-var refs the match disappears, allow it
                cleaned = re.sub(r'\$\{[A-Z_][A-Z0-9_]*\}', 'ENVREF', line)
                cleaned = re.sub(r'\$\{\{[^}]*\}\}', 'GHSECREF', cleaned)
                if not pattern.search(cleaned):
                    continue  # was an env var ref that happened to match pattern shape
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
        return [
            f.strip() for f in result.stdout.splitlines()
            if f.strip() and os.path.isfile(f.strip())
        ]


def get_all_tracked_files() -> List[str]:
    """Get all files tracked by git."""
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True, text=True,
    )
    return [
        f.strip() for f in result.stdout.splitlines()
        if f.strip() and os.path.isfile(f.strip())
    ]


def get_repo_root() -> str:
    """Return the git repository root, or cwd if not in a repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return os.getcwd()


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan files for plaintext secrets.")
    parser.add_argument("files", nargs="*", help="Files to scan (positional)")
    parser.add_argument("--diff", action="store_true", help="Scan git-changed files vs HEAD~1")
    parser.add_argument("--all", action="store_true", help="Scan all tracked files")
    parser.add_argument("--no-fail", action="store_true", help="Report but exit 0 (audit mode)")
    args = parser.parse_args()

    # Load SSOT allowlist (extends built-in list)
    repo_root = get_repo_root()
    load_ssot_allowlist(repo_root)

    if args.diff:
        files = get_changed_files_from_git()
    elif args.all:
        files = get_all_tracked_files()
    elif args.files:
        files = args.files
    else:
        files = get_changed_files_from_git()

    if not files:
        print("No files to scan.")
        sys.exit(0)

    total_findings = 0
    has_critical = False
    skipped = 0

    for filepath in files:
        if should_skip_file(filepath):
            skipped += 1
            continue

        findings = scan_file(filepath)
        if not findings:
            continue

        for lineno, name, severity, line_content in findings:
            total_findings += 1
            if severity == "CRITICAL":
                has_critical = True
            # Stable grep-compatible output: path:line:SEVERITY:pattern-id
            print(f"{filepath}:{lineno}:{severity}:{name}")
            # Indented preview (truncated, for human readability)
            preview = line_content.strip()[:100] + ("..." if len(line_content.strip()) > 100 else "")
            print(f"  {preview}")

    if total_findings == 0:
        print(
            f"✅ No plaintext secrets detected in {len(files) - skipped} file(s)"
            f" ({skipped} skipped)."
        )
        sys.exit(0)

    print("")
    print(f"{'='*60}")
    print(f"RESULT: {total_findings} potential secret(s) detected.")
    print(f"{'='*60}")
    print("")
    print("Approved alternatives:")
    print("  Local dev:  store in OS keychain; inject as env var at shell start")
    print("  CI:         GitHub Actions secret  ${{ secrets.NAME }}")
    print("  Platform:   Supabase Vault         vault_secret_name: <key>")
    print("  Allowlist:  ssot/secrets/allowlist_regex.txt (false-positive patterns)")
    print("  Runbook:    docs/runbooks/SECRETS_SSOT.md")
    print("")

    if args.no_fail:
        print("(--no-fail mode: exiting 0 despite findings)")
        sys.exit(0)

    sys.exit(1)


if __name__ == "__main__":
    main()
