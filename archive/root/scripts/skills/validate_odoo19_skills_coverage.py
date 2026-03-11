#!/usr/bin/env python3
"""
validate_odoo19_skills_coverage.py
Validates that the repository contains all the Odoo 19 application skills
defined in the SSOT (ssot/odoo/odoo19_app_skills_map.yaml).
"""

import sys
import json
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.resolve()
SSOT_PATH = REPO_ROOT / "ssot" / "odoo" / "odoo19_app_skills_map.yaml"
SKILLS_DIR = REPO_ROOT / "skills"


def main():
    if not SSOT_PATH.exists():
        print(f"Error: SSOT file not found at {SSOT_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(SSOT_PATH) as f:
        ssot = yaml.safe_load(f)

    expected_skills = {}
    for group, apps in ssot.get("expected", {}).items():
        for app, paths in apps.items():
            for p in paths:
                expected_skills[p] = f"{group}.{app}"

    missing_skills = []
    found_skills = []

    for skill_path, _ in expected_skills.items():
        full_path = SKILLS_DIR / skill_path
        if full_path.exists() and full_path.is_dir():
            found_skills.append(skill_path)
        else:
            missing_skills.append(skill_path)

    # Extra skills (optional to check all, but keeping simple for this validation)
    # We just focus on whether the expected ones are present.

    total = len(expected_skills)
    found = len(found_skills)
    coverage = (found / total * 100) if total > 0 else 100

    summary = {
        "total_expected": total,
        "found": found,
        "missing": len(missing_skills),
        "coverage_percentage": round(coverage, 2),
        "missing_skills": missing_skills,
    }

    print(json.dumps(summary, indent=2))

    if missing_skills:
        print(
            "\n[FAIL] Missing required skills defined in SSOT. Please create stub directories for them.",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        print("\n[OK] All expected skills are present.", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
