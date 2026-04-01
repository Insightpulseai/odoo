"""Validate route registry SSOT."""
import yaml
from pathlib import Path


def test_route_registry_loads():
    path = Path(__file__).parent.parent.parent / "ssot" / "routes" / "route-registry.yaml"
    assert path.exists(), f"Missing: {path}"
    with open(path) as f:
        data = yaml.safe_load(f)
    assert "routes" in data, "route-registry.yaml must have 'routes' key"
