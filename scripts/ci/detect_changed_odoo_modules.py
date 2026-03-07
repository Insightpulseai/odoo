#!/usr/bin/env python3
"""Detect changed Odoo modules from git diff.

Scans git diff between base and head refs to identify which Odoo modules
have been modified. Outputs a JSON array of module names suitable for
targeted CI testing.

Usage:
    # Compare against default branch
    python scripts/ci/detect_changed_odoo_modules.py

    # Compare specific refs
    python scripts/ci/detect_changed_odoo_modules.py --base origin/main --head HEAD

    # Output as comma-separated list (for Odoo -i flag)
    python scripts/ci/detect_changed_odoo_modules.py --format csv

Exit codes:
    0 — modules found (or --allow-empty)
    1 — error
    2 — no modules changed (unless --allow-empty)
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


# Addon paths to scan (relative to repo root)
ADDON_PATHS = [
    "addons",          # top-level: addons/ipai_*, addons/oca/
    "addons/ipai",     # nested: addons/ipai/ipai_*
]


def get_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    )
    return Path(result.stdout.strip())


def get_changed_files(base_ref: str, head_ref: str) -> list[str]:
    """Get list of changed files between two refs."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_ref}...{head_ref}"],
            capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError:
        # Fallback: diff against base directly (for shallow clones)
        result = subprocess.run(
            ["git", "diff", "--name-only", base_ref, head_ref],
            capture_output=True, text=True, check=True,
        )
    return [f for f in result.stdout.strip().split("\n") if f]


def is_odoo_module(path: Path) -> bool:
    """Check if a directory is an Odoo module (has __manifest__.py)."""
    return (path / "__manifest__.py").exists()


def extract_modules(changed_files: list[str], repo_root: Path) -> set[str]:
    """Extract Odoo module names from changed file paths."""
    modules = set()

    for filepath in changed_files:
        parts = Path(filepath).parts

        if len(parts) < 2:
            continue

        # Pattern 1: addons/<module_name>/...
        if parts[0] == "addons" and len(parts) >= 2:
            candidate = parts[1]

            # Skip non-module directories
            if candidate in ("oca", "_deprecated", "__pycache__"):
                # Pattern 2: addons/ipai/<module_name>/...
                if candidate == "ipai" and len(parts) >= 3:
                    mod_name = parts[2]
                    mod_path = repo_root / "addons" / "ipai" / mod_name
                    if is_odoo_module(mod_path):
                        modules.add(mod_name)
                # Pattern 3: addons/oca/<repo>/<module_name>/...
                elif candidate == "oca" and len(parts) >= 4:
                    mod_name = parts[3]
                    mod_path = repo_root / "addons" / "oca" / parts[2] / mod_name
                    if is_odoo_module(mod_path):
                        modules.add(mod_name)
                continue

            # Check if addons/<candidate> is itself a module
            mod_path = repo_root / "addons" / candidate
            if is_odoo_module(mod_path):
                modules.add(candidate)
            # Or addons/ipai/<...> nested pattern caught above
            elif candidate == "ipai" and len(parts) >= 3:
                mod_name = parts[2]
                mod_path = repo_root / "addons" / "ipai" / mod_name
                if is_odoo_module(mod_path):
                    modules.add(mod_name)

    return modules


def main():
    parser = argparse.ArgumentParser(description="Detect changed Odoo modules")
    parser.add_argument(
        "--base", default=os.environ.get("BASE_REF", "origin/main"),
        help="Base git ref (default: origin/main or $BASE_REF)",
    )
    parser.add_argument(
        "--head", default=os.environ.get("HEAD_REF", "HEAD"),
        help="Head git ref (default: HEAD or $HEAD_REF)",
    )
    parser.add_argument(
        "--format", choices=["json", "csv"], default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--allow-empty", action="store_true",
        help="Exit 0 even if no modules changed",
    )
    args = parser.parse_args()

    repo_root = get_repo_root()
    changed_files = get_changed_files(args.base, args.head)
    modules = sorted(extract_modules(changed_files, repo_root))

    if args.format == "json":
        print(json.dumps(modules))
    else:
        print(",".join(modules))

    # Log to stderr for CI visibility
    if modules:
        print(f"Detected {len(modules)} changed module(s): {', '.join(modules)}", file=sys.stderr)
    else:
        print("No Odoo modules changed.", file=sys.stderr)

    if not modules and not args.allow_empty:
        sys.exit(2)


if __name__ == "__main__":
    main()
