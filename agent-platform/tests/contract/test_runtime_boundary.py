"""Test runtime-boundary.yaml contract integrity."""
import pathlib
import yaml
import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
BOUNDARY_FILE = REPO_ROOT / "agent-platform" / "ssot" / "runtime" / "runtime-boundary.yaml"

REQUIRED_FIELDS = {"owns", "does_not_own", "decision_rule"}


def _load_boundary():
    assert BOUNDARY_FILE.exists(), f"Missing: {BOUNDARY_FILE}"
    with open(BOUNDARY_FILE) as f:
        return yaml.safe_load(f)


def test_boundary_file_exists():
    assert BOUNDARY_FILE.exists()


def test_required_fields_present():
    data = _load_boundary()
    missing = REQUIRED_FIELDS - set(data.keys())
    assert not missing, f"Missing required fields: {missing}"


def test_owns_is_nonempty_list():
    data = _load_boundary()
    assert isinstance(data["owns"], list)
    assert len(data["owns"]) > 0


def test_does_not_own_is_nonempty_list():
    data = _load_boundary()
    assert isinstance(data["does_not_own"], list)
    assert len(data["does_not_own"]) > 0


def test_no_overlap_between_owns_and_does_not_own():
    data = _load_boundary()
    overlap = set(data["owns"]) & set(data["does_not_own"])
    assert not overlap, f"Overlap: {overlap}"


def test_decision_rule_is_string():
    data = _load_boundary()
    assert isinstance(data["decision_rule"], str)
    assert len(data["decision_rule"]) > 5
