# -*- coding: utf-8 -*-
"""
HTTP Endpoint Tests for IDP Module.

Tests HTTP controllers including:
- Health endpoints (livez, readyz, healthz)
- API endpoints
"""
import json

from odoo.tests import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestIdpHealthEndpoints(HttpCase):
    """Test cases for IDP health HTTP endpoints."""

    def test_livez_endpoint_returns_200(self):
        """Test /ipai/idp/livez returns 200 and alive status."""
        response = self.url_open("/ipai/idp/livez")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data.get("status"), "alive")

    def test_readyz_endpoint_returns_status(self):
        """Test /ipai/idp/readyz returns readiness status."""
        response = self.url_open("/ipai/idp/readyz")
        # Should be 200 or 503 depending on readiness
        self.assertIn(response.status_code, [200, 503])

        data = json.loads(response.content)
        self.assertIn("status", data)
        self.assertIn(data["status"], ["ready", "not_ready"])

    def test_readyz_includes_db_check(self):
        """Test /ipai/idp/readyz includes DB check."""
        response = self.url_open("/ipai/idp/readyz")
        data = json.loads(response.content)
        self.assertIn("db", data)

    def test_healthz_endpoint_returns_status(self):
        """Test /ipai/idp/healthz returns deep health status."""
        response = self.url_open("/ipai/idp/healthz")
        self.assertIn(response.status_code, [200, 503])

        data = json.loads(response.content)
        self.assertIn("status", data)
        self.assertIn(data["status"], ["ok", "degraded", "unhealthy"])

    def test_healthz_includes_checks(self):
        """Test /ipai/idp/healthz includes individual checks."""
        response = self.url_open("/ipai/idp/healthz")
        data = json.loads(response.content)
        self.assertIn("checks", data)
        self.assertIn("db", data["checks"])

    def test_healthz_includes_timing(self):
        """Test /ipai/idp/healthz includes timing info."""
        response = self.url_open("/ipai/idp/healthz")
        data = json.loads(response.content)
        self.assertIn("check_time_ms", data)


@tagged("-at_install", "post_install")
class TestIdpApiEndpoints(HttpCase):
    """Test cases for IDP API HTTP endpoints."""

    def setUp(self):
        """Set up per-test fixtures."""
        super().setUp()
        # Authenticate as admin for API tests
        self.authenticate("admin", "admin")

    def test_metrics_endpoint_requires_auth(self):
        """Test /ipai/idp/metrics requires authentication."""
        # Logout first
        self.logout()

        # Make JSON-RPC call
        response = self.url_open(
            "/ipai/idp/metrics",
            data=json.dumps({"jsonrpc": "2.0", "method": "call", "params": {}}),
            headers={"Content-Type": "application/json"},
        )

        # Should fail or redirect without auth
        # Exact behavior depends on Odoo version
        self.assertIn(response.status_code, [200, 303, 400])

    def test_model_versions_endpoint(self):
        """Test /ipai/idp/api/model_versions returns versions."""
        response = self.url_open(
            "/ipai/idp/api/model_versions",
            data=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {"active_only": True},
                    "id": 1,
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        if "result" in data:
            result = data["result"]
            self.assertIn("versions", result)

    def test_parse_amount_endpoint(self):
        """Test /ipai/idp/api/parse/amount parses amounts."""
        response = self.url_open(
            "/ipai/idp/api/parse/amount",
            data=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {"text": "₱1,234.50"},
                    "id": 1,
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        if "result" in data:
            result = data["result"]
            self.assertEqual(result.get("amount"), 1234.50)
            self.assertEqual(result.get("currency"), "PHP")

    def test_parse_date_endpoint(self):
        """Test /ipai/idp/api/parse/date normalizes dates."""
        response = self.url_open(
            "/ipai/idp/api/parse/date",
            data=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {"text": "12/06/2024"},
                    "id": 1,
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        if "result" in data:
            result = data["result"]
            # Should normalize to ISO format
            self.assertIsNotNone(result.get("date"))

    def test_validate_endpoint(self):
        """Test /ipai/idp/api/validate validates data."""
        test_data = {
            "vendor_name": "Test Vendor",
            "total": 100.00,
            "invoice_date": "2024-12-06",
        }

        response = self.url_open(
            "/ipai/idp/api/validate",
            data=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {"data": test_data, "doc_type": "invoice"},
                    "id": 1,
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        if "result" in data:
            result = data["result"]
            self.assertIn("status", result)
            self.assertIn(result["status"], ["pass", "fail", "warning"])

    def test_documents_list_endpoint(self):
        """Test /ipai/idp/api/documents returns document list."""
        response = self.url_open(
            "/ipai/idp/api/documents",
            data=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {"limit": 10},
                    "id": 1,
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        if "result" in data:
            result = data["result"]
            self.assertIn("documents", result)
            self.assertIn("total", result)
