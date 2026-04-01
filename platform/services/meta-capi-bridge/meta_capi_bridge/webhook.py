"""Inbound webhook signature verification for Meta callbacks."""

import hashlib
import hmac
import logging

from .config import config

logger = logging.getLogger("meta_capi_bridge")


def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify Meta webhook signature (X-Hub-Signature-256).

    Args:
        payload_body: Raw request body bytes.
        signature_header: Value of X-Hub-Signature-256 header.

    Returns:
        True if signature is valid.
    """
    if not config.META_APP_SECRET:
        logger.warning("META_APP_SECRET not set — skipping signature verification")
        return False

    if not signature_header or not signature_header.startswith("sha256="):
        logger.warning("Missing or malformed signature header")
        return False

    expected = hmac.new(
        config.META_APP_SECRET.encode("utf-8"),
        payload_body,
        hashlib.sha256,
    ).hexdigest()

    received = signature_header.removeprefix("sha256=")
    return hmac.compare_digest(expected, received)
