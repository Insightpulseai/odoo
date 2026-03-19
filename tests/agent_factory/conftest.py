"""Shared fixtures for Agent Factory SSOT tests."""

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


@pytest.fixture(scope="session")
def ssot_bundle() -> dict:
    """Load all 4 Agent Factory SSOT YAML files into a dict keyed by short name."""
    data = {}
    for key, filename in YAML_FILES.items():
        path = SSOT_DIR / filename
        with open(path, "r") as f:
            data[key] = yaml.safe_load(f)
    return data


@pytest.fixture(scope="session")
def ssot_dir() -> Path:
    """Return the SSOT directory path."""
    return SSOT_DIR
