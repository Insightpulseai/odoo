#!/usr/bin/env python3
"""
Agent Factory SSOT Bundle Validator
====================================
Loads all 4 YAML files from ssot/agent-platform/ and validates:
- Structural integrity (required top-level keys)
- Cross-references between files
- Uniqueness constraints (stage IDs, maturity levels, task bus states)
- Monotonic ordering (stage order values)

Exit 0 on success, 1 on failure.
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FAIL: pyyaml is not installed. Run: pip install pyyaml")
    sys.exit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
SSOT_DIR = REPO_ROOT / "ssot" / "agent-platform"

YAML_FILES = {
    "agent_factory": "agent_factory.yaml",
    "agent_maturity_model": "agent_maturity_model.yaml",
    "task_bus": "task_bus.yaml",
    "stage_gates": "stage_gates.yaml",
}

REQUIRED_KEYS = {
    "agent_factory": ["id", "lifecycle_phases", "planes", "core_services"],
    "agent_maturity_model": ["id", "levels"],
    "task_bus": ["id", "envelope_schema", "states"],
    "stage_gates": ["id", "stages"],
}

EXPECTED_PLANES = {"control", "runtime", "artifact"}


def load_all_yamls() -> dict:
    """Load all 4 YAML files. Returns dict keyed by short name."""
    data = {}
    for key, filename in YAML_FILES.items():
        path = SSOT_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing SSOT file: {path}")
        with open(path, "r") as f:
            data[key] = yaml.safe_load(f)
    return data


def validate_required_keys(data: dict) -> list[str]:
    """Check that each file has its required top-level keys."""
    errors = []
    for key, required in REQUIRED_KEYS.items():
        doc = data[key]
        for rk in required:
            if rk not in doc:
                errors.append(f"{key}: missing required top-level key '{rk}'")
    return errors


def validate_stage_ids_unique(data: dict) -> list[str]:
    """Stage IDs in stage_gates.yaml must be unique."""
    errors = []
    stages = data["stage_gates"].get("stages", [])
    ids = [s["id"] for s in stages]
    seen = set()
    for sid in ids:
        if sid in seen:
            errors.append(f"stage_gates: duplicate stage ID '{sid}'")
        seen.add(sid)
    return errors


def validate_maturity_ids_unique(data: dict) -> list[str]:
    """Maturity level IDs must be unique."""
    errors = []
    levels = data["agent_maturity_model"].get("levels", [])
    ids = [lv["id"] for lv in levels]
    seen = set()
    for lid in ids:
        if lid in seen:
            errors.append(f"agent_maturity_model: duplicate level ID '{lid}'")
        seen.add(lid)
    return errors


def validate_task_bus_states_unique(data: dict) -> list[str]:
    """Task bus state IDs must be unique."""
    errors = []
    states = data["task_bus"].get("states", [])
    ids = [s["id"] for s in states]
    seen = set()
    for sid in ids:
        if sid in seen:
            errors.append(f"task_bus: duplicate state ID '{sid}'")
        seen.add(sid)
    return errors


def validate_stage_order_monotonic(data: dict) -> list[str]:
    """Stage order values must be strictly increasing."""
    errors = []
    stages = data["stage_gates"].get("stages", [])
    orders = [(s["id"], s["order"]) for s in stages]
    for i in range(1, len(orders)):
        prev_id, prev_order = orders[i - 1]
        curr_id, curr_order = orders[i]
        if curr_order <= prev_order:
            errors.append(
                f"stage_gates: order not monotonic at {curr_id} "
                f"(order {curr_order} <= {prev_order} of {prev_id})"
            )
    return errors


def validate_task_bus_transitions(data: dict) -> list[str]:
    """All transition targets in task bus must be valid state IDs."""
    errors = []
    states = data["task_bus"].get("states", [])
    valid_ids = {s["id"] for s in states}
    for state in states:
        transitions = state.get("transitions_to", [])
        if transitions is None:
            continue
        for target in transitions:
            # Strip inline comments (YAML may parse them, but be safe)
            target_clean = target.strip()
            if target_clean not in valid_ids:
                errors.append(
                    f"task_bus: state '{state['id']}' transitions to "
                    f"unknown state '{target_clean}'"
                )
    return errors


def validate_maturity_allowed_stages(data: dict) -> list[str]:
    """Every stage in maturity model allowed_stages must exist in stage_gates."""
    errors = []
    stages = data["stage_gates"].get("stages", [])
    valid_stage_ids = {s["id"] for s in stages}
    levels = data["agent_maturity_model"].get("levels", [])
    for level in levels:
        allowed = level.get("allowed_stages", [])
        for stage_id in allowed:
            if stage_id not in valid_stage_ids:
                errors.append(
                    f"agent_maturity_model: level '{level['id']}' references "
                    f"unknown stage '{stage_id}' in allowed_stages"
                )
    return errors


def validate_stage_feeds_into(data: dict) -> list[str]:
    """Every stage's feeds_into must reference an existing stage ID (or null)."""
    errors = []
    stages = data["stage_gates"].get("stages", [])
    valid_ids = {s["id"] for s in stages}
    for stage in stages:
        feeds_into = stage.get("feeds_into")
        if feeds_into is not None and feeds_into not in valid_ids:
            errors.append(
                f"stage_gates: stage '{stage['id']}' feeds_into "
                f"unknown stage '{feeds_into}'"
            )
    return errors


def validate_plane_names(data: dict) -> list[str]:
    """Plane names in agent_factory must match expected set."""
    errors = []
    planes = data["agent_factory"].get("planes", {})
    actual = set(planes.keys())
    if actual != EXPECTED_PLANES:
        missing = EXPECTED_PLANES - actual
        extra = actual - EXPECTED_PLANES
        if missing:
            errors.append(f"agent_factory: missing planes: {missing}")
        if extra:
            errors.append(f"agent_factory: unexpected planes: {extra}")
    return errors


def validate_core_services_specs(data: dict) -> list[str]:
    """Any spec: reference in core_services must point to an existing YAML file."""
    errors = []
    services = data["agent_factory"].get("core_services", [])
    for svc in services:
        spec_ref = svc.get("spec")
        if spec_ref:
            spec_path = SSOT_DIR / spec_ref
            if not spec_path.exists():
                errors.append(
                    f"agent_factory: core_service '{svc['id']}' references "
                    f"spec '{spec_ref}' which does not exist at {spec_path}"
                )
    return errors


def validate_maturity_stages_coverage(data: dict) -> list[str]:
    """Union of all maturity allowed_stages should cover all stage IDs
    (retirement stages S14-S16 may be excluded)."""
    warnings = []
    stages = data["stage_gates"].get("stages", [])
    all_stage_ids = {s["id"] for s in stages}
    # Retirement stages that may legitimately be excluded
    retirement_ids = {"S14", "S15", "S16"}
    required_ids = all_stage_ids - retirement_ids

    levels = data["agent_maturity_model"].get("levels", [])
    covered = set()
    for level in levels:
        covered.update(level.get("allowed_stages", []))

    uncovered = required_ids - covered
    if uncovered:
        warnings.append(
            f"agent_maturity_model: stages not covered by any maturity level: "
            f"{sorted(uncovered)} (non-retirement stages)"
        )
    return warnings


def main():
    print("=" * 60)
    print("Agent Factory SSOT Bundle Validator")
    print("=" * 60)
    print()

    # Load files
    try:
        data = load_all_yamls()
        print(f"PASS  Loaded {len(data)} YAML files from {SSOT_DIR}")
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"FAIL  {e}")
        sys.exit(1)

    # Run all validations
    all_errors = []
    all_warnings = []
    checks = [
        ("required_keys", validate_required_keys),
        ("stage_ids_unique", validate_stage_ids_unique),
        ("maturity_ids_unique", validate_maturity_ids_unique),
        ("task_bus_states_unique", validate_task_bus_states_unique),
        ("stage_order_monotonic", validate_stage_order_monotonic),
        ("task_bus_transitions", validate_task_bus_transitions),
        ("maturity_allowed_stages", validate_maturity_allowed_stages),
        ("stage_feeds_into", validate_stage_feeds_into),
        ("plane_names", validate_plane_names),
        ("core_services_specs", validate_core_services_specs),
    ]

    warning_checks = [
        ("maturity_stages_coverage", validate_maturity_stages_coverage),
    ]

    for name, check_fn in checks:
        errors = check_fn(data)
        if errors:
            all_errors.extend(errors)
            for e in errors:
                print(f"FAIL  [{name}] {e}")
        else:
            print(f"PASS  [{name}]")

    for name, check_fn in warning_checks:
        warnings = check_fn(data)
        if warnings:
            all_warnings.extend(warnings)
            for w in warnings:
                print(f"WARN  [{name}] {w}")
        else:
            print(f"PASS  [{name}]")

    # Summary
    print()
    print("-" * 60)
    total_checks = len(checks) + len(warning_checks)
    passed = total_checks - len([c for c, fn in checks if fn(data)]) - len(
        [c for c, fn in warning_checks if fn(data)]
    )
    print(f"checks={total_checks} passed={passed} errors={len(all_errors)} warnings={len(all_warnings)}")

    if all_errors:
        print("STATUS=FAIL")
        sys.exit(1)
    else:
        print("STATUS=PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
