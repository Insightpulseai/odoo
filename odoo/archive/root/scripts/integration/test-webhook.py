#!/usr/bin/env python3
"""
Test IPAI webhook signature and event emission
"""
import hmac
import hashlib
import json
import time
import uuid
import requests
import os
import sys


def send_test_event(url, secret, event_type="expense.submitted"):
    """Send test event to Edge Function with HMAC signature"""

    # Sample payloads
    payloads = {
        "expense.submitted": {
            "event_type": "expense.submitted",
            "aggregate_type": "expense",
            "aggregate_id": "12345",
            "payload": {
                "expense_id": 12345,
                "employee_id": 42,
                "employee_name": "John Doe",
                "employee_code": "EMP001",
                "amount": 1000.00,
                "currency": "PHP",
                "description": "Client dinner - Makati",
                "date": "2026-01-22",
                "category": "Meals & Entertainment",
                "submitted_at": "2026-01-22T10:30:00Z",
                "status": "submit"
            }
        },
        "asset.reserved": {
            "event_type": "asset.reserved",
            "aggregate_type": "asset_booking",
            "aggregate_id": "67890",
            "payload": {
                "booking_id": 67890,
                "asset_id": 15,
                "asset_name": "MacBook Pro 14\" M3",
                "asset_category": "Laptop",
                "reserved_by": 42,
                "reserved_by_name": "John Doe",
                "reserved_from": "2026-01-25",
                "reserved_to": "2026-01-27",
                "purpose": "Client presentation",
                "booking_state": "reserved"
            }
        },
        "finance_task.created": {
            "event_type": "finance_task.created",
            "aggregate_type": "finance_task",
            "aggregate_id": "100",
            "payload": {
                "task_id": 100,
                "task_code": "BIR-1601C-2026-01-RIM",
                "task_name": "BIR 1601-C Preparation - January 2026",
                "bir_form": "1601-C",
                "period_covered": "2026-01",
                "employee_code": "RIM",
                "prep_deadline": "2026-02-06",
                "filing_deadline": "2026-02-10",
                "status": "not_started"
            }
        }
    }

    if event_type not in payloads:
        print(f"❌ Unknown event type: {event_type}")
        print(f"   Available: {', '.join(payloads.keys())}")
        sys.exit(1)

    body = payloads[event_type]

    # Generate signature
    ts = str(int(time.time() * 1000))
    raw = json.dumps(body, separators=(",", ":"))
    sig = hmac.new(
        secret.encode("utf-8"),
        f"{ts}.{raw}".encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "content-type": "application/json",
        "x-ipai-timestamp": ts,
        "x-ipai-signature": sig,
        "x-idempotency-key": str(uuid.uuid4()),
    }

    print(f"Sending {event_type} event...")
    print(f"URL: {url}")
    print(f"Timestamp: {ts}")
    print(f"Signature: {sig[:20]}...")
    print(f"Payload: {json.dumps(body, indent=2)}")
    print("")

    try:
        r = requests.post(url, data=raw.encode("utf-8"), headers=headers, timeout=15)

        print(f"Response Status: {r.status_code}")
        print(f"Response Body: {r.text}")

        if r.status_code == 200:
            print("✅ Event sent successfully")
            return True
        else:
            print(f"❌ Event failed with status {r.status_code}")
            return False

    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False


def main():
    # Load from environment or use defaults
    url = os.environ.get("SUPABASE_FUNCTION_URL")
    secret = os.environ.get("ODOO_WEBHOOK_SECRET")

    if not url:
        print("❌ SUPABASE_FUNCTION_URL not set")
        print("   Set with: export SUPABASE_FUNCTION_URL='https://PROJECT.supabase.co/functions/v1/odoo-webhook'")
        sys.exit(1)

    if not secret:
        print("❌ ODOO_WEBHOOK_SECRET not set")
        print("   Set with: export ODOO_WEBHOOK_SECRET='your-secret-here'")
        sys.exit(1)

    # Test all event types
    event_types = ["expense.submitted", "asset.reserved", "finance_task.created"]

    if len(sys.argv) > 1:
        # Test specific event type
        event_types = [sys.argv[1]]

    print("=== IPAI Webhook Test Suite ===")
    print("")

    results = {}
    for event_type in event_types:
        success = send_test_event(url, secret, event_type)
        results[event_type] = success
        print("")
        time.sleep(1)  # Avoid rate limiting

    print("=== Test Results ===")
    for event_type, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {event_type}")

    print("")
    print("Next Steps:")
    print("1. Verify events in Supabase:")
    print("   supabase db query \"SELECT * FROM integration.outbox ORDER BY created_at DESC LIMIT 10;\"")
    print("")
    print("2. Check n8n event router is active")
    print("")
    print("3. Monitor Mattermost for notifications")
    print("")

    # Exit with error if any test failed
    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
