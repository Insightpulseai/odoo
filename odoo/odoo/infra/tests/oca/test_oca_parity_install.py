"""
Tests for scripts/oca/oca_parity_install.py

Run:  pytest tests/oca/test_oca_parity_install.py -v
CI:   No live Odoo required — all XML-RPC calls are mocked.

Conventions:
  - Uses importlib to load the script directly (no __init__.py in scripts/)
  - All XML-RPC calls patched via mock_xmlrpc fixture
  - Canonical manifest/allowlist tests use real files from repo
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Load the module under test via importlib (scripts/ has no __init__.py)
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = REPO_ROOT / "scripts" / "oca" / "oca_parity_install.py"

_spec = importlib.util.spec_from_file_location("oca_parity_install", _SCRIPT_PATH)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["oca_parity_install"] = _mod
_spec.loader.exec_module(_mod)

# Import public API for convenience
detect_runtime = _mod.detect_runtime
get_connection_defaults = _mod.get_connection_defaults
load_manifest = _mod.load_manifest
load_allowlist = _mod.load_allowlist
all_wave_numbers = _mod.all_wave_numbers
discover_modules = _mod.discover_modules
check_against_allowlist = _mod.check_against_allowlist
install_chunk = _mod.install_chunk
get_installed_modules = _mod.get_installed_modules
_connect = _mod._connect
load_state = _mod.load_state
save_state = _mod.save_state
check_prerequisites = _mod.check_prerequisites
run_selftest = _mod.run_selftest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def minimal_manifest(tmp_path) -> Path:
    """2-wave YAML manifest with 3 modules total."""
    content = """\
waves:
  - wave: 1
    name: "Test Wave 1"
    risk: low
    modules:
      - name: mod_a
      - name: mod_b
  - wave: 2
    name: "Test Wave 2"
    risk: medium
    modules:
      - name: mod_c
"""
    p = tmp_path / "install_manifest.yaml"
    p.write_text(content)
    return p


@pytest.fixture
def minimal_allowlist(tmp_path) -> Path:
    """Allowlist YAML with 3 module names."""
    content = """\
oca_modules:
  - mod_a
  - mod_b
  - mod_c
"""
    p = tmp_path / "oca_installed_allowlist.yaml"
    p.write_text(content)
    return p


@pytest.fixture
def mock_xmlrpc():
    """Patch xmlrpc.client.ServerProxy for the loaded module."""
    with patch("oca_parity_install.xmlrpc.client.ServerProxy") as mock_proxy:
        common = MagicMock()
        common.authenticate.return_value = 1  # valid uid
        models = MagicMock()
        models.execute_kw.return_value = []
        mock_proxy.side_effect = lambda url: common if "common" in url else models
        yield common, models


# ---------------------------------------------------------------------------
# Runtime detection tests
# ---------------------------------------------------------------------------

def test_detect_runtime_local(monkeypatch):
    """Returns 'local' when no sentinel files exist."""
    monkeypatch.setattr("pathlib.Path.exists", lambda self: False)
    assert detect_runtime() == "local"


def test_detect_runtime_docker(monkeypatch):
    """Returns 'docker' when /.dockerenv sentinel file exists."""
    monkeypatch.setattr(
        "pathlib.Path.exists",
        lambda self: str(self) in ("/.dockerenv", "/run/.containerenv"),
    )
    assert detect_runtime() == "docker"


# ---------------------------------------------------------------------------
# Manifest loading tests
# ---------------------------------------------------------------------------

def test_load_manifest_happy_path(minimal_manifest):
    """load_manifest() returns dict with 2 waves."""
    manifest = load_manifest(minimal_manifest)
    assert isinstance(manifest, dict)
    assert "waves" in manifest
    assert len(manifest["waves"]) == 2


def test_load_manifest_missing_file(tmp_path):
    """load_manifest() raises FileNotFoundError for missing path."""
    with pytest.raises(FileNotFoundError):
        load_manifest(tmp_path / "nonexistent.yaml")


# ---------------------------------------------------------------------------
# Allowlist loading tests
# ---------------------------------------------------------------------------

def test_load_allowlist_returns_set(minimal_allowlist):
    """load_allowlist() returns a set of module names."""
    result = load_allowlist(minimal_allowlist)
    assert isinstance(result, set)
    assert len(result) == 3
    assert "mod_a" in result
    assert "mod_c" in result


# ---------------------------------------------------------------------------
# Module discovery tests
# ---------------------------------------------------------------------------

def test_discover_modules_flat_list(minimal_manifest):
    """discover_modules() returns flat list of length 3."""
    manifest = load_manifest(minimal_manifest)
    modules = discover_modules(manifest)
    assert isinstance(modules, list)
    assert len(modules) == 3
    assert "mod_a" in modules
    assert "mod_b" in modules
    assert "mod_c" in modules


# ---------------------------------------------------------------------------
# Allowlist partitioning tests
# ---------------------------------------------------------------------------

def test_check_against_allowlist_partitions_correctly():
    """check_against_allowlist() partitions confirmed=[A,B], unconfirmed=[C]."""
    allowlist = {"mod_a", "mod_b"}
    modules = ["mod_a", "mod_b", "mod_c"]
    result = check_against_allowlist(modules, allowlist)
    assert result["confirmed"] == ["mod_a", "mod_b"]
    assert result["unconfirmed"] == ["mod_c"]


# ---------------------------------------------------------------------------
# install_chunk tests
# ---------------------------------------------------------------------------

def test_install_chunk_dry_run_no_subprocess():
    """install_chunk(dry_run=True) returns True without calling subprocess.run."""
    with patch("oca_parity_install.subprocess.run") as mock_run:
        result = install_chunk(["base", "mail"], "testdb", dry_run=True)
    assert result is True
    mock_run.assert_not_called()


# ---------------------------------------------------------------------------
# XML-RPC helper tests
# ---------------------------------------------------------------------------

def test_get_installed_modules_filters_installed_state(mock_xmlrpc):
    """get_installed_modules() calls search_read with 'installed' state filter."""
    common, models = mock_xmlrpc
    models.execute_kw.return_value = [
        {"name": "base", "installed_version": "19.0.1.0.0"},
    ]
    result = get_installed_modules("odoo", "pwd", 1, models, ["base", "mail"])
    assert "base" in result
    assert result["base"] == "19.0.1.0.0"
    assert models.execute_kw.called


def test_connect_exits_on_auth_failure(monkeypatch):
    """_connect() calls sys.exit(1) when authenticate returns falsy uid."""
    monkeypatch.setenv("ODOO_PASSWORD", "wrong_password")

    with patch("oca_parity_install.xmlrpc.client.ServerProxy") as mock_proxy:
        common = MagicMock()
        common.authenticate.return_value = 0  # authentication failure
        mock_proxy.return_value = common

        with pytest.raises(SystemExit) as exc_info:
            _connect()
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# State management tests
# ---------------------------------------------------------------------------

def test_load_state_returns_empty_dict_when_missing(tmp_path):
    """load_state() returns {} when state file does not exist."""
    absent = tmp_path / "nonexistent_state.json"
    result = load_state(path=absent)
    assert result == {}


def test_save_and_reload_state_roundtrip(tmp_path):
    """save_state() → load_state() preserves data exactly."""
    state_path = tmp_path / "state.json"
    data = {"mod_a": "installed", "mod_b": "failed"}
    save_state(data, path=state_path)
    reloaded = load_state(path=state_path)
    assert reloaded == data


# ---------------------------------------------------------------------------
# check_prerequisites tests
# ---------------------------------------------------------------------------

def test_check_prerequisites_no_password(monkeypatch):
    """check_prerequisites() returns error containing 'ODOO_PASSWORD' when unset."""
    monkeypatch.delenv("ODOO_PASSWORD", raising=False)

    class _Args:
        dry_run = False
        selftest = False
        status = False
        verify = False

    errors = check_prerequisites(_Args())
    assert len(errors) > 0
    assert any("ODOO_PASSWORD" in e for e in errors)


def test_check_prerequisites_dry_run_skips_password(monkeypatch):
    """check_prerequisites() returns no errors when --dry-run is set."""
    monkeypatch.delenv("ODOO_PASSWORD", raising=False)

    class _Args:
        dry_run = True
        selftest = False
        status = False
        verify = False

    errors = check_prerequisites(_Args())
    assert errors == []


# ---------------------------------------------------------------------------
# Selftest mode
# ---------------------------------------------------------------------------

def test_selftest_mode_exits_zero(capsys):
    """run_selftest() returns 0 when canonical manifest + allowlist are present."""
    result = run_selftest()
    captured = capsys.readouterr()
    # Should report all tests passed
    assert result == 0, f"selftest failed:\n{captured.out}"
    assert "9/9 tests passed" in captured.out


# ---------------------------------------------------------------------------
# Canonical file tests (real repo files)
# ---------------------------------------------------------------------------

def test_canonical_manifest_loads():
    """Real docs/oca/install_manifest.yaml loads with 4 waves."""
    manifest = load_manifest()  # uses MANIFEST_PATH default
    assert isinstance(manifest, dict)
    assert "waves" in manifest
    assert len(manifest["waves"]) == 4


def test_canonical_allowlist_loads():
    """Real odoo/ssot/oca_installed_allowlist.yaml has >= 100 modules."""
    allowlist = load_allowlist()  # uses ALLOWLIST_PATH default
    assert isinstance(allowlist, set)
    assert len(allowlist) >= 100


def test_all_manifest_modules_in_allowlist():
    """Policy gate: every module in install_manifest.yaml is in the allowlist."""
    manifest = load_manifest()
    allowlist = load_allowlist()
    modules = discover_modules(manifest)
    partitioned = check_against_allowlist(modules, allowlist)

    unconfirmed = partitioned["unconfirmed"]
    assert unconfirmed == [], (
        f"Policy violation: {len(unconfirmed)} manifest module(s) not in allowlist:\n"
        + "\n".join(f"  - {m}" for m in unconfirmed)
    )
