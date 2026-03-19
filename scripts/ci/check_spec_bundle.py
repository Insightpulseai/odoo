#!/usr/bin/env python3
import pathlib
import sys

REQUIRED_SPEC_FILES = {
    "constitution.md",
    "prd.md",
    "plan.md",
    "tasks.md"
}

def check_spec_bundles():
    repo_root = pathlib.Path(__file__).parent.parent.parent
    spec_dir = repo_root / "spec"
    violations = []

    if not spec_dir.exists():
        print("No spec/ directory found. Skipping check.")
        sys.exit(0)

    for bundle_dir in spec_dir.iterdir():
        if bundle_dir.is_dir():
            files_in_bundle = {f.name for f in bundle_dir.iterdir() if f.is_file()}
            missing_files = REQUIRED_SPEC_FILES - files_in_bundle
            extra_files = files_in_bundle - REQUIRED_SPEC_FILES

            if missing_files:
                violations.append(f"Bundle '{bundle_dir.name}' is missing required files: {missing_files}")
            if extra_files:
                violations.append(f"Bundle '{bundle_dir.name}' contains unauthorized files: {extra_files}")

    if violations:
        print("Spec Kit Consistency Violations:")
        for v in violations:
            print(v)
        sys.exit(1)
    else:
        print("Spec Kit Consistency Check Passed.")
        sys.exit(0)

if __name__ == "__main__":
    check_spec_bundles()
