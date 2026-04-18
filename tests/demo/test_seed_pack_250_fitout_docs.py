"""Pack 250 contract tests."""
from __future__ import annotations

import pathlib

import yaml

PACK_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "ssot" / "demo" / "250-fitout-docs"


def _load(name: str) -> dict:
    return yaml.safe_load((PACK_DIR / name).read_text(encoding="utf-8"))


def test_checklist_template_exists():
    templates = _load("checklist-templates.yaml")["templates"]
    assert templates, "at least one checklist template required"
    for t in templates:
        assert t.get("required_docs"), f"template {t['key']} must list required_docs"


def test_fitout_has_ready_and_blocked():
    requests = _load("fitout-requests.yaml")["requests"]
    states = {r["expected_state"] for r in requests}
    assert "ready_for_submission" in states, "fitout ready fixture missing"
    assert "collecting" in states, "fitout blocked (collecting) fixture missing"


def test_fitout_blocked_has_missing_docs_list():
    for r in _load("fitout-requests.yaml")["requests"]:
        if r["expected_state"] == "collecting":
            assert r.get("missing_docs"), f"blocked fitout {r['key']} must declare missing_docs"
            assert len(r["missing_docs"]) > 0


def test_fitout_ready_has_all_required_docs():
    templates = {t["key"]: t for t in _load("checklist-templates.yaml")["templates"]}
    for r in _load("fitout-requests.yaml")["requests"]:
        if r["expected_state"] == "ready_for_submission":
            template = templates[r["template"]]
            required = set(template["required_docs"])
            present = set(r.get("docs_present", []))
            assert required.issubset(present), \
                f"ready fitout {r['key']} missing docs: {required - present}"
