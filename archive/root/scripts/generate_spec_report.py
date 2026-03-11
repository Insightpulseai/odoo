#!/usr/bin/env python3
"""
Generate Spec Bundle Report
Creates summary report of all spec bundles with validation status
"""

import sys
from pathlib import Path
from datetime import datetime


def count_lines(file_path: Path) -> tuple:
    """Count total lines, non-empty lines, and content lines"""
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    non_empty = [l for l in lines if l.strip()]
    content_lines = [l for l in non_empty if not l.strip().startswith("#")]
    return len(lines), len(non_empty), len(content_lines)


def main():
    """Generate spec bundle report"""
    repo_root = Path(__file__).parent.parent
    spec_dir = repo_root / "spec"

    print("=" * 80)
    print("SPEC KIT VALIDATION REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().isoformat()}")
    print()

    # Find all spec bundles
    spec_bundles = [
        d for d in spec_dir.iterdir() if d.is_dir() and (d / "constitution.md").exists()
    ]

    if not spec_bundles:
        print("No spec bundles found")
        sys.exit(0)

    print(f"Total Spec Bundles: {len(spec_bundles)}")
    print()

    for bundle in sorted(spec_bundles):
        print(f"Spec Bundle: {bundle.name}")
        print("-" * 80)

        required_files = ["constitution.md", "prd.md", "plan.md", "tasks.md"]
        all_present = True

        for file_name in required_files:
            file_path = bundle / file_name
            if file_path.exists():
                total, non_empty, content = count_lines(file_path)
                status = "✓" if content >= 10 else "✗"
                print(
                    f"  {status} {file_name:20} {total:4} lines ({content:3} content lines)"
                )
                if content < 10:
                    all_present = False
            else:
                print(f"  ✗ {file_name:20} MISSING")
                all_present = False

        # Check for additional files
        additional = [
            f.name
            for f in bundle.iterdir()
            if f.is_file()
            and f.name not in required_files
            and not f.name.startswith(".")
        ]
        if additional:
            print(f"  Additional files: {', '.join(additional)}")

        print(f"  Overall: {'VALID' if all_present else 'INVALID'}")
        print()

    print("=" * 80)


if __name__ == "__main__":
    main()
