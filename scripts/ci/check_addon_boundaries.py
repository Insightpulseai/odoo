#!/usr/bin/env python3
"""
Addon boundary enforcement — CI gate.

Rules:
  1. addons/ipai/ modules must have ipai_ prefix
  2. addons/oca/ must only contain OCA repo directories (no loose modules)
  3. addons/local/ must not contain ipai_ prefixed modules
  4. All three addon roots must exist
  5. Every OCA repo under addons/oca/ should have at least one __manifest__.py
     (known-empty repos on 19.0 are downgraded to warnings)

Exit 0 = pass, Exit 1 = violation found.
"""
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADDONS_DIR = REPO_ROOT / "addons"

# OCA repos known to have no 19.0 modules yet — downgrade to warning, not error.
# Review periodically: if modules appear on 19.0, remove from this list.
OCA_ALLOWED_EMPTY = {
    "social",       # no modules on 19.0 branch as of 2026-03
}

errors = []
warnings = []


def check_addon_roots_exist():
    """Rule 4: All three addon roots must exist."""
    for root in ("oca", "ipai", "local"):
        path = ADDONS_DIR / root
        if not path.is_dir():
            errors.append(f"MISSING: addons/{root}/ does not exist")


def check_ipai_prefix():
    """Rule 1: Every module in addons/ipai/ must start with ipai_."""
    ipai_dir = ADDONS_DIR / "ipai"
    if not ipai_dir.is_dir():
        return
    for entry in sorted(ipai_dir.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        if not entry.name.startswith("ipai_"):
            errors.append(
                f"BOUNDARY: addons/ipai/{entry.name} does not have ipai_ prefix. "
                f"Move to addons/local/ or rename."
            )


def check_oca_structure():
    """Rule 2 & 5: OCA entries should be repo dirs with modules inside."""
    oca_dir = ADDONS_DIR / "oca"
    if not oca_dir.is_dir():
        return
    for entry in sorted(oca_dir.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        # Check it looks like an OCA repo (has at least one module with __manifest__.py)
        manifests = list(entry.glob("*/__manifest__.py"))
        if not manifests:
            # Could be a repo with modules at root level
            root_manifest = entry / "__manifest__.py"
            if root_manifest.exists():
                errors.append(
                    f"STRUCTURE: addons/oca/{entry.name} has __manifest__.py at root. "
                    f"OCA repos contain modules as subdirectories, not at root level."
                )
            elif entry.name in OCA_ALLOWED_EMPTY:
                warnings.append(
                    f"ALLOWED-EMPTY: addons/oca/{entry.name} has no 19.0 modules (allowlisted)"
                )
            else:
                errors.append(
                    f"EMPTY: addons/oca/{entry.name} has no modules with __manifest__.py. "
                    f"Add to OCA_ALLOWED_EMPTY in this script if intentional."
                )


def check_local_no_ipai():
    """Rule 3: addons/local/ must not contain ipai_ prefixed modules."""
    local_dir = ADDONS_DIR / "local"
    if not local_dir.is_dir():
        return
    for entry in sorted(local_dir.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        if entry.name.startswith("ipai_"):
            errors.append(
                f"BOUNDARY: addons/local/{entry.name} has ipai_ prefix. "
                f"Move to addons/ipai/."
            )


def main():
    check_addon_roots_exist()
    check_ipai_prefix()
    check_oca_structure()
    check_local_no_ipai()

    # Print warnings (non-blocking)
    for warn in warnings:
        print(f"  WARN: {warn}")

    if errors:
        print(f"\nFAIL: {len(errors)} addon boundary violation(s):\n")
        for err in errors:
            print(f"  - {err}")
        return 1
    else:
        # Count inventory
        ipai_count = sum(
            1 for d in (ADDONS_DIR / "ipai").iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ) if (ADDONS_DIR / "ipai").is_dir() else 0
        oca_repos = sum(
            1 for d in (ADDONS_DIR / "oca").iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ) if (ADDONS_DIR / "oca").is_dir() else 0
        local_count = sum(
            1 for d in (ADDONS_DIR / "local").iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ) if (ADDONS_DIR / "local").is_dir() else 0
        print(
            f"PASS: addon boundaries OK "
            f"(ipai: {ipai_count}, oca repos: {oca_repos}, local: {local_count})"
        )
        if warnings:
            print(f"  ({len(warnings)} warning(s) — see above)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
