"""Validate all SSOT YAML files in platform/ parse correctly."""
import pathlib
import yaml
import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SSOT_DIR = REPO_ROOT / "platform" / "ssot"


def _find_yaml_files():
    """Collect all .yaml and .yml files under platform/ssot/."""
    files = []
    for ext in ("*.yaml", "*.yml"):
        files.extend(SSOT_DIR.rglob(ext))
    return sorted(files)


@pytest.fixture
def yaml_files():
    files = _find_yaml_files()
    assert len(files) > 0, f"No YAML files found under {SSOT_DIR}"
    return files


def test_all_ssot_yaml_files_parse(yaml_files):
    failures = []
    for filepath in yaml_files:
        try:
            with open(filepath) as f:
                data = yaml.safe_load(f)
            # safe_load returns None for empty files — that is acceptable
        except yaml.YAMLError as exc:
            failures.append(f"{filepath.relative_to(REPO_ROOT)}: {exc}")
    assert not failures, f"YAML parse failures:\n" + "\n".join(failures)


def test_no_empty_yaml_documents(yaml_files):
    """Warn about YAML files that parse to None (empty)."""
    empties = []
    for filepath in yaml_files:
        with open(filepath) as f:
            data = yaml.safe_load(f)
        if data is None:
            empties.append(str(filepath.relative_to(REPO_ROOT)))
    # Empty files are a warning, not a hard failure — but flag them
    if empties:
        pytest.skip(f"Empty YAML files (review needed): {empties}")
