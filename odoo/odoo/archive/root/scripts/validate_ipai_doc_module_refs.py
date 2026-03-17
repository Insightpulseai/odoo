#!/usr/bin/env python3
"""
IPAI Doc ↔ Repo Module Drift Gate

Validates that documentation doesn't reference IPAI modules that don't exist in the repository.
Prevents recurrence of the "35 phantom modules" incident.

Exit codes:
  0: All module references are valid
  1: Found references to non-existent modules

Usage:
  python3 scripts/validate_ipai_doc_module_refs.py
"""

import re
import sys
from pathlib import Path


def get_repo_modules() -> set[str]:
    """Get actual IPAI module names from addons/ipai/ directory."""
    ipai_dir = Path("addons/ipai")
    if not ipai_dir.exists():
        print("❌ Error: addons/ipai/ directory not found")
        sys.exit(1)

    modules = {
        d.name
        for d in ipai_dir.iterdir()
        if d.is_dir() and not d.name.startswith((".", "__"))
    }

    print(f"✅ Found {len(modules)} actual IPAI modules in repository")
    return modules


def extract_module_refs(content: str) -> set[str]:
    """Extract all ipai_* module references from markdown content."""
    # Match complete module names in backticks, quotes, or as standalone words
    # Avoid matching:
    # - Wildcard patterns like ipai_finance_*, ipai_workos_*
    # - Incomplete names like ipai_module, ipai_all_features
    # - Text in historical sections documenting what doesn't exist

    lines = content.split("\n")
    modules = set()
    in_exclusion_section = False

    for i, line in enumerate(lines):
        # Detect exclusion section starts
        if any(
            marker in line
            for marker in [
                "Missing modules",
                "not yet implemented",
                "don't exist",
                "MISSING FROM REPO",
                "Status: ⚠️",
                "Original Plan",
                "WRONG",
                "Deprecated",
            ]
        ):
            in_exclusion_section = True

        # Detect exclusion section ends (next major heading)
        if line.startswith("##") and in_exclusion_section:
            in_exclusion_section = False

        # Skip if in exclusion section
        if in_exclusion_section:
            continue

        # Skip lines with patterns/wildcards
        if "*" in line or "pattern" in line.lower():
            continue

        # Skip lines with exclusion markers
        if "❌" in line or "N/A" in line:
            continue

        # Match complete module names
        pattern = r'[`\'"]?(ipai_[a-z0-9_]+)[`\'"]?'
        matches = re.findall(pattern, line, re.IGNORECASE)

        for match in matches:
            mod = match.lower()
            # Filter out generic/incomplete names
            if mod in ["ipai_module", "ipai_all_features", "ipai_module_backup"]:
                continue
            # Filter out wildcard suffixes
            if mod.endswith("_"):
                continue

            modules.add(mod)

    return modules


def check_file(file_path: Path, repo_modules: set[str]) -> list[tuple[str, str]]:
    """Check a single file for invalid module references."""
    try:
        content = file_path.read_text()
    except Exception as e:
        print(f"⚠️  Warning: Could not read {file_path}: {e}")
        return []

    referenced = extract_module_refs(content)
    invalid = referenced - repo_modules

    if invalid:
        return [(file_path, mod) for mod in sorted(invalid)]

    return []


def main():
    """Main validation logic."""
    print("=" * 70)
    print("IPAI Documentation Module Reference Validation")
    print("=" * 70)
    print()

    # Get actual repository modules
    repo_modules = get_repo_modules()

    # Files to check
    doc_files = [
        Path("docs/ipai/MODULE_DEPRECATION_PLAN.md"),
        Path("docs/ipai/PROFILES.md"),
        Path("docs/ipai/MODULE_EVALUATION_SUMMARY.md"),
        Path("docs/ipai/profiles/finance_prod.txt"),
        Path("docs/CANONICAL_MAP.md"),
    ]

    # Exclude MODULE_NAME_CORRECTIONS.md - it intentionally documents wrong names

    # Check each file
    all_errors = []
    for doc_file in doc_files:
        if not doc_file.exists():
            print(f"⚠️  Warning: {doc_file} not found (skipping)")
            continue

        errors = check_file(doc_file, repo_modules)
        if errors:
            all_errors.extend(errors)

    # Report results
    print()
    if all_errors:
        print("❌ VALIDATION FAILED: Found references to non-existent modules")
        print()
        print("Invalid module references:")

        # Group by file
        by_file = {}
        for file_path, module in all_errors:
            by_file.setdefault(file_path, []).append(module)

        for file_path, modules in sorted(by_file.items()):
            print(f"\n  {file_path}:")
            for mod in sorted(modules):
                print(f"    - {mod}")

        print()
        print("Action required:")
        print("  1. Verify these module names against addons/ipai/")
        print("  2. Update documentation with correct module names")
        print("  3. Run validation again")
        print()
        sys.exit(1)

    else:
        print("✅ VALIDATION PASSED: All module references are valid")
        print()
        print(f"Checked {len(doc_files)} documentation files")
        print(f"All ipai_* references match actual repository modules")
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
