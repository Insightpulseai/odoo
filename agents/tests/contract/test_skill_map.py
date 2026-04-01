"""Validate skill-map.yaml structure and file references."""
import pathlib
import yaml
import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
AGENTS_DIR = REPO_ROOT / "agents"
SKILL_MAP = AGENTS_DIR / "ssot" / "manifests" / "skill-map.yaml"


def _load_skill_map():
    assert SKILL_MAP.exists(), f"Missing: {SKILL_MAP}"
    with open(SKILL_MAP) as f:
        return yaml.safe_load(f)


def test_skill_map_exists():
    assert SKILL_MAP.exists()


def test_skill_map_parses():
    data = _load_skill_map()
    assert "skills" in data
    assert isinstance(data["skills"], list)


def test_skill_entries_have_required_fields():
    """Validate structure of any registered skills."""
    data = _load_skill_map()
    if not data["skills"]:
        pytest.skip("No skills registered yet")
    required = {"name", "domain", "file"}
    for entry in data["skills"]:
        missing = required - set(entry.keys())
        assert not missing, f"Skill '{entry.get('name', '?')}' missing fields: {missing}"


def test_all_skill_files_exist():
    """Validate that referenced skill files exist."""
    data = _load_skill_map()
    if not data["skills"]:
        pytest.skip("No skills registered yet")
    missing = []
    for entry in data["skills"]:
        filepath = AGENTS_DIR / entry["file"]
        if not filepath.exists():
            missing.append(f"{entry['name']}: {entry['file']}")
    assert not missing, f"Skill files not found:\n" + "\n".join(missing)
