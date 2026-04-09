# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import unittest


class TestAcaProxyHeaderInjection(unittest.TestCase):
    """Test the ACA proxy header injection logic without requiring Odoo runtime.

    The ipai_aca_proxy module monkey-patches Application.__call__ to inject
    X-Forwarded-Host from the Host header when ACA's Envoy ingress omits it.
    These tests verify the conditional logic directly.
    """

    @staticmethod
    def _simulate_patch(environ):
        """Replicate the patch logic from ipai_aca_proxy.__init__.py."""
        if (
            environ.get("HTTP_X_FORWARDED_PROTO")
            and not environ.get("HTTP_X_FORWARDED_HOST")
            and environ.get("HTTP_HOST")
        ):
            environ["HTTP_X_FORWARDED_HOST"] = environ["HTTP_HOST"]
        return environ

    def test_inject_when_proto_present_host_missing(self):
        """ACA scenario: X-Forwarded-Proto set, X-Forwarded-Host absent."""
        env = {
            "HTTP_X_FORWARDED_PROTO": "https",
            "HTTP_X_FORWARDED_FOR": "10.0.0.1",
            "HTTP_HOST": "odoo.insightpulseai.com",
        }
        result = self._simulate_patch(env)
        self.assertEqual(
            result["HTTP_X_FORWARDED_HOST"],
            "odoo.insightpulseai.com",
        )

    def test_no_inject_when_forwarded_host_already_present(self):
        """Standard proxy: X-Forwarded-Host already set, no override."""
        env = {
            "HTTP_X_FORWARDED_PROTO": "https",
            "HTTP_X_FORWARDED_HOST": "existing.example.com",
            "HTTP_HOST": "odoo.insightpulseai.com",
        }
        result = self._simulate_patch(env)
        self.assertEqual(
            result["HTTP_X_FORWARDED_HOST"],
            "existing.example.com",
            "Should not override existing X-Forwarded-Host",
        )

    def test_no_inject_when_no_forwarded_proto(self):
        """Direct connection: no X-Forwarded-Proto, no injection needed."""
        env = {
            "HTTP_HOST": "localhost:8069",
        }
        result = self._simulate_patch(env)
        self.assertNotIn(
            "HTTP_X_FORWARDED_HOST",
            result,
            "Should not inject when no X-Forwarded-Proto",
        )

    def test_no_inject_when_no_host_header(self):
        """Edge case: X-Forwarded-Proto set but no Host header."""
        env = {
            "HTTP_X_FORWARDED_PROTO": "https",
        }
        result = self._simulate_patch(env)
        self.assertNotIn(
            "HTTP_X_FORWARDED_HOST",
            result,
            "Should not inject when Host header is absent",
        )

    def test_preserves_other_environ_keys(self):
        """Injection must not alter other environ keys."""
        env = {
            "HTTP_X_FORWARDED_PROTO": "https",
            "HTTP_HOST": "odoo.insightpulseai.com",
            "SERVER_NAME": "0.0.0.0",
            "SERVER_PORT": "8069",
        }
        result = self._simulate_patch(env)
        self.assertEqual(result["SERVER_NAME"], "0.0.0.0")
        self.assertEqual(result["SERVER_PORT"], "8069")

    def test_http_proto_value_preserved(self):
        """X-Forwarded-Proto=http should still trigger injection."""
        env = {
            "HTTP_X_FORWARDED_PROTO": "http",
            "HTTP_HOST": "staging.insightpulseai.com",
        }
        result = self._simulate_patch(env)
        self.assertEqual(
            result["HTTP_X_FORWARDED_HOST"],
            "staging.insightpulseai.com",
        )

    def test_post_load_function_importable(self):
        """The post_load entry point must be importable."""
        from ipai_aca_proxy import _aca_proxy_post_load
        self.assertTrue(callable(_aca_proxy_post_load))


class TestAcaProxyInstallSmoke(unittest.TestCase):
    """Verify module is importable without side effects."""

    def test_module_importable(self):
        """ipai_aca_proxy must be importable."""
        import ipai_aca_proxy  # noqa: F401
        self.assertTrue(hasattr(ipai_aca_proxy, "_aca_proxy_post_load"))
