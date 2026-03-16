#!/usr/bin/env python3
"""Check for forbidden naming aliases in active files."""
import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_ALIASES = {
    "lakehouse": "data-intelligence",
    "ops-platform": "platform",
    "design-system": "design",
}

# Path alias check (case-sensitive)
PATH_ALIASES = {
    "addons/OCA": "addons/oca",
}

BYPASS_PATTERNS = [
    re.compile(r"RECONCILIATION", re.IGNORECASE),
    re.compile(r"MIGRATION", re.IGNORECASE),
    re.compile(r"AUDIT", re.IGNORECASE),
    re.compile(r"MEMORY\.md$", re.IGNORECASE),
]

SKIP_DIRS = {"archive", "node_modules", ".git", "__pycache__", ".venv", ".claude",
             "vendor", ".devcontainer", ".supabase", ".temp", "odoo", "supabase",
             ".github", "apps", "packages"}
SKIP_EXTENSIONS = {".png", ".svg", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2",
                   ".ttf", ".eot", ".pdf", ".zip", ".tar", ".gz", ".lock", ".db",
                   ".pyc", ".pyo", ".so", ".dylib", ".json", ".sql"}

# Also skip this script itself
SELF_PATH = Path(__file__).resolve()


def is_bypass(path: Path) -> bool:
    name = str(path)
    return any(p.search(name) for p in BYPASS_PATTERNS)


SCAN_DIRS = ["docs", "ssot", "spec", "config", "scripts", "infra", "addons/ipai"]


def check_naming_drift(strict=False):
    violations = []

    # Only scan owned directories, not the entire repo
    files = []
    for scan_dir in SCAN_DIRS:
        d = REPO_ROOT / scan_dir
        if d.exists():
            files.extend(d.rglob("*"))

    for f in files:
        if f.is_dir() or f == SELF_PATH:
            continue

        rel = f.relative_to(REPO_ROOT)
        parts = rel.parts

        # Skip dirs
        if any(p in SKIP_DIRS for p in parts):
            continue
        # Skip binary
        if f.suffix.lower() in SKIP_EXTENSIONS:
            continue
        # Skip bypass patterns
        if is_bypass(rel):
            continue

        # Check path for forbidden aliases
        rel_str = str(rel)
        for alias, canonical in PATH_ALIASES.items():
            if alias in rel_str:
                violations.append(f"PATH: {rel} contains '{alias}' (use '{canonical}')")

        # Check file content for forbidden name aliases
        try:
            content = f.read_text(errors="ignore")
        except Exception:
            continue

        for alias, canonical in FORBIDDEN_ALIASES.items():
            # Match as whole word or path segment, not substring of longer words
            pattern = r'\b' + re.escape(alias) + r'\b'
            matches = list(re.finditer(pattern, content))
            if matches:
                # Report first occurrence with line number
                lines = content[:matches[0].start()].count('\n') + 1
                violations.append(f"CONTENT: {rel}:{lines} contains '{alias}' (use '{canonical}')")

    if violations:
        mode = "FAIL" if strict else "WARN"
        print(f"{mode}: {len(violations)} naming drift violation(s):")
        for v in violations[:50]:  # Cap output
            print(f"  - {v}")
        if len(violations) > 50:
            print(f"  ... and {len(violations) - 50} more")
        return 1 if strict else 0

    print("PASS: No naming drift detected")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Check for forbidden naming aliases")
    parser.add_argument("--strict", action="store_true", help="Fail on violations instead of warning")
    args = parser.parse_args()
    return check_naming_drift(strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
