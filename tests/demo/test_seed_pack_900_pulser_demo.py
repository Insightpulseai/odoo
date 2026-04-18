"""Pack 900 contract tests — Pulser scenarios must reference lower packs."""
from __future__ import annotations

import pathlib

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DEMO_DIR = REPO_ROOT / "ssot" / "demo"
PACK_DIR = DEMO_DIR / "900-pulser-demo"


def _load(path: pathlib.Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _collect_lower_pack_keys() -> set[str]:
    keys: set[str] = set()
    lower_packs = ("100-system-shared", "200-finance", "225-ph-compliance", "250-fitout-docs")
    for pack in lower_packs:
        for yaml_file in (DEMO_DIR / pack).glob("*.yaml"):
            if yaml_file.name == "manifest.yaml":
                continue
            payload = _load(yaml_file)
            if not isinstance(payload, dict):
                continue
            top = next(iter(payload.values())) if payload else []
            if isinstance(top, list):
                for row in top:
                    if isinstance(row, dict) and "key" in row:
                        keys.add(row["key"])
    return keys


def test_every_pulser_scenario_references_lower_pack_record():
    lower_keys = _collect_lower_pack_keys()
    scenarios = _load(PACK_DIR / "pulser-scenarios.yaml")["scenarios"]
    for s in scenarios:
        source = s.get("source_record")
        assert source in lower_keys, \
            f"pulser scenario {s['key']} references unknown lower-pack key {source!r}"


def test_every_scenario_has_allowed_and_forbidden_actions():
    for s in _load(PACK_DIR / "pulser-scenarios.yaml")["scenarios"]:
        assert s.get("allowed_actions"), f"scenario {s['key']} missing allowed_actions"
        assert s.get("forbidden_actions"), f"scenario {s['key']} missing forbidden_actions"
        assert not (set(s["allowed_actions"]) & set(s["forbidden_actions"])), \
            f"scenario {s['key']} has action in both allowed and forbidden"


def test_blocked_scenarios_never_allow_terminal_actions():
    terminal_actions = {
        "post_invoice",
        "release_2307_without_validation",
        "mark_fitout_complete_without_documents",
    }
    for s in _load(PACK_DIR / "pulser-scenarios.yaml")["scenarios"]:
        if s["expected_ready_state"] == "blocked":
            overlap = terminal_actions & set(s.get("allowed_actions", []))
            assert not overlap, \
                f"blocked scenario {s['key']} must not allow terminal action(s): {overlap}"


def test_demo_routes_reference_scenarios():
    scenario_keys = {s["key"] for s in _load(PACK_DIR / "pulser-scenarios.yaml")["scenarios"]}
    for route in _load(PACK_DIR / "demo-routes.yaml")["routes"]:
        for scen in route.get("scenarios", []):
            assert scen in scenario_keys, \
                f"demo route {route['key']} references unknown scenario {scen!r}"


def test_eval_fixtures_reference_prompt_fixtures():
    prompt_keys = {p["key"] for p in _load(PACK_DIR / "prompt-fixtures.yaml")["prompts"]}
    for ev in _load(PACK_DIR / "eval-fixtures.yaml")["evals"]:
        for p in ev.get("prompts", []):
            assert p in prompt_keys, \
                f"eval {ev['key']} references unknown prompt {p!r}"
