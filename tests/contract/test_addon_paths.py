"""Validate canonical addon path structure."""
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def test_oca_addons_dir_exists():
    assert (REPO_ROOT / "addons" / "oca").exists() or (REPO_ROOT / "addons" / "oca").is_symlink(), \
        "addons/oca/ must exist"


def test_ipai_addons_dir_exists():
    assert (REPO_ROOT / "addons" / "ipai").exists(), "addons/ipai/ must exist"


def test_config_envs_exist():
    for env in ["dev", "staging", "prod"]:
        config_dir = REPO_ROOT / "config" / env
        assert config_dir.exists(), f"config/{env}/ must exist"
