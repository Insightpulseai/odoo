"""Live integration test — sends a test event to Meta CAPI.

Requires:
  - META_PIXEL_ID, META_ACCESS_TOKEN, META_APP_SECRET env vars
  - META_TEST_EVENT_CODE set (sandboxed, not production)

Run:
  META_PIXEL_ID=... META_ACCESS_TOKEN=... META_APP_SECRET=... META_TEST_EVENT_CODE=TEST_CAPI_IPAI \
    python -m pytest tests/test_live_capi.py -v -s
"""

import os
import uuid

import pytest

from meta_capi_bridge.client import send_events
from meta_capi_bridge.events import to_capi_payload


LIVE = all(
    os.environ.get(k)
    for k in ("META_PIXEL_ID", "META_ACCESS_TOKEN", "META_APP_SECRET")
)

pytestmark = pytest.mark.skipif(not LIVE, reason="Live Meta secrets not set")


def test_live_lead_event():
    """Fire a test Lead event and verify Meta accepts it."""
    event = {
        "event_type": "lead_created",
        "event_id": f"test-{uuid.uuid4().hex[:12]}",
        "user": {
            "email": "test-integration@insightpulseai.com",
            "first_name": "Test",
            "last_name": "Runner",
            "country_code": "PH",
        },
        "source_url": "https://erp.insightpulseai.com/crm/lead/test",
        "custom_data": {
            "content_name": "CAPI Integration Test",
        },
    }
    payload = to_capi_payload(event)
    result = send_events([payload], test_event_code="TEST_CAPI_IPAI")

    assert result.get("events_received") == 1, f"Unexpected response: {result}"
    print(f"\n  Meta accepted event: events_received={result['events_received']}")


def test_live_purchase_event():
    """Fire a test Purchase event with value/currency."""
    event = {
        "event_type": "invoice_paid",
        "event_id": f"test-{uuid.uuid4().hex[:12]}",
        "user": {
            "email": "buyer-test@insightpulseai.com",
            "phone": "+639170000000",
        },
        "custom_data": {
            "value": 12500.00,
            "currency": "PHP",
            "order_id": f"SO-TEST-{uuid.uuid4().hex[:8]}",
        },
    }
    payload = to_capi_payload(event)
    result = send_events([payload], test_event_code="TEST_CAPI_IPAI")

    assert result.get("events_received") == 1, f"Unexpected response: {result}"
    print(f"\n  Meta accepted Purchase event: events_received={result['events_received']}")


def test_live_batch_events():
    """Fire a batch of mixed events."""
    events = [
        {
            "event_type": "lead_created",
            "event_id": f"batch-lead-{uuid.uuid4().hex[:8]}",
            "user": {"email": "batch1@test.com"},
        },
        {
            "event_type": "lead_qualified",
            "event_id": f"batch-qual-{uuid.uuid4().hex[:8]}",
            "user": {"email": "batch2@test.com"},
        },
        {
            "event_type": "opportunity_won",
            "event_id": f"batch-won-{uuid.uuid4().hex[:8]}",
            "user": {"email": "batch3@test.com"},
            "custom_data": {"value": 50000, "currency": "PHP"},
        },
    ]
    payloads = [to_capi_payload(e) for e in events]
    result = send_events(payloads, test_event_code="TEST_CAPI_IPAI")

    assert result.get("events_received") == 3, f"Unexpected response: {result}"
    print(f"\n  Meta accepted batch: events_received={result['events_received']}")
