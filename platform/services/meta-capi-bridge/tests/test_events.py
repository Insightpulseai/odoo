"""Tests for canonical event → CAPI payload transformation."""

import hashlib
import time

from meta_capi_bridge.events import _hash_pii, to_capi_payload


def test_hash_pii_lowercases_and_strips():
    assert _hash_pii("  Test@Example.COM  ") == hashlib.sha256(b"test@example.com").hexdigest()


def test_lead_created_event():
    event = {
        "event_type": "lead_created",
        "event_id": "lead-001",
        "timestamp": 1711900000,
        "user": {
            "email": "buyer@example.com",
            "phone": "+639171234567",
            "first_name": "Juan",
            "last_name": "Dela Cruz",
        },
        "source_url": "https://erp.insightpulseai.com/crm/lead/1",
    }
    payload = to_capi_payload(event)

    assert payload["event_name"] == "Lead"
    assert payload["event_id"] == "lead-001"
    assert payload["event_time"] == 1711900000
    assert payload["action_source"] == "system_generated"
    assert payload["event_source_url"] == "https://erp.insightpulseai.com/crm/lead/1"
    assert "em" in payload["user_data"]
    assert "ph" in payload["user_data"]
    assert "fn" in payload["user_data"]
    assert "ln" in payload["user_data"]


def test_invoice_paid_with_value():
    event = {
        "event_type": "invoice_paid",
        "event_id": "inv-042",
        "user": {"email": "customer@test.com"},
        "custom_data": {
            "value": 15000.50,
            "currency": "php",
            "order_id": "SO-2026-042",
        },
    }
    payload = to_capi_payload(event)

    assert payload["event_name"] == "Purchase"
    assert payload["custom_data"]["value"] == 15000.50
    assert payload["custom_data"]["currency"] == "PHP"
    assert payload["custom_data"]["order_id"] == "SO-2026-042"


def test_lead_qualified_adds_marker():
    event = {
        "event_type": "lead_qualified",
        "event_id": "qual-001",
        "user": {"email": "prospect@example.com"},
    }
    payload = to_capi_payload(event)

    assert payload["event_name"] == "Lead"
    assert payload["custom_data"]["lead_event_source"] == "qualified"


def test_opportunity_won():
    event = {
        "event_type": "opportunity_won",
        "event_id": "opp-099",
        "user": {"email": "winner@corp.com"},
        "custom_data": {"value": 250000, "currency": "USD"},
    }
    payload = to_capi_payload(event)
    assert payload["event_name"] == "Purchase"


def test_default_timestamp_is_recent():
    event = {
        "event_type": "lead_created",
        "event_id": "ts-test",
        "user": {},
    }
    payload = to_capi_payload(event)
    assert abs(payload["event_time"] - int(time.time())) < 5


def test_client_identifiers_not_hashed():
    event = {
        "event_type": "lead_created",
        "event_id": "client-id-test",
        "user": {
            "email": "test@test.com",
            "client_ip": "203.0.113.42",
            "user_agent": "Mozilla/5.0",
            "fbc": "fb.1.123.abc",
            "fbp": "fb.1.456.def",
        },
    }
    payload = to_capi_payload(event)
    ud = payload["user_data"]

    # These should be plain, not hashed
    assert ud["client_ip_address"] == "203.0.113.42"
    assert ud["client_user_agent"] == "Mozilla/5.0"
    assert ud["fbc"] == "fb.1.123.abc"
    assert ud["fbp"] == "fb.1.456.def"
    # Email should be hashed
    assert ud["em"] != ["test@test.com"]
