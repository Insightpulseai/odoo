"""Validates schedule-registry.yaml is valid YAML with expected schema."""
import pathlib
import yaml
import pytest

REGISTRY_PATH = pathlib.Path(__file__).parents[2] / "ssot" / "schedules" / "schedule-registry.yaml"


def test_registry_exists():
    assert REGISTRY_PATH.exists(), f"Missing: {REGISTRY_PATH}"


def test_registry_valid_yaml():
    data = yaml.safe_load(REGISTRY_PATH.read_text())
    assert isinstance(data, dict), "Registry must be a YAML mapping"


def test_registry_has_schedules_key():
    data = yaml.safe_load(REGISTRY_PATH.read_text())
    assert "schedules" in data, "Registry must have a 'schedules' key"
    assert isinstance(data["schedules"], list), "'schedules' must be a list"


def test_schedule_entries_have_required_fields():
    data = yaml.safe_load(REGISTRY_PATH.read_text())
    required = {"name", "trigger", "category", "handler", "enabled"}
    for entry in data["schedules"]:
        missing = required - set(entry.keys())
        assert not missing, f"Schedule '{entry.get('name', '?')}' missing fields: {missing}"
