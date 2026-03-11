"""
Pure-Python unit tests for utils/ocr_client.fetch_image_text().

These tests have NO Odoo dependency and run via plain pytest:
    pytest addons/ipai/ipai_expense_ocr/tests/test_ocr_client.py -v

Coverage targets
----------------
- Happy path: {"text": "..."} response
- Happy path: {"lines": [...]} fallback (no "text" key)
- HTTP 500 → requests.HTTPError propagates
- Connection timeout → requests.Timeout propagates
- Response JSON is not a dict → KeyError/TypeError propagates
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

# ---------------------------------------------------------------------------
# sys.path bootstrap — allow import of utils/ocr_client without Odoo loader
# ---------------------------------------------------------------------------
_ADDON_ROOT = Path(__file__).parent.parent.parent  # addons/ipai/
if str(_ADDON_ROOT) not in sys.path:
    sys.path.insert(0, str(_ADDON_ROOT))

from ipai_expense_ocr.utils.ocr_client import fetch_image_text  # noqa: E402

FAKE_ENDPOINT = "http://fake-ocr.test"
FAKE_IMAGE = b"FAKE IMAGE BYTES"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_response(json_payload, status_code=200):
    """Return a MagicMock that behaves like a requests.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_payload
    if status_code >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError(
            f"{status_code} Error", response=resp
        )
    else:
        resp.raise_for_status.return_value = None
    return resp


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_fetch_returns_text_field():
    """Response with 'text' key → that string is returned."""
    payload = {"text": "ACME STORE\n2026-01-25\nTotal PHP 123.45", "confidence": 0.95}
    with patch("requests.post", return_value=_mock_response(payload)) as mock_post:
        result = fetch_image_text(FAKE_IMAGE, FAKE_ENDPOINT)

    assert result == "ACME STORE\n2026-01-25\nTotal PHP 123.45"
    mock_post.assert_called_once()
    call_url = mock_post.call_args[0][0]
    assert call_url == f"{FAKE_ENDPOINT}/ocr"


def test_fetch_fallback_to_lines_when_no_text_key():
    """Response without 'text' key → lines[].text joined with newline."""
    payload = {
        "lines": [
            {"text": "Coffee Shop", "confidence": 0.9},
            {"text": "Total: 150.00", "confidence": 0.85},
        ]
    }
    with patch("requests.post", return_value=_mock_response(payload)):
        result = fetch_image_text(FAKE_IMAGE, FAKE_ENDPOINT)

    assert "Coffee Shop" in result
    assert "Total: 150.00" in result


def test_fetch_empty_text_falls_back_to_lines():
    """Response with 'text': None → falls back to lines."""
    payload = {
        "text": None,
        "lines": [{"text": "Receipt", "confidence": 0.8}],
    }
    with patch("requests.post", return_value=_mock_response(payload)):
        result = fetch_image_text(FAKE_IMAGE, FAKE_ENDPOINT)

    assert "Receipt" in result


def test_fetch_url_strips_trailing_slash():
    """Endpoint URL with trailing slash → /ocr not //ocr."""
    payload = {"text": "OK"}
    with patch("requests.post", return_value=_mock_response(payload)) as mock_post:
        fetch_image_text(FAKE_IMAGE, FAKE_ENDPOINT + "/")

    assert mock_post.call_args[0][0] == f"{FAKE_ENDPOINT}/ocr"


def test_fetch_sends_file_multipart():
    """Image bytes are sent as multipart 'file' field."""
    payload = {"text": "OK"}
    with patch("requests.post", return_value=_mock_response(payload)) as mock_post:
        fetch_image_text(FAKE_IMAGE, FAKE_ENDPOINT)

    _, kwargs = mock_post.call_args
    assert "files" in kwargs
    file_tuple = kwargs["files"]["file"]
    assert FAKE_IMAGE in file_tuple  # (filename, bytes, mimetype)


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------


def test_fetch_http_500_raises():
    """HTTP 500 response → requests.HTTPError propagates to caller."""
    with patch("requests.post", return_value=_mock_response({}, status_code=500)):
        with pytest.raises(requests.HTTPError):
            fetch_image_text(FAKE_IMAGE, FAKE_ENDPOINT)


def test_fetch_timeout_raises():
    """Connection timeout → requests.Timeout propagates."""
    with patch("requests.post", side_effect=requests.Timeout("timed out")):
        with pytest.raises(requests.Timeout):
            fetch_image_text(FAKE_IMAGE, FAKE_ENDPOINT)


def test_fetch_connection_error_raises():
    """Connection refused → requests.ConnectionError propagates."""
    with patch(
        "requests.post", side_effect=requests.ConnectionError("connection refused")
    ):
        with pytest.raises(requests.ConnectionError):
            fetch_image_text(FAKE_IMAGE, FAKE_ENDPOINT)


def test_fetch_json_decode_error_raises():
    """Non-JSON response body → ValueError/JSONDecodeError propagates."""
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.side_effect = ValueError("not valid JSON")
    with patch("requests.post", return_value=resp):
        with pytest.raises(ValueError):
            fetch_image_text(FAKE_IMAGE, FAKE_ENDPOINT)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
