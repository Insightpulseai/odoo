"""Validates all template dirs in the catalog have at least one template file."""
import pathlib
import yaml
import pytest

REPO_ROOT = pathlib.Path(__file__).parents[3]
CATALOG_PATH = REPO_ROOT / "templates" / "ssot" / "catalog" / "template-catalog.yaml"


def test_catalog_exists():
    assert CATALOG_PATH.exists(), f"Missing: {CATALOG_PATH}"


def test_catalog_valid_yaml():
    data = yaml.safe_load(CATALOG_PATH.read_text())
    assert isinstance(data, dict), "Catalog must be a YAML mapping"
    assert "templates" in data, "Catalog must have a 'templates' key"


def _get_templates():
    data = yaml.safe_load(CATALOG_PATH.read_text())
    return data.get("templates", [])


@pytest.mark.parametrize(
    "template",
    _get_templates(),
    ids=lambda t: t.get("name", "unknown"),
)
def test_template_dir_has_content(template):
    tpl_dir = REPO_ROOT / template["path"]
    assert tpl_dir.exists(), f"Template dir missing: {template['path']}"
    files = [f for f in tpl_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
    assert len(files) >= 1, f"Template dir '{template['path']}' has no template files"
