#!/usr/bin/env python3
"""
Validate Spec Kit structure for all spec bundles.

Each spec/<slug>/ must contain:
- constitution.md
- prd.md
- plan.md
- tasks.md

Exit codes:
- 0: All spec bundles valid
- 1: Missing spec/ directory
- 2: Validation failures found
"""

import os
import sys
import glob

REQUIRED_FILES = {"constitution.md", "prd.md", "plan.md", "tasks.md"}
MIN_LINES = 10  # Minimum non-empty, non-heading lines


def count_content_lines(filepath: str) -> int:
    """Count non-empty, non-heading lines in a file."""
    count = 0
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                # Skip empty lines and markdown headings
                if stripped and not stripped.startswith("#"):
                    count += 1
    except Exception:
        return 0
    return count


def check_placeholders(filepath: str) -> list:
    """Check for placeholder text in file."""
    placeholders = []
    patterns = ["TODO", "TBD", "PLACEHOLDER", "FILL ME IN", "LOREM IPSUM"]
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().upper()
            for pattern in patterns:
                if pattern in content:
                    placeholders.append(pattern)
    except Exception:
        pass
    return placeholders


def validate_spec_bundle(slug_path: str) -> tuple:
    """
    Validate a single spec bundle.

    Returns:
        (is_valid: bool, errors: list, warnings: list)
    """
    errors = []
    warnings = []
    slug_name = os.path.basename(slug_path)

    files = set(os.listdir(slug_path))
    missing = sorted(list(REQUIRED_FILES - files))

    if missing:
        errors.append(f"Missing files: {', '.join(missing)}")

    for req_file in REQUIRED_FILES:
        filepath = os.path.join(slug_path, req_file)
        if not os.path.exists(filepath):
            continue

        # Check minimum content
        content_lines = count_content_lines(filepath)
        if content_lines < MIN_LINES:
            errors.append(
                f"{req_file}: Only {content_lines} content lines (minimum {MIN_LINES})"
            )

        # Check for placeholders
        placeholders = check_placeholders(filepath)
        if placeholders:
            warnings.append(f"{req_file}: Contains placeholders: {', '.join(placeholders)}")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def main() -> int:
    base = "spec"

    if not os.path.isdir(base):
        print("Missing spec/ directory")
        return 1

    # Find all spec bundles (directories with constitution.md)
    slugs = []
    for path in glob.glob(f"{base}/*"):
        if os.path.isdir(path):
            # Only consider directories that should be spec bundles
            # (have at least one of the required files)
            files = set(os.listdir(path))
            if files & REQUIRED_FILES:
                slugs.append(path)

    if not slugs:
        print("No spec/<slug>/ bundles found with required files")
        return 1

    all_valid = True
    results = []

    for slug_path in sorted(slugs):
        slug_name = os.path.basename(slug_path)
        is_valid, errors, warnings = validate_spec_bundle(slug_path)

        if not is_valid:
            all_valid = False
            print(f"[FAIL] {slug_path}")
            for error in errors:
                print(f"       - {error}")
        else:
            print(f"[OK] {slug_path}")

        for warning in warnings:
            print(f"       [WARN] {warning}")

        results.append({
            "slug": slug_name,
            "path": slug_path,
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
        })

    # Summary
    valid_count = sum(1 for r in results if r["valid"])
    total_count = len(results)
    print(f"\nSummary: {valid_count}/{total_count} spec bundles valid")

    return 0 if all_valid else 2


if __name__ == "__main__":
    sys.exit(main())
