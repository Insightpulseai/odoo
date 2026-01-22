# -*- coding: utf-8 -*-
"""
IPAI Webhook Emitter - Send events to Supabase integration bus via signed webhooks
"""
import hmac
import hashlib
import json
import time
import uuid
import requests
import logging

_logger = logging.getLogger(__name__)


def send_ipai_event(url: str, secret: str, event: dict, idempotency_key: str | None = None, timeout=10):
    """
    Send event to IPAI integration bus (Supabase Edge Function) with HMAC signature.

    Args:
        url: Edge Function URL (e.g., https://PROJECT.functions.supabase.co/odoo-webhook)
        secret: ODOO_WEBHOOK_SECRET (shared secret for HMAC)
        event: Event dictionary with required fields:
            - event_type: str (e.g., "expense.submitted")
            - aggregate_type: str (e.g., "expense")
            - aggregate_id: str (Odoo record ID)
            - payload: dict (event-specific data)
        idempotency_key: Optional idempotency key (UUID generated if not provided)
        timeout: Request timeout in seconds

    Returns:
        dict: Response JSON ({"ok": True} on success)

    Raises:
        requests.HTTPError: If request fails
    """
    ts = str(int(time.time() * 1000))
    raw = json.dumps(event, separators=(",", ":"), ensure_ascii=False)
    sig = hmac.new(secret.encode("utf-8"), f"{ts}.{raw}".encode("utf-8"), hashlib.sha256).hexdigest()

    headers = {
        "content-type": "application/json",
        "x-ipai-timestamp": ts,
        "x-ipai-signature": sig,
        "x-idempotency-key": idempotency_key or str(uuid.uuid4()),
    }

    _logger.info(f"Sending IPAI event: {event.get('event_type')} for {event.get('aggregate_type')}#{event.get('aggregate_id')}")

    r = requests.post(url, data=raw.encode("utf-8"), headers=headers, timeout=timeout)
    r.raise_for_status()

    return r.json() if r.content else {"ok": True}
