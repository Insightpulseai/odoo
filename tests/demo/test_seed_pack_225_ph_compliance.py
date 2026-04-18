"""Pack 225 contract tests."""
from __future__ import annotations

import pathlib

import yaml

PACK_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "ssot" / "demo" / "225-ph-compliance"


def _load(name: str) -> dict:
    return yaml.safe_load((PACK_DIR / name).read_text(encoding="utf-8"))


def test_bir2307_has_ready_and_blocked():
    scenarios = _load("bir2307-scenarios.yaml")["scenarios"]
    states = {s["expected_state"] for s in scenarios}
    assert "releasable" in states, "2307 releasable fixture missing"
    assert "blocked" in states, "2307 blocked fixture missing"


def test_bir2307_blocked_lacks_final_cert():
    for s in _load("bir2307-scenarios.yaml")["scenarios"]:
        if s["expected_state"] == "blocked":
            assert s.get("final_certificate_pdf_present") is False, \
                f"blocked 2307 {s['key']} must have final_certificate_pdf_present=false"


def test_bir2307_ready_has_linked_bill_and_payment():
    for s in _load("bir2307-scenarios.yaml")["scenarios"]:
        if s["expected_state"] == "releasable":
            assert s.get("linked_vendor_bill"), f"ready 2307 {s['key']} missing linked_vendor_bill"
            assert s.get("linked_payment"), f"ready 2307 {s['key']} missing linked_payment"


def test_tin_atc_pair_exists():
    fixtures = _load("tin-atc-fixtures.yaml")["fixtures"]
    valid_states = {f["expected_valid"] for f in fixtures}
    assert True in valid_states and False in valid_states, \
        "tin-atc fixtures must include both valid and invalid cases"
