#!/usr/bin/env python3
"""Root-boundary drift guard.

Scans the repo root directory and classifies every entry as:
  CANONICAL   - listed in the hardcoded allowlist (or external allowlist)
  EXCEPTION   - known drift that is not yet relocated
  UNKNOWN_WARNING - unlisted entry (warn-only, non-blocking)
  UNKNOWN_ERROR   - unlisted entry (blocking in --strict mode)

Exit codes:
  0  all entries are CANONICAL, EXCEPTION, or UNKNOWN_WARNING
  1  at least one UNKNOWN_ERROR (only possible with --strict)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Hardcoded canonical top-level entries
# ---------------------------------------------------------------------------
CANONICAL_ENTRIES: set[str] = {
    # Directories
    ".github",
    ".claude",
    ".agent",
    ".devcontainer",
    ".vscode",
    ".git",
    "addons",
    "agents",
    "skills",
    "config",
    "docker",
    "runtime",
    "scripts",
    "supabase",
    "infra",
    "apps",
    "packages",
    "docs",
    "spec",
    "ssot",
    "tests",
    # Files
    ".gitignore",
    ".pre-commit-config.yaml",
    "Makefile",
    "package.json",
    "pnpm-workspace.yaml",
    "turbo.json",
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    "README.md",
    "odoo-bin",
    "vercel.json",
    "pyproject.toml",
    ".env",
    ".env.example",
    ".env.dev",
    ".env.prod",
    ".env.stage",
    "requirements.txt",
    "requirements-dev.txt",
    "CHANGELOG.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    ".flake8",
    ".yamllint.yml",
    ".python-version",
    ".mypy-baseline.txt",
    # Lockfiles and workspace artifacts
    "pnpm-lock.yaml",
    "docker-compose.yml",
    "docker-compose.dev.yml",
    "Dockerfile",
}

# ---------------------------------------------------------------------------
# Known exceptions — real entries that are not yet relocated.
# Each maps to a short note explaining why it exists.
# ---------------------------------------------------------------------------
KNOWN_EXCEPTIONS: dict[str, str] = {
    "catalog": "parity catalog — pending relocation to docs/ or spec/",
    "catalogs": "plural variant of catalog — pending merge",
    "mcp": "MCP server definitions — pending relocation to infra/ or packages/",
    "n8n": "n8n workflow exports — pending relocation to automations/",
    "specs": "plural variant of spec — pending merge into spec/",
    "scratch": "developer scratch area — should be gitignored or removed",
    "sandbox": "transient sandbox — should be gitignored or removed",
    "out": "build output — should be gitignored",
    "odoo_local": "local Odoo dev data — should be gitignored",
    "odoo19": "Odoo 19 checkout — pending relocation",
    "web": "web frontend apps — pending relocation to apps/",
    "archive": "archived content — pending relocation to docs/archive/",
    "templates": "reusable scaffolds — pending relocation",
    "third_party": "third-party deps — pending relocation to vendor/",
    "vendor": "vendored deps — pending policy decision",
    "patches": "runtime patches — pending relocation to runtime/patches/",
    "automations": "automation scripts — pending relocation to n8n/ or scripts/",
    "workflows": "workflow definitions — pending relocation",
}


def load_external_allowlist(path: str) -> set[str]:
    """Load additional allowed entries from a YAML file.

    Expected format (flat list under 'allowed:' key):
        allowed:
          - entry_name
          - another_entry
    """
    entries: set[str] = set()
    try:
        with open(path) as f:
            content = f.read()
    except FileNotFoundError:
        print(f"WARNING: allowlist file not found: {path}", file=sys.stderr)
        return entries

    # Minimal YAML parsing — no external deps required
    in_allowed = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "allowed:":
            in_allowed = True
            continue
        if in_allowed:
            if stripped.startswith("- "):
                entries.add(stripped[2:].strip().strip("'\""))
            elif stripped and not stripped.startswith("#"):
                # New top-level key, stop parsing
                break
    return entries


def scan_root(repo_root: Path) -> list[str]:
    """Return sorted list of top-level entries in the repo root."""
    entries = []
    for entry in repo_root.iterdir():
        name = entry.name
        # Skip . and .. (shouldn't appear with iterdir, but be safe)
        if name in (".", ".."):
            continue
        entries.append(name)
    return sorted(entries)


def classify(
    entries: list[str],
    canonical: set[str],
    exceptions: dict[str, str],
    strict: bool,
) -> dict[str, list[tuple[str, str]]]:
    """Classify each entry into a category.

    Returns dict mapping category -> list of (entry, note) tuples.
    """
    results: dict[str, list[tuple[str, str]]] = {
        "CANONICAL": [],
        "EXCEPTION": [],
        "UNKNOWN_WARNING": [],
        "UNKNOWN_ERROR": [],
    }

    for entry in entries:
        if entry in canonical:
            results["CANONICAL"].append((entry, ""))
        elif entry in exceptions:
            results["EXCEPTION"].append((entry, exceptions[entry]))
        elif strict:
            results["UNKNOWN_ERROR"].append((entry, "not in allowlist (strict mode)"))
        else:
            results["UNKNOWN_WARNING"].append(
                (entry, "not in allowlist (warn-only)")
            )

    return results


def print_report(results: dict[str, list[tuple[str, str]]]) -> None:
    """Print a human-readable drift report."""
    total = sum(len(v) for v in results.values())
    print("=" * 70)
    print("ROOT BOUNDARY DRIFT REPORT")
    print("=" * 70)
    print(f"Total root entries scanned: {total}")
    print(
        f"  CANONICAL:        {len(results['CANONICAL'])}"
    )
    print(
        f"  EXCEPTION:        {len(results['EXCEPTION'])}"
    )
    print(
        f"  UNKNOWN_WARNING:  {len(results['UNKNOWN_WARNING'])}"
    )
    print(
        f"  UNKNOWN_ERROR:    {len(results['UNKNOWN_ERROR'])}"
    )
    print("-" * 70)

    if results["EXCEPTION"]:
        print("\nEXCEPTIONS (known drift, warn-only):")
        for entry, note in results["EXCEPTION"]:
            print(f"  {entry:40s} -- {note}")

    if results["UNKNOWN_WARNING"]:
        print("\nUNKNOWN WARNINGS (not in allowlist, non-blocking):")
        for entry, note in results["UNKNOWN_WARNING"]:
            print(f"  {entry:40s} -- {note}")

    if results["UNKNOWN_ERROR"]:
        print("\nUNKNOWN ERRORS (not in allowlist, BLOCKING):")
        for entry, note in results["UNKNOWN_ERROR"]:
            print(f"  {entry:40s} -- {note}")

    if not results["EXCEPTION"] and not results["UNKNOWN_WARNING"] and not results["UNKNOWN_ERROR"]:
        print("\nAll root entries are canonical. No drift detected.")

    print("=" * 70)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check repo root for boundary drift against canonical allowlist."
    )
    parser.add_argument(
        "repo_root",
        nargs="?",
        default=None,
        help="Path to repo root (default: two levels up from this script)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Make all unknown entries blocking (exit 1)",
    )
    parser.add_argument(
        "--allowlist",
        type=str,
        default=None,
        help="Path to external YAML allowlist file with additional allowed entries",
    )
    parser.add_argument(
        "--report-file",
        type=str,
        default=None,
        help="Write report to this file (in addition to stdout)",
    )
    args = parser.parse_args()

    # Resolve repo root
    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
    else:
        # Default: script is at scripts/policy/check_root_boundary_drift.py
        repo_root = Path(__file__).resolve().parent.parent.parent

    if not repo_root.is_dir():
        print(f"ERROR: repo root is not a directory: {repo_root}", file=sys.stderr)
        return 2

    # Build canonical set
    canonical = set(CANONICAL_ENTRIES)
    if args.allowlist:
        extra = load_external_allowlist(args.allowlist)
        if extra:
            print(f"Loaded {len(extra)} additional entries from {args.allowlist}")
            canonical.update(extra)

    # Scan and classify
    entries = scan_root(repo_root)
    results = classify(entries, canonical, KNOWN_EXCEPTIONS, args.strict)

    # Print report
    print_report(results)

    # Optionally write report to file
    if args.report_file:
        import io

        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        print_report(results)
        sys.stdout = old_stdout
        report_path = Path(args.report_file)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(buf.getvalue())
        print(f"\nReport written to: {args.report_file}")

    # Exit code
    if results["UNKNOWN_ERROR"]:
        print("\nFAILED: Unknown entries found in strict mode.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
