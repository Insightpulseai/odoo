#!/usr/bin/env python3
"""Check spec bundle completeness -- every spec/<slug>/ must have 4 files."""
import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_DIR = REPO_ROOT / "spec"

REQUIRED_FILES = {"constitution.md", "prd.md", "plan.md", "tasks.md"}


def main():
    parser = argparse.ArgumentParser(description="Check spec bundle completeness")
    parser.add_argument("--strict", action="store_true",
                        help="Fail on incomplete bundles (default: warn-only)")
    args = parser.parse_args()

    if not SPEC_DIR.exists():
        print("SKIP: spec/ directory not found")
        return 0

    errors = []
    bundles = sorted(
        d for d in SPEC_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )

    if not bundles:
        print("SKIP: No spec bundles found")
        return 0

    for bundle in bundles:
        existing = {f.name for f in bundle.iterdir() if f.is_file()}
        missing = REQUIRED_FILES - existing
        if missing:
            errors.append(f"{bundle.name}: missing {', '.join(sorted(missing))}")

    if errors:
        mode = "FAIL" if args.strict else "WARN"
        print(f"{mode}: {len(errors)} spec bundle(s) incomplete:")
        for e in errors:
            print(f"  - {e}")
        return 1 if args.strict else 0

    print(f"PASS: {len(bundles)} spec bundle(s) complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
