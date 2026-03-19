#!/usr/bin/env python3
"""Odoo Web Asset Smoke Test

Validates that the Odoo web interface loads without asset bundling errors.
Designed to run against a live Odoo instance (local devcontainer or ACA).

Checks:
- /web/login returns 200
- page source contains no asset compilation exceptions
- critical bundled asset URLs return 200
- no 500 errors on initial page load

Environment variables:
    ODOO_URL: Base URL of the Odoo instance (default: http://localhost:8069)
    ODOO_DB: Database name (default: odoo_dev)

Run:
    # Against local devcontainer
    ODOO_URL=http://localhost:8069 python3 tests/test_web_asset_smoke.py

    # Against ACA dev
    ODOO_URL=https://erp.insightpulseai.com python3 tests/test_web_asset_smoke.py

    # Via pytest
    pytest tests/test_web_asset_smoke.py -v
"""

import os
import re
import sys
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ODOO_URL = os.environ.get("ODOO_URL", "http://localhost:8069").rstrip("/")
ODOO_DB = os.environ.get("ODOO_DB", "odoo_dev")

# Asset error markers that indicate bundling failures.
# Note: Odoo script tags have onerror="__odooAssetError=1" by default — that is
# NOT an error, it's a standard error handler attribute. We only match markers
# that appear outside of HTML attribute contexts.
ASSET_ERROR_MARKERS = [
    "Asset compilation error",
    "QWebException",
    "Could not compile",
    "Cannot read properties of undefined",
    "Module not found",
    "owl.js:Error",
    "web.assets_backend: error",
    "web.assets_frontend: error",
    "Traceback (most recent call last)",
    "Internal Server Error",
]

# Known critical asset URL patterns (regex) that must resolve
CRITICAL_ASSET_PATTERNS = [
    r"/web/assets/[^\"']+\.js",
    r"/web/assets/[^\"']+\.css",
]


def fetch(url: str, timeout: int = 30) -> tuple[int, str]:
    """Fetch URL, return (status_code, body)."""
    req = Request(url, headers={"User-Agent": "OdooAssetSmoke/1.0"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body
    except HTTPError as e:
        return e.code, ""
    except URLError:
        return 0, ""


@unittest.skipIf(
    fetch(ODOO_URL + "/web/health")[0] == 0,
    f"Odoo not reachable at {ODOO_URL} — skipping smoke tests",
)
class TestWebAssetSmoke(unittest.TestCase):
    """Smoke tests for Odoo web asset bundling."""

    def test_web_login_returns_200(self):
        """GET /web/login must return HTTP 200."""
        status, _ = fetch(f"{ODOO_URL}/web/login")
        self.assertEqual(status, 200, f"/web/login returned {status}")

    def test_web_login_no_asset_errors(self):
        """Login page source must not contain asset compilation errors."""
        status, body = fetch(f"{ODOO_URL}/web/login")
        if status != 200:
            self.skipTest(f"/web/login returned {status}")

        found = []
        for marker in ASSET_ERROR_MARKERS:
            if marker.lower() in body.lower():
                # Extract context around the marker
                idx = body.lower().find(marker.lower())
                snippet = body[max(0, idx - 50) : idx + len(marker) + 50]
                found.append(f"  - '{marker}' found near: ...{snippet.strip()}...")

        if found:
            self.fail(
                f"Asset error markers found in /web/login:\n" + "\n".join(found)
            )

    def test_critical_asset_urls_resolve(self):
        """Critical asset URLs extracted from login page must return 200."""
        status, body = fetch(f"{ODOO_URL}/web/login")
        if status != 200:
            self.skipTest(f"/web/login returned {status}")

        asset_urls = set()
        for pattern in CRITICAL_ASSET_PATTERNS:
            matches = re.findall(pattern, body)
            asset_urls.update(matches)

        if not asset_urls:
            # No bundled asset URLs found — might be a minimal page or error page
            self.skipTest("No asset URLs found in /web/login page source")

        failures = []
        for asset_url in sorted(asset_urls)[:10]:  # Check up to 10 assets
            full_url = f"{ODOO_URL}{asset_url}"
            asset_status, _ = fetch(full_url, timeout=15)
            if asset_status != 200:
                failures.append(f"  - {asset_url} → {asset_status}")

        if failures:
            self.fail(
                f"Critical asset URLs failed ({len(failures)}/{len(asset_urls)}):\n"
                + "\n".join(failures)
            )

    def test_web_login_no_500(self):
        """Login page must not return 500-series errors."""
        status, _ = fetch(f"{ODOO_URL}/web/login")
        self.assertLess(status, 500, f"/web/login returned server error {status}")

    def test_web_health_endpoint(self):
        """/web/health must return 200 (basic Odoo liveness)."""
        status, _ = fetch(f"{ODOO_URL}/web/health")
        self.assertEqual(status, 200, f"/web/health returned {status}")


if __name__ == "__main__":
    unittest.main()
