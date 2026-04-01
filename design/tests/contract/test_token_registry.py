"""Validate design token registry SSOT."""
import yaml
from pathlib import Path


def test_token_registry_loads():
    path = Path(__file__).parent.parent.parent / "ssot" / "tokens" / "token-registry.yaml"
    assert path.exists(), f"Missing: {path}"
    with open(path) as f:
        data = yaml.safe_load(f)
    assert "sources" in data, "token-registry.yaml must have 'sources' key"
    assert "schema" in data, "token-registry.yaml must have 'schema' key"


def test_token_schema_exists():
    schema = Path(__file__).parent.parent.parent / "schema.tokens.json"
    assert schema.exists(), f"Missing token schema: {schema}"
