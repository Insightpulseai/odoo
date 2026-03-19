# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Thin HTTP adapter for Slack Incoming Webhooks.

This module is the mock boundary in Layer-2 tests:
    patch("odoo.addons.ipai_slack_connector.utils.slack_client.post_webhook")

Keeping all requests logic here (instead of in the Odoo model) means:
- Pure-Python (Layer 1) tests can import and test this directly
- Layer-2 tests mock at a clean boundary without touching Odoo internals
"""

import requests


def post_webhook(url, payload, timeout=10):
    """POST *payload* as JSON to *url*.

    Args:
        url (str): Slack Incoming Webhook URL.
        payload (dict): JSON-serialisable message payload.
        timeout (int): Request timeout in seconds.

    Returns:
        requests.Response

    Raises:
        requests.HTTPError: If the server returns HTTP >= 300.
        requests.exceptions.RequestException: On network errors.
    """
    resp = requests.post(url, json=payload, timeout=timeout)
    if resp.status_code >= 300:
        raise requests.HTTPError(
            f"Slack webhook HTTP {resp.status_code}: {resp.text}",
            response=resp,
        )
    return resp
