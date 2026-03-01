#!/usr/bin/env python3
"""
validate_skills_registry.py
CI validator for ssot/agents/skills.yaml

Usage:
    python3 scripts/ci/validate_skills_registry.py [--ssot-path PATH]

Exit codes:
    0 — PASS (registry is valid)
    1 — FAIL (schema errors found)

Failure mode: CI.SKILLS_REGISTRY_INVALID
Runbook:      docs/runbooks/failures/CI.SKILLS_REGISTRY_INVALID.md
"""

import sys
import argparse
from pathlib import Path

# ── Try to import PyYAML (available in ubuntu-latest GH runners) ──────────
try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# Schema definition (inline — no external jsonschema dep required)
# ─────────────────────────────────────────────────────────────────────────────

VALID_EXECUTORS      = {"vercel_sandbox", "do_runner"}
VALID_STATES         = {"PLAN", "PATCH", "VERIFY", "PR"}
VALID_STATUSES       = {"active", "deprecated", "experimental"}
REQUIRED_SKILL_KEYS  = {"id", "name", "description", "executor", "max_duration_s",
                        "tags", "state_machine", "owner", "status"}

def validate_skill(skill: dict, index: int) -> list[str]:
    """Return list of error messages for a single skill entry."""
    errors = []
    prefix = f"skills[{index}]"

    # Required keys
    for key in REQUIRED_SKILL_KEYS:
        if key not in skill:
            errors.append(f"{prefix}.{key}: required field missing")

    if errors:  # stop early — remaining checks need the fields
        return errors

    # id: non-empty snake_case
    sid = skill["id"]
    if not isinstance(sid, str) or not sid.strip():
        errors.append(f"{prefix}.id: must be a non-empty string")
    elif not __import__("re").match(r"^[a-z][a-z0-9-]+$", sid):
        errors.append(f"{prefix}.id: must match ^[a-z][a-z0-9-]+$ (got '{sid}')")

    # name
    if not isinstance(skill["name"], str) or not skill["name"].strip():
        errors.append(f"{prefix}.name: must be a non-empty string")

    # executor
    if skill["executor"] not in VALID_EXECUTORS:
        errors.append(
            f"{prefix}.executor: must be one of {sorted(VALID_EXECUTORS)}"
            f" (got '{skill['executor']}')"
        )

    # max_duration_s
    mds = skill["max_duration_s"]
    if not isinstance(mds, int) or mds < 1 or mds > 3600:
        errors.append(f"{prefix}.max_duration_s: must be integer 1–3600 (got {mds!r})")

    # tags
    if not isinstance(skill["tags"], list):
        errors.append(f"{prefix}.tags: must be a list")

    # state_machine
    sm = skill["state_machine"]
    if not isinstance(sm, list) or len(sm) == 0:
        errors.append(f"{prefix}.state_machine: must be a non-empty list")
    else:
        for j, state in enumerate(sm):
            if state not in VALID_STATES:
                errors.append(
                    f"{prefix}.state_machine[{j}]: '{state}' is not one of "
                    f"{sorted(VALID_STATES)}"
                )
        # Order must be a subsequence of PLAN→PATCH→VERIFY→PR
        canonical_order = ["PLAN", "PATCH", "VERIFY", "PR"]
        last_idx = -1
        for state in sm:
            if state in canonical_order:
                idx = canonical_order.index(state)
                if idx <= last_idx:
                    errors.append(
                        f"{prefix}.state_machine: states must appear in order "
                        f"PLAN→PATCH→VERIFY→PR (got {sm})"
                    )
                    break
                last_idx = idx

    # status
    if skill["status"] not in VALID_STATUSES:
        errors.append(
            f"{prefix}.status: must be one of {sorted(VALID_STATUSES)}"
            f" (got '{skill['status']}')"
        )

    # owner
    if not isinstance(skill["owner"], str) or not skill["owner"].strip():
        errors.append(f"{prefix}.owner: must be a non-empty string")

    return errors


def validate_registry(path: Path) -> int:
    """Validate the registry YAML. Returns exit code."""
    if not path.exists():
        print(f"ERROR: {path} not found")
        return 1

    with path.open() as f:
        try:
            doc = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"ERROR: YAML parse error in {path}: {e}")
            return 1

    if not isinstance(doc, dict):
        print(f"ERROR: {path} must be a YAML mapping at the top level")
        return 1

    skills = doc.get("skills")
    if not isinstance(skills, list) or len(skills) == 0:
        print(f"ERROR: {path} must contain a non-empty 'skills' list")
        return 1

    all_errors: list[str] = []
    ids_seen: set[str] = set()

    for i, skill in enumerate(skills):
        if not isinstance(skill, dict):
            all_errors.append(f"skills[{i}]: must be a mapping")
            continue

        # Duplicate ID check
        sid = skill.get("id")
        if sid and sid in ids_seen:
            all_errors.append(f"skills[{i}].id: duplicate id '{sid}'")
        elif sid:
            ids_seen.add(sid)

        all_errors.extend(validate_skill(skill, i))

    if all_errors:
        print(f"FAIL: ssot/agents/skills.yaml schema validation failed")
        print(f"      Failure mode: CI.SKILLS_REGISTRY_INVALID")
        print(f"      Runbook:      docs/runbooks/failures/CI.SKILLS_REGISTRY_INVALID.md")
        print()
        for err in all_errors:
            print(f"  {err}")
        print(f"\n{len(all_errors)} error(s) found in {len(skills)} skill(s)")
        return 1

    print(f"PASS: {len(skills)} skill(s) validated in {path}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ssot-path",
        default="ssot/agents/skills.yaml",
        help="Path to skills YAML (default: ssot/agents/skills.yaml)",
    )
    args = parser.parse_args()
    sys.exit(validate_registry(Path(args.ssot_path)))


if __name__ == "__main__":
    main()
