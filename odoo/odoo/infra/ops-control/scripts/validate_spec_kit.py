#!/usr/bin/env python3
"""
Spec Kit Validator

Validates that all Spec Kit bundles contain required files and meet structure requirements.
Run this as part of CI to enforce Spec Kit compliance.

Usage:
    python3 scripts/validate_spec_kit.py

Exit codes:
    0 - All Spec Kits valid
    1 - Validation failed
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

REQUIRED_FILES = ["constitution.md", "prd.md", "plan.md", "tasks.md"]
MIN_FILE_SIZE = 40  # minimum characters to consider file non-empty

def fail(msg: str) -> None:
    """Print error message and exit with code 1."""
    print(f"[SPEC-KIT] ❌ FAIL: {msg}", file=sys.stderr)
    sys.exit(1)

def warn(msg: str) -> None:
    """Print warning message."""
    print(f"[SPEC-KIT] ⚠️  WARN: {msg}")

def success(msg: str) -> None:
    """Print success message."""
    print(f"[SPEC-KIT] ✅ {msg}")

def check_file_exists(bundle_path: Path, filename: str) -> bool:
    """Check if required file exists in bundle."""
    file_path = bundle_path / filename
    if not file_path.exists():
        fail(f"Missing {file_path.as_posix()}")
    return True

def check_file_content(bundle_path: Path, filename: str) -> bool:
    """Check if file has meaningful content."""
    file_path = bundle_path / filename
    try:
        content = file_path.read_text(encoding="utf-8").strip()
        if len(content) < MIN_FILE_SIZE:
            fail(f"{file_path.as_posix()} looks empty or too short (< {MIN_FILE_SIZE} chars)")
        return True
    except Exception as e:
        fail(f"Error reading {file_path.as_posix()}: {e}")

def check_prd_acceptance_criteria(bundle_path: Path) -> bool:
    """Check that PRD contains acceptance criteria section."""
    prd_path = bundle_path / "prd.md"
    try:
        content = prd_path.read_text(encoding="utf-8").lower()
        if "acceptance" not in content:
            fail(f"{prd_path.as_posix()} must include acceptance criteria section")
        return True
    except Exception as e:
        fail(f"Error reading {prd_path.as_posix()}: {e}")

def check_constitution_principles(bundle_path: Path) -> bool:
    """Check that constitution contains core principles."""
    const_path = bundle_path / "constitution.md"
    try:
        content = const_path.read_text(encoding="utf-8").lower()
        if "principle" not in content and "tenet" not in content:
            warn(f"{const_path.as_posix()} should include core principles or tenets")
        return True
    except Exception as e:
        fail(f"Error reading {const_path.as_posix()}: {e}")

def check_plan_phases(bundle_path: Path) -> bool:
    """Check that plan contains implementation phases."""
    plan_path = bundle_path / "plan.md"
    try:
        content = plan_path.read_text(encoding="utf-8").lower()
        if "phase" not in content and "milestone" not in content:
            warn(f"{plan_path.as_posix()} should include phases or milestones")
        return True
    except Exception as e:
        fail(f"Error reading {plan_path.as_posix()}: {e}")

def check_tasks_breakdown(bundle_path: Path) -> bool:
    """Check that tasks file contains actual task breakdown."""
    tasks_path = bundle_path / "tasks.md"
    try:
        content = tasks_path.read_text(encoding="utf-8")
        # Count task items (lines starting with - [ ] or - [x])
        task_lines = [line for line in content.split('\n') if line.strip().startswith('- [')]
        if len(task_lines) < 3:
            warn(f"{tasks_path.as_posix()} should contain multiple tasks (found {len(task_lines)})")
        return True
    except Exception as e:
        fail(f"Error reading {tasks_path.as_posix()}: {e}")

def validate_bundle(bundle_path: Path) -> bool:
    """Validate a single Spec Kit bundle."""
    bundle_name = bundle_path.name
    print(f"\n[SPEC-KIT] Validating bundle: {bundle_name}")
    
    # Check required files exist
    for filename in REQUIRED_FILES:
        check_file_exists(bundle_path, filename)
    
    # Check file content
    for filename in REQUIRED_FILES:
        check_file_content(bundle_path, filename)
    
    # Check specific file requirements
    check_prd_acceptance_criteria(bundle_path)
    check_constitution_principles(bundle_path)
    check_plan_phases(bundle_path)
    check_tasks_breakdown(bundle_path)
    
    success(f"Bundle '{bundle_name}' is valid")
    return True

def find_spec_bundles(spec_dir: Path) -> List[Path]:
    """Find all Spec Kit bundles in spec/ directory."""
    if not spec_dir.exists():
        fail("Missing spec/ directory")
    
    bundles = [p for p in spec_dir.iterdir() if p.is_dir() and not p.name.startswith('.')]
    
    if not bundles:
        fail("No Spec Kit bundles found under spec/<slug>/")
    
    return bundles

def main() -> None:
    """Main validation function."""
    print("[SPEC-KIT] Starting Spec Kit validation...")
    
    # Find spec directory
    spec_dir = Path("spec")
    
    # Find all bundles
    bundles = find_spec_bundles(spec_dir)
    print(f"[SPEC-KIT] Found {len(bundles)} bundle(s) to validate")
    
    # Validate each bundle
    for bundle_path in bundles:
        validate_bundle(bundle_path)
    
    # Final success message
    print(f"\n[SPEC-KIT] ✅ All {len(bundles)} bundle(s) passed validation!")
    print("[SPEC-KIT] Spec Kit compliance verified.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[SPEC-KIT] Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[SPEC-KIT] ❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
