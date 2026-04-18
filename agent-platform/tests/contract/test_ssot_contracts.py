"""Contract tests — validate all SSOT YAML files load and have required keys."""

from pathlib import Path

import yaml
import pytest

_SSOT_ROOT = Path(__file__).parents[2] / "ssot"

_REQUIRED_FILES = [
    "runtime/services.yaml",
    "runtime/agents.yaml",
    "runtime/tools.yaml",
    "runtime/models.yaml",
    "runtime/environments.yaml",
    "security/auth_policy.yaml",
    "security/role_bindings.yaml",
    "security/allowed_tools.yaml",
    "eval/gates.yaml",
    "eval/scenarios.yaml",
    "eval/score_thresholds.yaml",
]


@pytest.mark.parametrize("rel_path", _REQUIRED_FILES)
def test_ssot_yaml_loads(rel_path: str) -> None:
    path = _SSOT_ROOT / rel_path
    assert path.exists(), f"SSOT file missing: {path}"
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict), f"SSOT file is not a dict: {path}"
    assert "schema_version" in data, f"Missing schema_version in {path}"
