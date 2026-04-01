"""Validate all environment config YAML files parse correctly."""
import pathlib
import yaml
import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
CONFIGS_DIR = REPO_ROOT / "agent-platform" / "configs"

EXPECTED_ENVS = {"dev", "staging", "prod"}
REQUIRED_TOP_KEYS = {"environment", "api", "orchestrator", "executor"}


def _find_runtime_configs():
    configs = {}
    for env_dir in CONFIGS_DIR.iterdir():
        if env_dir.is_dir() and not env_dir.name.startswith("."):
            runtime_file = env_dir / "runtime.yaml"
            if runtime_file.exists():
                configs[env_dir.name] = runtime_file
    return configs


def test_all_expected_envs_have_configs():
    configs = _find_runtime_configs()
    missing = EXPECTED_ENVS - set(configs.keys())
    assert not missing, f"Missing config for environments: {missing}"


def test_all_configs_parse():
    configs = _find_runtime_configs()
    failures = []
    for env_name, filepath in configs.items():
        try:
            with open(filepath) as f:
                yaml.safe_load(f)
        except yaml.YAMLError as exc:
            failures.append(f"{env_name}: {exc}")
    assert not failures, f"YAML parse failures:\n" + "\n".join(failures)


def test_all_configs_have_required_keys():
    configs = _find_runtime_configs()
    failures = []
    for env_name, filepath in configs.items():
        with open(filepath) as f:
            data = yaml.safe_load(f)
        missing = REQUIRED_TOP_KEYS - set(data.keys())
        if missing:
            failures.append(f"{env_name} missing keys: {missing}")
    assert not failures, "\n".join(failures)
