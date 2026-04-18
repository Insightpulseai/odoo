"""Pack 200 contract tests."""
from __future__ import annotations

import pathlib

import yaml

PACK_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "ssot" / "demo" / "200-finance"


def _load(name: str) -> dict:
    return yaml.safe_load((PACK_DIR / name).read_text(encoding="utf-8"))


def test_invoices_are_not_auto_posted():
    for inv in _load("invoices-draft.yaml")["invoices"]:
        assert inv["state"] == "draft", f"invoice {inv['key']} must be draft, got {inv['state']}"


def test_vendor_bills_are_not_auto_posted():
    for bill in _load("vendor-bills.yaml")["bills"]:
        assert bill["state"] == "draft", f"bill {bill['key']} must be draft, got {bill['state']}"


def test_intercompany_has_ready_and_blocked_pair():
    scenarios = _load("intercompany-scenarios.yaml")["scenarios"]
    states = {s["expected_state"] for s in scenarios}
    assert "ready_for_draft" in states, "ic ready fixture missing"
    assert "blocked" in states, "ic blocked fixture missing"


def test_intercompany_blocked_has_missing_support():
    for s in _load("intercompany-scenarios.yaml")["scenarios"]:
        if s["expected_state"] == "blocked":
            assert s.get("missing_attachments"), f"blocked ic {s['key']} must declare missing_attachments"
            assert s.get("blocker_reason"), f"blocked ic {s['key']} must declare blocker_reason"
