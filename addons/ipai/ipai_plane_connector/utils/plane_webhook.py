# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Plane webhook signature verification.

Pure-Python — no Odoo dependency.  Mock boundary for tests:
    patch("odoo.addons.ipai_plane_connector.utils.plane_webhook.verify_plane_signature")
"""

import hashlib
import hmac


def verify_plane_signature(secret, payload_bytes, signature_header):
    """Verify Plane webhook HMAC-SHA256 signature.

    Args:
        secret: Webhook secret string (or bytes).
        payload_bytes: Raw request body bytes (or string).
        signature_header: ``X-Plane-Signature`` header value.

    Returns:
        bool: ``True`` if the signature is valid, ``False`` otherwise.
    """
    if not secret or not payload_bytes or not signature_header:
        return False
    expected = hmac.new(
        secret.encode("utf-8") if isinstance(secret, str) else secret,
        (payload_bytes if isinstance(payload_bytes, bytes)
         else payload_bytes.encode("utf-8")),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)
