"""
Tests for individual Agent Factory SSOT file integrity.

Validates:
- YAML parsing
- Required top-level keys
- Uniqueness constraints
- Monotonic ordering
- Valid transition targets
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SSOT_DIR = REPO_ROOT / "ssot" / "agent-platform"

YAML_FILES = {
    "agent_factory": "agent_factory.yaml",
    "agent_maturity_model": "agent_maturity_model.yaml",
    "task_bus": "task_bus.yaml",
    "stage_gates": "stage_gates.yaml",
}


# -------------------------------------------------------------------------
# Parsing
# -------------------------------------------------------------------------


@pytest.mark.parametrize("filename", YAML_FILES.values())
def test_yaml_files_parse(filename):
    """All 4 YAML files parse without error."""
    path = SSOT_DIR / filename
    assert path.exists(), f"File not found: {path}"
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    assert data is not None, f"File parsed as empty: {path}"


# -------------------------------------------------------------------------
# Required Keys
# -------------------------------------------------------------------------


def test_agent_factory_required_keys(ssot_bundle):
    """agent_factory.yaml has: id, lifecycle_phases, planes, core_services."""
    doc = ssot_bundle["agent_factory"]
    for key in ("id", "lifecycle_phases", "planes", "core_services"):
        assert key in doc, f"Missing required key '{key}' in agent_factory.yaml"


def test_maturity_model_required_keys(ssot_bundle):
    """agent_maturity_model.yaml has: id, levels."""
    doc = ssot_bundle["agent_maturity_model"]
    for key in ("id", "levels"):
        assert key in doc, f"Missing required key '{key}' in agent_maturity_model.yaml"


def test_task_bus_required_keys(ssot_bundle):
    """task_bus.yaml has: id, envelope_schema, states."""
    doc = ssot_bundle["task_bus"]
    for key in ("id", "envelope_schema", "states"):
        assert key in doc, f"Missing required key '{key}' in task_bus.yaml"


def test_stage_gates_required_keys(ssot_bundle):
    """stage_gates.yaml has: id, stages."""
    doc = ssot_bundle["stage_gates"]
    for key in ("id", "stages"):
        assert key in doc, f"Missing required key '{key}' in stage_gates.yaml"


# -------------------------------------------------------------------------
# Uniqueness
# -------------------------------------------------------------------------


def test_stage_ids_unique(ssot_bundle):
    """No duplicate stage IDs in stage_gates.yaml."""
    stages = ssot_bundle["stage_gates"]["stages"]
    ids = [s["id"] for s in stages]
    assert len(ids) == len(set(ids)), f"Duplicate stage IDs found: {ids}"


def test_maturity_ids_unique(ssot_bundle):
    """No duplicate maturity level IDs in agent_maturity_model.yaml."""
    levels = ssot_bundle["agent_maturity_model"]["levels"]
    ids = [lv["id"] for lv in levels]
    assert len(ids) == len(set(ids)), f"Duplicate maturity level IDs found: {ids}"


def test_task_bus_states_unique(ssot_bundle):
    """No duplicate state IDs in task_bus.yaml."""
    states = ssot_bundle["task_bus"]["states"]
    ids = [s["id"] for s in states]
    assert len(ids) == len(set(ids)), f"Duplicate task bus state IDs found: {ids}"


# -------------------------------------------------------------------------
# Ordering
# -------------------------------------------------------------------------


def test_stage_order_monotonic(ssot_bundle):
    """Stage order values are strictly increasing."""
    stages = ssot_bundle["stage_gates"]["stages"]
    orders = [(s["id"], s["order"]) for s in stages]
    for i in range(1, len(orders)):
        prev_id, prev_order = orders[i - 1]
        curr_id, curr_order = orders[i]
        assert curr_order > prev_order, (
            f"Stage order not monotonic: {curr_id} (order={curr_order}) "
            f"<= {prev_id} (order={prev_order})"
        )


# -------------------------------------------------------------------------
# Transitions
# -------------------------------------------------------------------------


def test_task_bus_transitions_valid(ssot_bundle):
    """All transition targets in task bus exist as valid state IDs."""
    states = ssot_bundle["task_bus"]["states"]
    valid_ids = {s["id"] for s in states}
    invalid = []
    for state in states:
        transitions = state.get("transitions_to") or []
        for target in transitions:
            target_clean = target.strip()
            if target_clean not in valid_ids:
                invalid.append((state["id"], target_clean))
    assert not invalid, f"Invalid transition targets: {invalid}"
