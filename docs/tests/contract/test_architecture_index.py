"""Validate architecture index SSOT."""
import yaml
from pathlib import Path


def test_architecture_index_loads():
    path = Path(__file__).parent.parent.parent / "ssot" / "indexes" / "architecture-index.yaml"
    assert path.exists()
    with open(path) as f:
        data = yaml.safe_load(f)
    assert "documents" in data
