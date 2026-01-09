#!/usr/bin/env python3
"""
Spec Kit Validation Script
Validates spec bundle structure and content quality
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Required files in each spec bundle
REQUIRED_FILES = ["constitution.md", "prd.md", "plan.md", "tasks.md"]

# Minimum non-empty, non-heading lines
MIN_CONTENT_LINES = 10

# Placeholder patterns to flag
PLACEHOLDER_PATTERNS = [
    "TODO",
    "TBD",
    "PLACEHOLDER",
    "FILL ME IN",
    "LOREM IPSUM",
    "COMING SOON",
]


def validate_spec_bundle(spec_dir: Path) -> Tuple[bool, List[str]]:
    """
    Validate a single spec bundle directory.
    Returns: (is_valid, error_messages)
    """
    errors = []
    spec_name = spec_dir.name

    print(f"Validating spec bundle: {spec_name}")

    # Check required files exist
    for file_name in REQUIRED_FILES:
        file_path = spec_dir / file_name
        if not file_path.exists():
            errors.append(f"Missing required file: {file_path}")
            continue

        # Check file is not empty
        if file_path.stat().st_size == 0:
            errors.append(f"Empty file: {file_path}")
            continue

        # Check minimum content (non-empty, non-heading lines)
        content = file_path.read_text(encoding="utf-8")
        non_empty_lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

        if len(non_empty_lines) < MIN_CONTENT_LINES:
            errors.append(
                f"{file_path}: Too few content lines ({len(non_empty_lines)} < {MIN_CONTENT_LINES})"
            )

        # Check for placeholder patterns (warning level)
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern in content.upper():
                print(
                    f"  WARNING: {file_path} contains placeholder text: {pattern}"
                )

    # Validate constitution.md specific requirements
    constitution_path = spec_dir / "constitution.md"
    if constitution_path.exists():
        content = constitution_path.read_text(encoding="utf-8")
        if "## Non-Negotiable Rules" not in content:
            errors.append(
                f"{constitution_path}: Missing '## Non-Negotiable Rules' section"
            )

    # Validate tasks.md has checkboxes
    tasks_path = spec_dir / "tasks.md"
    if tasks_path.exists():
        content = tasks_path.read_text(encoding="utf-8")
        if "[ ]" not in content and "[x]" not in content:
            print(
                f"  WARNING: {tasks_path} has no task checkboxes ([ ] or [x])"
            )

    return len(errors) == 0, errors


def main():
    """Main validation routine"""
    repo_root = Path(__file__).parent.parent
    spec_dir = repo_root / "spec"

    if not spec_dir.exists():
        print(f"ERROR: spec/ directory not found at {spec_dir}")
        sys.exit(1)

    # Find all spec bundles (directories with constitution.md)
    spec_bundles = [
        d
        for d in spec_dir.iterdir()
        if d.is_dir() and (d / "constitution.md").exists()
    ]

    if not spec_bundles:
        print("WARNING: No spec bundles found (no constitution.md files)")
        sys.exit(0)

    print(f"Found {len(spec_bundles)} spec bundle(s)")
    print()

    all_valid = True
    all_errors = []

    for bundle in sorted(spec_bundles):
        is_valid, errors = validate_spec_bundle(bundle)
        if not is_valid:
            all_valid = False
            all_errors.extend(errors)
        print()

    # Summary
    if all_valid:
        print("✓ All spec bundles are valid")
        sys.exit(0)
    else:
        print(f"✗ Validation failed with {len(all_errors)} error(s):")
        for error in all_errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
