#!/usr/bin/env python3
"""Odoo Login Surface Smoke Test

Validates that the Odoo login page meets branding and debranding requirements.
Designed to run against a live Odoo instance (local devcontainer or ACA).

Checks:
- /web/login returns 200
- Login page contains visible form controls (username/password inputs)
- Page does NOT contain "Your logo" placeholder text
- Page does NOT contain "Powered by Odoo" (debranding check)
- Page contains expected brand marker (configurable via env var)

Environment variables:
    ODOO_URL: Base URL of the Odoo instance (default: http://localhost:8069)
    ODOO_DB: Database name (default: odoo_dev)
    EXPECTED_BRAND: Brand text expected on login page (default: InsightPulse)

Run:
    # Against local devcontainer
    ODOO_URL=http://localhost:8069 python3 tests/test_login_surface_smoke.py

    # Against ACA dev
    ODOO_URL=https://erp.insightpulseai.com python3 tests/test_login_surface_smoke.py

    # With custom brand marker
    EXPECTED_BRAND="My Company" python3 tests/test_login_surface_smoke.py

    # Via pytest
    pytest tests/test_login_surface_smoke.py -v
"""

import os
import re
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ODOO_URL = os.environ.get("ODOO_URL", "http://localhost:8069").rstrip("/")
ODOO_DB = os.environ.get("ODOO_DB", "odoo_dev")
EXPECTED_BRAND = os.environ.get("EXPECTED_BRAND", "InsightPulse")

# Odoo branding strings that must NOT appear after debranding modules are installed.
ODOO_BRANDING_MARKERS = [
    "Powered by Odoo",
    "Powered by <a",  # partial anchor variant: "Powered by <a...>Odoo</a>"
    "odoo.com",
    "Odoo S.A.",
    "Odoo Enterprise",
    "Try Odoo for Free",
    "Upgrade to Enterprise",
]

# Placeholder markers that indicate incomplete company configuration.
PLACEHOLDER_MARKERS = [
    "Your logo",
    "Your Company",
    "My Company",
    "company_logo_placeholder",
]


def fetch(url: str, timeout: int = 30) -> tuple[int, str]:
    """Fetch URL, return (status_code, body)."""
    req = Request(url, headers={"User-Agent": "OdooLoginSmoke/1.0"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body
    except HTTPError as e:
        return e.code, ""
    except URLError:
        return 0, ""


def _get_login_page() -> tuple[int, str]:
    """Fetch the login page. Cached per test run via module-level call."""
    return fetch(f"{ODOO_URL}/web/login")


@unittest.skipIf(
    fetch(ODOO_URL + "/web/health")[0] == 0,
    f"Odoo not reachable at {ODOO_URL} -- skipping login surface tests",
)
class TestLoginSurfaceSmoke(unittest.TestCase):
    """Smoke tests for Odoo login page branding and debranding."""

    @classmethod
    def setUpClass(cls):
        """Fetch login page once for all tests in this class."""
        super().setUpClass()
        cls._status, cls._body = _get_login_page()

    def _require_page(self) -> str:
        """Return page body or skip if login page is not available."""
        if self._status != 200:
            self.skipTest(f"/web/login returned {self._status}")
        return self._body

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    def test_login_returns_200(self):
        """GET /web/login must return HTTP 200."""
        self.assertEqual(
            self._status, 200, f"/web/login returned {self._status}"
        )

    # ------------------------------------------------------------------
    # Form controls
    # ------------------------------------------------------------------

    def test_login_has_username_input(self):
        """Login page must contain an input for username/login."""
        body = self._require_page()
        # Odoo login form uses name="login" for the username field.
        has_login_input = bool(
            re.search(
                r'<input[^>]+name=["\']login["\']', body, re.IGNORECASE
            )
        )
        self.assertTrue(
            has_login_input,
            "Login page missing username input (name='login')",
        )

    def test_login_has_password_input(self):
        """Login page must contain an input for password."""
        body = self._require_page()
        has_password_input = bool(
            re.search(
                r'<input[^>]+type=["\']password["\']', body, re.IGNORECASE
            )
        )
        self.assertTrue(
            has_password_input,
            "Login page missing password input (type='password')",
        )

    def test_login_has_submit_button(self):
        """Login page must contain a submit button."""
        body = self._require_page()
        has_submit = bool(
            re.search(
                r'<button[^>]+type=["\']submit["\']', body, re.IGNORECASE
            )
        ) or bool(
            re.search(
                r'<input[^>]+type=["\']submit["\']', body, re.IGNORECASE
            )
        )
        self.assertTrue(
            has_submit,
            "Login page missing submit button",
        )

    # ------------------------------------------------------------------
    # Placeholder / unconfigured checks
    # ------------------------------------------------------------------

    def test_no_logo_placeholder(self):
        """Login page must NOT contain placeholder logo text."""
        body = self._require_page()
        body_lower = body.lower()
        found = []
        for marker in PLACEHOLDER_MARKERS:
            if marker.lower() in body_lower:
                found.append(marker)
        if found:
            self.fail(
                f"Placeholder text found on login page (incomplete company config): "
                f"{found}"
            )

    # ------------------------------------------------------------------
    # Debranding
    # ------------------------------------------------------------------

    def test_no_odoo_branding(self):
        """Login page must NOT contain Odoo branding after debranding modules."""
        body = self._require_page()
        body_lower = body.lower()
        found = []
        for marker in ODOO_BRANDING_MARKERS:
            if marker.lower() in body_lower:
                # Extract context for diagnostics
                idx = body_lower.find(marker.lower())
                snippet = body[max(0, idx - 40) : idx + len(marker) + 40]
                found.append(f"  - '{marker}' near: ...{snippet.strip()}...")
        if found:
            self.fail(
                f"Odoo branding markers found on login page "
                f"(debranding modules missing or misconfigured):\n"
                + "\n".join(found)
            )

    def test_no_powered_by_odoo(self):
        """Login page must NOT contain 'Powered by Odoo' in any form."""
        body = self._require_page()
        # Catch variants: "Powered by Odoo", "Powered by\n  Odoo", anchor tags
        pattern = r"Powered\s+by\s+(?:<[^>]*>)?\s*Odoo"
        match = re.search(pattern, body, re.IGNORECASE | re.DOTALL)
        if match:
            self.fail(
                f"'Powered by Odoo' found on login page: "
                f"'{match.group()}' -- install OCA debranding modules"
            )

    # ------------------------------------------------------------------
    # Expected brand
    # ------------------------------------------------------------------

    def test_expected_brand_present(self):
        """Login page must contain the expected brand marker."""
        body = self._require_page()
        if EXPECTED_BRAND.lower() not in body.lower():
            self.fail(
                f"Expected brand '{EXPECTED_BRAND}' not found on login page. "
                f"Configure company name and logo in Settings > General Settings > Companies, "
                f"or set EXPECTED_BRAND env var to match your deployment."
            )

    # ------------------------------------------------------------------
    # Page title
    # ------------------------------------------------------------------

    def test_page_title_not_default(self):
        """Login page <title> should not be the default 'Odoo' title."""
        body = self._require_page()
        title_match = re.search(
            r"<title[^>]*>(.*?)</title>", body, re.IGNORECASE | re.DOTALL
        )
        if title_match:
            title_text = title_match.group(1).strip()
            self.assertNotEqual(
                title_text.lower(),
                "odoo",
                f"Page title is still the default 'Odoo' -- "
                f"configure web.base.url.title or install debranding modules",
            )


if __name__ == "__main__":
    unittest.main()
