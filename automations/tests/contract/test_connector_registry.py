"""Validates connector-registry.yaml is valid YAML with expected schema."""
import pathlib
import yaml

REGISTRY_PATH = pathlib.Path(__file__).parents[2] / "ssot" / "connectors" / "connector-registry.yaml"


def test_registry_exists():
    assert REGISTRY_PATH.exists(), f"Missing: {REGISTRY_PATH}"


def test_registry_valid_yaml():
    data = yaml.safe_load(REGISTRY_PATH.read_text())
    assert isinstance(data, dict), "Registry must be a YAML mapping"


def test_registry_has_connectors_key():
    data = yaml.safe_load(REGISTRY_PATH.read_text())
    assert "connectors" in data, "Registry must have a 'connectors' key"
    assert isinstance(data["connectors"], list), "'connectors' must be a list"


def test_connector_entries_have_required_fields():
    data = yaml.safe_load(REGISTRY_PATH.read_text())
    required = {"name", "type", "auth_method", "module_path"}
    for entry in data["connectors"]:
        missing = required - set(entry.keys())
        assert not missing, f"Connector '{entry.get('name', '?')}' missing fields: {missing}"
