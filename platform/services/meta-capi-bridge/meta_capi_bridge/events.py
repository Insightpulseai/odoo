"""Canonical event schema — maps Odoo business events to Meta CAPI payloads.

Supported events:
  - lead_created      → Lead
  - lead_qualified    → Lead (qualified)
  - opportunity_won   → Purchase / CompleteRegistration
  - invoice_paid      → Purchase
  - refund_issued     → (custom event)
"""

import hashlib
import time
from typing import Any


def _hash_pii(value: str) -> str:
    """SHA-256 hash for PII fields per Meta CAPI spec."""
    return hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()


def _build_user_data(event: dict[str, Any]) -> dict[str, Any]:
    """Extract and hash user data from canonical event."""
    user = event.get("user", {})
    data: dict[str, Any] = {}

    if email := user.get("email"):
        data["em"] = [_hash_pii(email)]
    if phone := user.get("phone"):
        data["ph"] = [_hash_pii(phone)]
    if first_name := user.get("first_name"):
        data["fn"] = _hash_pii(first_name)
    if last_name := user.get("last_name"):
        data["ln"] = _hash_pii(last_name)
    if city := user.get("city"):
        data["ct"] = _hash_pii(city)
    if country := user.get("country_code"):
        data["country"] = _hash_pii(country)

    # Client identifiers (not hashed)
    if client_ip := user.get("client_ip"):
        data["client_ip_address"] = client_ip
    if user_agent := user.get("user_agent"):
        data["client_user_agent"] = user_agent
    if fbc := user.get("fbc"):
        data["fbc"] = fbc
    if fbp := user.get("fbp"):
        data["fbp"] = fbp

    return data


# Event type mapping: canonical → Meta CAPI event_name
EVENT_MAP = {
    "lead_created": "Lead",
    "lead_qualified": "Lead",
    "opportunity_won": "Purchase",
    "invoice_paid": "Purchase",
    "refund_issued": "Refund",
}


def to_capi_payload(event: dict[str, Any]) -> dict[str, Any]:
    """Transform a canonical Odoo business event into a Meta CAPI event payload.

    Args:
        event: Canonical event dict with keys:
            - event_type: str (one of EVENT_MAP keys)
            - event_id: str (idempotency key)
            - timestamp: int (unix epoch, optional — defaults to now)
            - source_url: str (optional)
            - user: dict (email, phone, first_name, last_name, etc.)
            - custom_data: dict (currency, value, content_name, etc.)

    Returns:
        Dict ready for Meta CAPI /events endpoint.
    """
    event_type = event["event_type"]
    meta_event_name = EVENT_MAP.get(event_type, event_type)

    capi_event: dict[str, Any] = {
        "event_name": meta_event_name,
        "event_time": event.get("timestamp", int(time.time())),
        "event_id": event["event_id"],
        "action_source": event.get("action_source", "system_generated"),
        "user_data": _build_user_data(event),
    }

    if source_url := event.get("source_url"):
        capi_event["event_source_url"] = source_url

    # Custom data (value, currency, content info)
    custom = event.get("custom_data", {})
    if custom:
        capi_custom: dict[str, Any] = {}
        if "value" in custom:
            capi_custom["value"] = float(custom["value"])
        if "currency" in custom:
            capi_custom["currency"] = custom["currency"].upper()
        if "content_name" in custom:
            capi_custom["content_name"] = custom["content_name"]
        if "content_ids" in custom:
            capi_custom["content_ids"] = custom["content_ids"]
        if "content_type" in custom:
            capi_custom["content_type"] = custom["content_type"]
        if "order_id" in custom:
            capi_custom["order_id"] = custom["order_id"]
        if capi_custom:
            capi_event["custom_data"] = capi_custom

    # Qualified lead distinction
    if event_type == "lead_qualified":
        capi_event.setdefault("custom_data", {})["lead_event_source"] = "qualified"

    return capi_event
