# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAuthOidcProviders(TransactionCase):
    """Verify OAuth provider data records created by ipai_auth_oidc."""

    def test_keycloak_provider_exists(self):
        """Keycloak SSO provider record must exist after install."""
        provider = self.env.ref(
            "ipai_auth_oidc.auth_provider_keycloak",
            raise_if_not_found=False,
        )
        self.assertTrue(provider, "Keycloak provider record not found")

    def test_google_provider_exists(self):
        """Google OIDC provider record must exist after install."""
        provider = self.env.ref(
            "ipai_auth_oidc.auth_provider_google_oidc",
            raise_if_not_found=False,
        )
        self.assertTrue(provider, "Google OIDC provider record not found")

    def test_keycloak_provider_disabled_by_default(self):
        """Keycloak provider must be disabled on fresh install."""
        provider = self.env.ref("ipai_auth_oidc.auth_provider_keycloak")
        self.assertFalse(
            provider.enabled,
            "Keycloak provider should be disabled by default",
        )

    def test_google_provider_disabled_by_default(self):
        """Google provider must be disabled on fresh install."""
        provider = self.env.ref("ipai_auth_oidc.auth_provider_google_oidc")
        self.assertFalse(
            provider.enabled,
            "Google provider should be disabled by default",
        )

    def test_keycloak_endpoints_use_correct_domain(self):
        """Keycloak endpoints must point to insightpulseai.com."""
        provider = self.env.ref("ipai_auth_oidc.auth_provider_keycloak")
        self.assertIn(
            "auth.insightpulseai.com",
            provider.auth_endpoint,
            "Auth endpoint must use insightpulseai.com domain",
        )
        self.assertIn(
            "auth.insightpulseai.com",
            provider.validation_endpoint,
            "Validation endpoint must use insightpulseai.com domain",
        )

    def test_no_deprecated_domain_in_endpoints(self):
        """No provider should reference the deprecated .net domain."""
        providers = self.env["auth.oauth.provider"].search([])
        for p in providers:
            if p.auth_endpoint:
                self.assertNotIn(
                    "insightpulseai.net",
                    p.auth_endpoint,
                    "Provider %s uses deprecated .net domain" % p.name,
                )

    def test_scopes_include_openid(self):
        """Both providers must request openid scope."""
        for xmlid in [
            "ipai_auth_oidc.auth_provider_keycloak",
            "ipai_auth_oidc.auth_provider_google_oidc",
        ]:
            provider = self.env.ref(xmlid)
            self.assertIn(
                "openid",
                provider.scope,
                "Provider %s missing openid scope" % provider.name,
            )

    def test_no_hardcoded_secrets_in_provider_data(self):
        """Client IDs must not contain real secrets (only placeholders)."""
        google = self.env.ref("ipai_auth_oidc.auth_provider_google_oidc")
        self.assertIn(
            "PLACEHOLDER",
            google.client_id,
            "Google client_id should be a placeholder, not a real secret",
        )

    def test_provider_sequence_ordering(self):
        """Keycloak should have lower sequence (primary) than Google."""
        kc = self.env.ref("ipai_auth_oidc.auth_provider_keycloak")
        google = self.env.ref("ipai_auth_oidc.auth_provider_google_oidc")
        self.assertLess(
            kc.sequence,
            google.sequence,
            "Keycloak (primary) should have lower sequence than Google (fallback)",
        )
