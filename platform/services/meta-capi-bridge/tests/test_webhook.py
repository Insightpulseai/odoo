"""Tests for webhook signature verification."""

import hashlib
import hmac
from unittest.mock import patch

from meta_capi_bridge import webhook


def test_valid_signature():
    secret = "test_app_secret_123"
    body = b'{"object":"page","entry":[]}'
    sig = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    with patch.object(webhook.config, "META_APP_SECRET", secret):
        assert webhook.verify_signature(body, sig) is True


def test_invalid_signature():
    secret = "test_app_secret_123"
    body = b'{"object":"page","entry":[]}'
    sig = "sha256=0000000000000000000000000000000000000000000000000000000000000000"

    with patch.object(webhook.config, "META_APP_SECRET", secret):
        assert webhook.verify_signature(body, sig) is False


def test_missing_signature():
    with patch.object(webhook.config, "META_APP_SECRET", "secret"):
        assert webhook.verify_signature(b"body", "") is False


def test_no_app_secret():
    with patch.object(webhook.config, "META_APP_SECRET", ""):
        assert webhook.verify_signature(b"body", "sha256=abc") is False
