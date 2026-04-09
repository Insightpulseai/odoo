"""Meta CAPI HTTP client with App Secret Proof, retry, and dead-letter."""

import hashlib
import hmac
import logging
import time
from typing import Any

import requests

from .config import config

logger = logging.getLogger("meta_capi_bridge")

MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2  # seconds


def _generate_appsecret_proof(access_token: str, app_secret: str) -> str:
    """Generate appsecret_proof HMAC-SHA256 per Meta docs."""
    return hmac.new(
        app_secret.encode("utf-8"),
        access_token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def send_events(events: list[dict[str, Any]], test_event_code: str = "") -> dict[str, Any]:
    """Send batch of CAPI events to Meta.

    Args:
        events: List of CAPI event payloads (from events.to_capi_payload).
        test_event_code: Optional test event code for sandbox validation.

    Returns:
        Meta API response dict.

    Raises:
        MetaCapiError: On non-retryable failure after exhausting retries.
    """
    validation_errors = config.validate()
    if validation_errors:
        raise MetaCapiError(f"Config validation failed: {', '.join(validation_errors)}")

    payload: dict[str, Any] = {
        "data": events,
        "access_token": config.META_ACCESS_TOKEN,
    }

    if test_event_code or config.META_TEST_EVENT_CODE:
        payload["test_event_code"] = test_event_code or config.META_TEST_EVENT_CODE

    params: dict[str, str] = {}
    if config.META_APP_SECRET:
        params["appsecret_proof"] = _generate_appsecret_proof(
            config.META_ACCESS_TOKEN, config.META_APP_SECRET
        )

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(
                config.capi_url,
                json=payload,
                params=params,
                timeout=30,
            )

            if resp.status_code == 200:
                result = resp.json()
                event_ids = [e.get("event_id", "?") for e in events]
                logger.info(
                    "CAPI delivery success",
                    extra={
                        "events_received": result.get("events_received"),
                        "event_ids": event_ids,
                        "attempt": attempt + 1,
                    },
                )
                return result

            # Rate limit — retry with backoff
            if resp.status_code == 429:
                wait = RETRY_BACKOFF_BASE ** (attempt + 1)
                logger.warning(f"Rate limited, retrying in {wait}s (attempt {attempt + 1})")
                time.sleep(wait)
                last_error = f"HTTP 429: {resp.text[:200]}"
                continue

            # Server error — retry
            if resp.status_code >= 500:
                wait = RETRY_BACKOFF_BASE ** (attempt + 1)
                logger.warning(f"Server error {resp.status_code}, retrying in {wait}s")
                time.sleep(wait)
                last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
                continue

            # Client error — don't retry
            error_body = resp.text[:500]
            logger.error(f"CAPI client error: {resp.status_code} {error_body}")
            raise MetaCapiError(f"HTTP {resp.status_code}: {error_body}")

        except requests.RequestException as e:
            wait = RETRY_BACKOFF_BASE ** (attempt + 1)
            logger.warning(f"Request error: {e}, retrying in {wait}s")
            time.sleep(wait)
            last_error = str(e)

    raise MetaCapiError(f"Exhausted {MAX_RETRIES} retries. Last error: {last_error}")


class MetaCapiError(Exception):
    """Non-retryable CAPI delivery failure."""
