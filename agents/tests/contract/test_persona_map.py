"""Validate persona-map.yaml entries point to real files."""
import pathlib
import yaml
import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
AGENTS_DIR = REPO_ROOT / "agents"
PERSONA_MAP = AGENTS_DIR / "ssot" / "manifests" / "persona-map.yaml"


def _load_persona_map():
    assert PERSONA_MAP.exists(), f"Missing: {PERSONA_MAP}"
    with open(PERSONA_MAP) as f:
        return yaml.safe_load(f)


def test_persona_map_exists():
    assert PERSONA_MAP.exists()


def test_persona_map_has_personas():
    data = _load_persona_map()
    assert "personas" in data
    assert isinstance(data["personas"], list)
    assert len(data["personas"]) > 0, "persona-map must contain at least one persona"


def test_all_persona_files_exist():
    data = _load_persona_map()
    missing = []
    for entry in data["personas"]:
        filepath = AGENTS_DIR / entry["file"]
        if not filepath.exists():
            missing.append(f"{entry['name']}: {entry['file']}")
    assert not missing, f"Persona files not found:\n" + "\n".join(missing)


def test_persona_entries_have_required_fields():
    data = _load_persona_map()
    required = {"name", "domain", "file"}
    for entry in data["personas"]:
        missing = required - set(entry.keys())
        assert not missing, f"Persona '{entry.get('name', '?')}' missing fields: {missing}"
