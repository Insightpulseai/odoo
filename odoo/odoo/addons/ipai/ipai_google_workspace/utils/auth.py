# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Google ID token verification for Workspace Add-on requests.

Every incoming POST from Google Workspace carries a Bearer token.
This module verifies it using google-auth.

Mock boundary for tests:
    patch("odoo.addons.ipai_google_workspace.utils.auth.verify_google_token")
"""

import logging

_logger = logging.getLogger(__name__)


def verify_google_token(token, expected_audience):
    """Verify a Google-signed ID token.

    Args:
        token (str): The Bearer token from the Authorization header.
        expected_audience (str): Google Cloud project number.

    Returns:
        dict: Decoded token claims on success.

    Raises:
        ValueError: If token is invalid, expired, or audience mismatch.
    """
    try:
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests
    except ImportError:
        raise ValueError(
            "google-auth library not installed. "
            "Run: pip install google-auth"
        )

    request = google_requests.Request()
    claims = google_id_token.verify_token(
        token,
        request=request,
        audience=expected_audience,
    )
    _logger.debug("GWS token verified for sub=%s", claims.get("sub"))
    return claims
