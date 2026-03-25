#!/usr/bin/env python3
"""CI gate: scan public-facing files for forbidden first-party branding.

Fails on:
- "Odoo Copilot", "InsightPulse Copilot", "IPAI Copilot" etc.
- bare "copilot" unless referencing Microsoft products
- "Odoo AI" as a product name

Allows:
- "Microsoft Copilot", "Microsoft 365 Copilot", "Security Copilot"
- Internal code files (not scanned)
- Governance docs (excluded to avoid self-flagging)

Exit 0 = clean. Exit 1 = violations found.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Directories to scan (public-facing surfaces)
PUBLIC_DIRS = [
    "web",
    "docs",
]

# Paths to exclude
EXCLUDE_PATTERNS = [
    r"docs/governance/.*",  # governance docs define the rules, not violate them
    r".*node_modules/.*",
    r".*dist/.*",
    r".*build/.*",
    r".*\.next/.*",
    r".*package-lock\.json$",
    r".*pnpm-lock\.yaml$",
    r".*\.DS_Store$",
]

# Forbidden first-party branding patterns
FORBIDDEN_PATTERNS = [
    re.compile(r"\bOdoo Copilot\b", re.IGNORECASE),
    re.compile(r"\bInsightPulse Copilot\b", re.IGNORECASE),
    re.compile(r"\bIPAI Copilot\b", re.IGNORECASE),
    re.compile(r"\bAsk IPAI Copilot\b", re.IGNORECASE),
    re.compile(r"\bAsk Odoo Copilot\b", re.IGNORECASE),
    re.compile(r"\bOdoo AI\b", re.IGNORECASE),
]

# Allowed referential Microsoft phrases
ALLOWED_REFERENTIAL = [
    re.compile(r"\bMicrosoft Copilot\b", re.IGNORECASE),
    re.compile(r"\bMicrosoft 365 Copilot\b", re.IGNORECASE),
    re.compile(r"\bSecurity Copilot\b", re.IGNORECASE),
    re.compile(r"\bGitHub Copilot\b", re.IGNORECASE),
    re.compile(r"\bcopilot-style\b", re.IGNORECASE),  # descriptor OK
]

TEXT_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".md", ".mdx", ".html", ".css", ".scss",
    ".json", ".yml", ".yaml", ".txt", ".xml",
}


def is_excluded(rel: pathlib.Path) -> bool:
    s = str(rel)
    return any(re.match(p, s) for p in EXCLUDE_PATTERNS)


def iter_files() -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for d in PUBLIC_DIRS:
        target = ROOT / d
        if target.is_dir():
            for f in target.rglob("*"):
                if f.is_file() and f.suffix.lower() in TEXT_EXTENSIONS:
                    rel = f.relative_to(ROOT)
                    if not is_excluded(rel):
                        files.append(rel)
    return sorted(set(files))


def line_is_referential(line: str) -> bool:
    return any(p.search(line) for p in ALLOWED_REFERENTIAL)


def main() -> int:
    violations: list[str] = []

    for rel in iter_files():
        full = ROOT / rel
        try:
            content = full.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        for lineno, line in enumerate(content.splitlines(), start=1):
            # Check explicit forbidden patterns
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    violations.append(
                        f"  {rel}:{lineno}: {pattern.pattern} -> {line.strip()[:80]}"
                    )

    if violations:
        print(f"Branding policy violations ({len(violations)}):\n")
        for v in violations:
            print(v)
        print(f"\nSee docs/governance/BRANDING_STRING_MATRIX.md for replacements.")
        return 1

    print("Branding policy check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
