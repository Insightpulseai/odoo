"""
Tests for cross-file consistency of the Agent Factory SSOT bundle.

Validates:
- Maturity model allowed_stages reference valid stage IDs
- Stage coverage across maturity levels
- Core service spec references point to existing files
- Stage gate feeds_into chains
- Plane name consistency
"""

from pathlib import Path


# -------------------------------------------------------------------------
# Maturity <-> Stage Gates
# -------------------------------------------------------------------------


def test_maturity_allowed_stages_exist(ssot_bundle):
    """Every stage in maturity model allowed_stages exists in stage_gates.yaml."""
    stages = ssot_bundle["stage_gates"]["stages"]
    valid_stage_ids = {s["id"] for s in stages}
    levels = ssot_bundle["agent_maturity_model"]["levels"]
    invalid = []
    for level in levels:
        for stage_id in level.get("allowed_stages", []):
            if stage_id not in valid_stage_ids:
                invalid.append((level["id"], stage_id))
    assert not invalid, (
        f"Maturity levels reference unknown stage IDs: {invalid}"
    )


def test_maturity_stages_cover_all_stages(ssot_bundle):
    """Union of all maturity allowed_stages covers S01-S16.

    Retirement stages (S14-S16) may be excluded since they represent
    post-lifecycle phases not governed by maturity levels.
    """
    stages = ssot_bundle["stage_gates"]["stages"]
    all_stage_ids = {s["id"] for s in stages}
    # S14 (optimize), S15 (deprecate), S16 (decommission) are retirement stages
    retirement_ids = {"S14", "S15", "S16"}
    required_ids = all_stage_ids - retirement_ids

    levels = ssot_bundle["agent_maturity_model"]["levels"]
    covered = set()
    for level in levels:
        covered.update(level.get("allowed_stages", []))

    uncovered = required_ids - covered
    assert not uncovered, (
        f"Non-retirement stages not covered by any maturity level: "
        f"{sorted(uncovered)}"
    )


# -------------------------------------------------------------------------
# Core Services -> Spec Files
# -------------------------------------------------------------------------


def test_factory_services_reference_valid_specs(ssot_bundle, ssot_dir):
    """Any spec: reference in core_services points to an existing YAML file."""
    services = ssot_bundle["agent_factory"].get("core_services", [])
    missing = []
    for svc in services:
        spec_ref = svc.get("spec")
        if spec_ref:
            spec_path = ssot_dir / spec_ref
            if not spec_path.exists():
                missing.append((svc["id"], spec_ref, str(spec_path)))
    assert not missing, (
        f"Core services reference non-existent spec files: {missing}"
    )


# -------------------------------------------------------------------------
# Stage Gate Chain
# -------------------------------------------------------------------------


def test_stage_gates_chain(ssot_bundle):
    """Every stage's feeds_into references an existing stage ID (except terminal)."""
    stages = ssot_bundle["stage_gates"]["stages"]
    valid_ids = {s["id"] for s in stages}
    broken = []
    for stage in stages:
        feeds_into = stage.get("feeds_into")
        if feeds_into is not None and feeds_into not in valid_ids:
            broken.append((stage["id"], feeds_into))
    assert not broken, (
        f"Stage feeds_into references unknown stage IDs: {broken}"
    )


# -------------------------------------------------------------------------
# Plane Names
# -------------------------------------------------------------------------


def test_plane_names_consistent(ssot_bundle):
    """Plane names in agent_factory.yaml match expected set."""
    expected = {"control", "runtime", "artifact"}
    actual = set(ssot_bundle["agent_factory"].get("planes", {}).keys())
    assert actual == expected, (
        f"Plane names mismatch. Expected: {expected}, Got: {actual}. "
        f"Missing: {expected - actual}, Extra: {actual - expected}"
    )
