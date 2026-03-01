#!/usr/bin/env python3
"""
check_deprecated_provider_defaults.py — Scan for deprecated provider defaults in addon code.

Catches regressions where a deprecated provider is hardcoded as the default
in Odoo model field definitions or param fallbacks.

Forbidden patterns (tuples of regex pattern, human-readable reason):
  - default="mailgun"   — Mailgun deprecated 2026-02, replaced by Zoho Mail
  - "mailgun"           — as a get_param/set_param fallback

Exit codes:
  0  no violations found
  1  one or more forbidden defaults detected (prints file:line for each)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Forbidden patterns
# Each entry: (compiled_regex, description, glob_pattern)
# ---------------------------------------------------------------------------
FORBIDDEN: list[tuple[re.Pattern, str, str]] = [
    (
        re.compile(r'default\s*=\s*["\']mailgun["\']'),
        "deprecated provider default='mailgun' (replace with 'zoho')",
        "**/*.py",
    ),
    (
        re.compile(r'get_param\([^)]+,\s*["\']mailgun["\']'),
        "deprecated get_param fallback 'mailgun' (replace with 'zoho')",
        "**/*.py",
    ),
    (
        re.compile(r'set_param\([^)]+\bor\s*["\']mailgun["\']'),
        "deprecated set_param fallback 'mailgun' (replace with 'zoho')",
        "**/*.py",
    ),
]

# Paths to scan (relative to repo root)
SCAN_ROOTS = [
    ROOT / "addons" / "ipai",
    ROOT / "scripts",
]

# Paths to exclude from scanning (e.g., archived docs, test fixtures)
EXCLUDE_PATTERNS = [
    "__pycache__",
    ".git",
    "tests/fixtures",
    "docs/",
    "config/MAILGUN_INTEGRATION_DEPLOYMENT.md",  # legacy doc — not code
    # Exclude this script itself (contains forbidden strings as documentation)
    "scripts/ci/check_deprecated_provider_defaults.py",
]


def is_excluded(path: Path) -> bool:
    parts = path.parts
    return any(ex in str(path) for ex in EXCLUDE_PATTERNS)


def scan() -> list[tuple[Path, int, str, str]]:
    """Return list of (file, lineno, matched_text, reason) for each violation."""
    violations: list[tuple[Path, int, str, str]] = []

    for scan_root in SCAN_ROOTS:
        if not scan_root.exists():
            continue
        for py_file in scan_root.rglob("*.py"):
            if is_excluded(py_file):
                continue
            try:
                lines = py_file.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue
            for lineno, line in enumerate(lines, start=1):
                for pattern, reason, _ in FORBIDDEN:
                    if pattern.search(line):
                        violations.append((py_file, lineno, line.strip(), reason))

    return violations


def main() -> int:
    violations = scan()
    if not violations:
        print("OK: no deprecated provider defaults found.")
        return 0

    print(f"ERROR: {len(violations)} deprecated provider default(s) found:\n", file=sys.stderr)
    for path, lineno, text, reason in violations:
        rel = path.relative_to(ROOT)
        print(f"  {rel}:{lineno}  →  {reason}", file=sys.stderr)
        print(f"    {text}", file=sys.stderr)

    print(
        "\nFix: replace forbidden defaults with the canonical provider "
        "(e.g., 'zoho' for mail). See ssot/runtime/prod_settings.yaml.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
