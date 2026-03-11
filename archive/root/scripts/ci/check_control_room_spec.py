#!/usr/bin/env python3
from __future__ import annotations

"""Validate the control-room-platform spec bundle.

Checks:
  - All 4 required files exist: constitution.md, prd.md, plan.md, tasks.md
  - Each file contains the required section headers
  - tasks.md contains at least one task item (checkbox line)

Exit 0 on pass, exit 1 on fail.
Uses only stdlib -- no pip dependencies.
"""

import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_DIR = os.path.join(REPO_ROOT, "spec", "control-room-platform")

REQUIRED_FILES = ["constitution.md", "prd.md", "plan.md", "tasks.md"]

# Required sections (case-insensitive substring match against # headings)
REQUIRED_SECTIONS = {
    "constitution.md": ["purpose", "non-negotiables", "boundaries"],
    "prd.md": ["problem", "users", ("functional requirements", "use cases")],
    "plan.md": [("phases", "rollout")],
    "tasks.md": [],  # validated separately via checkbox pattern
}

TASK_PATTERN = re.compile(r"^\s*-\s+\[([ xX])\]", re.MULTILINE)


def extract_headings(content: str) -> list[str]:
    """Return lowercase text of all markdown headings (any level)."""
    headings: list[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            # Remove leading # characters and whitespace
            heading_text = stripped.lstrip("#").strip().lower()
            headings.append(heading_text)
    return headings


def check_section_present(headings: list[str], requirement) -> bool:
    """Check if a required section is present in the headings list.

    ``requirement`` is either a single string or a tuple of alternatives
    (any one match satisfies the check).
    """
    if isinstance(requirement, tuple):
        alternatives = requirement
    else:
        alternatives = (requirement,)

    for alt in alternatives:
        alt_lower = alt.lower()
        for heading in headings:
            if alt_lower in heading:
                return True
    return False


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    # ------------------------------------------------------------------
    # 1. Check directory exists
    # ------------------------------------------------------------------
    if not os.path.isdir(SPEC_DIR):
        errors.append(f"Spec directory missing: {SPEC_DIR}")
        # Cannot continue; all file checks would fail
        _report(errors, warnings)
        return 1

    # ------------------------------------------------------------------
    # 2. Check all required files exist
    # ------------------------------------------------------------------
    existing_files: list[str] = []
    for fname in REQUIRED_FILES:
        fpath = os.path.join(SPEC_DIR, fname)
        if not os.path.isfile(fpath):
            errors.append(f"Required file missing: spec/control-room-platform/{fname}")
        else:
            existing_files.append(fname)

    # ------------------------------------------------------------------
    # 3. Validate required sections in each existing file
    # ------------------------------------------------------------------
    for fname in existing_files:
        fpath = os.path.join(SPEC_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as exc:
            errors.append(f"Cannot read {fname}: {exc}")
            continue

        if not content.strip():
            errors.append(f"{fname} is empty")
            continue

        headings = extract_headings(content)

        # Check heading-based sections
        for req in REQUIRED_SECTIONS.get(fname, []):
            if not check_section_present(headings, req):
                if isinstance(req, tuple):
                    label = " or ".join(f'"{r}"' for r in req)
                else:
                    label = f'"{req}"'
                errors.append(
                    f"{fname}: missing required section heading containing {label}"
                )

        # Special check for tasks.md -- must have checkbox items
        if fname == "tasks.md":
            matches = TASK_PATTERN.findall(content)
            if not matches:
                errors.append(
                    f"tasks.md: no task items found (expected lines like '- [ ] ...' or '- [x] ...')"
                )
            else:
                total = len(matches)
                done = sum(1 for m in matches if m.lower() == "x")
                warnings.append(
                    f"tasks.md: {done}/{total} tasks completed"
                )

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    return _report(errors, warnings)


def _report(errors: list[str], warnings: list[str]) -> int:
    print("=" * 60)
    print("Control Room Spec Bundle Validator")
    print("=" * 60)

    if warnings:
        for w in warnings:
            print(f"  INFO: {w}")

    if errors:
        print()
        for e in errors:
            print(f"  FAIL: {e}")
        print()
        print(f"Result: FAILED ({len(errors)} error(s))")
        print("=" * 60)
        return 1

    print()
    print("  All spec bundle checks passed.")
    print()
    print("Result: PASSED")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
