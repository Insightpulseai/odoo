#!/usr/bin/env python3
"""
Release Workflow Contract Gate

Regex-validates that .github/workflows/cd-production.yml and
.github/workflows/ship-on-deploy.yml contain required release-contract
integration points:

  1. build_release_manifest.py is invoked
  2. release_manifest.json is attached to the GitHub release
  3. Manifest generation does not silently swallow failures (warning)

Exit 0 = pass, exit 1 = contract violation.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

WORKFLOWS = {
    "cd-production": REPO_ROOT / ".github" / "workflows" / "cd-production.yml",
    "ship-on-deploy": REPO_ROOT / ".github" / "workflows" / "ship-on-deploy.yml",
}

# --- Required patterns (hard fail if missing) ---

REQUIRED_CHECKS: list[dict] = [
    {
        "id": "manifest_script_invoked",
        "description": "build_release_manifest.py is invoked",
        "pattern": re.compile(r"build_release_manifest\.py"),
        "workflows": ["cd-production", "ship-on-deploy"],
    },
    {
        "id": "manifest_json_attached",
        "description": "release_manifest.json is attached to release",
        "pattern": re.compile(r"release_manifest\.json"),
        "workflows": ["cd-production", "ship-on-deploy"],
    },
]

# --- Advisory checks (warn but do not fail) ---

ADVISORY_CHECKS: list[dict] = [
    {
        "id": "manifest_fail_suppressed",
        "description": "Manifest generation uses '|| echo' (best-effort, not hard-fail)",
        "pattern": re.compile(
            r"build_release_manifest\.py.*?\|\|\s*echo\s+[\"']WARNING",
            re.DOTALL,
        ),
        "workflows": ["cd-production", "ship-on-deploy"],
        "advisory": "Consider removing '|| echo WARNING...' to make manifest generation a hard gate.",
    },
    {
        "id": "gates_report_missing",
        "description": "gates_report.json not referenced (future enhancement)",
        "pattern": re.compile(r"gates_report\.json"),
        "workflows": ["cd-production"],
        "invert": True,  # warn when pattern is NOT found
        "advisory": "gates_report.json is not yet generated. Add gate report artifact in a future PR.",
    },
]


def load_workflow(name: str) -> str | None:
    path = WORKFLOWS[name]
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    # Load all workflows
    contents: dict[str, str | None] = {}
    for name in WORKFLOWS:
        contents[name] = load_workflow(name)
        if contents[name] is None:
            errors.append(f"Workflow file missing: {WORKFLOWS[name]}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1

    # Required checks (hard fail)
    for check in REQUIRED_CHECKS:
        for wf_name in check["workflows"]:
            text = contents[wf_name]
            if text is None:
                continue
            if not check["pattern"].search(text):
                errors.append(
                    f"[{wf_name}] Missing: {check['description']} "
                    f"(id={check['id']})"
                )

    # Advisory checks (warn only)
    for check in ADVISORY_CHECKS:
        for wf_name in check["workflows"]:
            text = contents[wf_name]
            if text is None:
                continue
            found = bool(check["pattern"].search(text))
            invert = check.get("invert", False)
            # For inverted checks, warn when NOT found
            # For normal checks, warn when found
            should_warn = (not found) if invert else found
            if should_warn:
                warnings.append(
                    f"[{wf_name}] Advisory: {check['description']} — "
                    f"{check.get('advisory', '')}"
                )

    # Report
    if warnings:
        print(f"WARN: {len(warnings)} advisory finding(s):")
        for w in warnings:
            print(f"  - {w}")
        print()

    if errors:
        print(f"FAIL: {len(errors)} contract violation(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    req_count = sum(len(c["workflows"]) for c in REQUIRED_CHECKS)
    print(
        f"PASS: release workflow contract ({req_count} required checks, "
        f"{len(warnings)} advisory)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
