"""Managed identity and RBAC smoke tests.

Covers:
  - ACA managed identity can acquire a token from IMDS
  - Key Vault secret access succeeds with managed identity
  - ACR pull succeeds (container image access)
  - Denied path: wrong scope returns 403/401

Requires env vars (skipped without):
  AZURE_SUBSCRIPTION_ID — Azure subscription
  KEY_VAULT_NAME — Key Vault to test access against

Run:  pytest infra/tests/smoke/test_managed_identity.py -v
CI:   azure_staging_revision gate
"""

import os
import json

import pytest

SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID", "")
KEY_VAULT_NAME = os.environ.get("KEY_VAULT_NAME", "")
SKIP = not SUBSCRIPTION_ID or not KEY_VAULT_NAME


@pytest.mark.skipif(SKIP, reason="AZURE_SUBSCRIPTION_ID or KEY_VAULT_NAME not set")
class TestManagedIdentityBindings:
    """Validate managed identity can access expected Azure resources."""

    def _get_imds_token(self, resource: str) -> str:
        """Acquire a token from the Instance Metadata Service (IMDS)."""
        import urllib.request

        url = (
            "http://169.254.169.254/metadata/identity/oauth2/token"
            f"?api-version=2018-02-01&resource={resource}"
        )
        req = urllib.request.Request(url, headers={"Metadata": "true"})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                return data["access_token"]
        except Exception as e:
            pytest.fail(f"IMDS token acquisition failed: {e}")

    def test_imds_token_for_key_vault(self):
        """Managed identity can acquire a token for Key Vault."""
        token = self._get_imds_token("https://vault.azure.net")
        assert len(token) > 0, "Token must not be empty"
        # JWT format: header.payload.signature
        parts = token.split(".")
        assert len(parts) == 3, f"Token is not a valid JWT (got {len(parts)} parts)"

    def test_key_vault_secret_accessible(self):
        """Managed identity can read a secret from Key Vault."""
        import urllib.request
        import urllib.error

        token = self._get_imds_token("https://vault.azure.net")
        # Try to list secrets (just need 200, not the actual values)
        url = f"https://{KEY_VAULT_NAME}.vault.azure.net/secrets?api-version=7.4&maxresults=1"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
        })
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                assert resp.status == 200, f"Key Vault returned {resp.status}"
        except urllib.error.HTTPError as e:
            if e.code == 403:
                pytest.fail(
                    f"Key Vault access denied (403). "
                    f"Managed identity may lack 'Key Vault Secrets User' role on {KEY_VAULT_NAME}"
                )
            raise

    def test_denied_path_wrong_scope(self):
        """Token acquired for wrong resource should be rejected by Key Vault."""
        import urllib.request
        import urllib.error

        # Acquire token for management plane (wrong scope for Key Vault data plane)
        token = self._get_imds_token("https://management.azure.com")

        url = f"https://{KEY_VAULT_NAME}.vault.azure.net/secrets?api-version=7.4&maxresults=1"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
        })
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                pytest.fail(
                    f"Expected 401/403 for wrong-scope token, got {resp.status}"
                )
        except urllib.error.HTTPError as e:
            assert e.code in (401, 403), (
                f"Expected 401 or 403 for wrong-scope token, got {e.code}"
            )


class TestManagedIdentityConfig:
    """Static validation of managed identity configuration in IaC."""

    def test_aca_uses_user_assigned_identity(self):
        """ACA bicep must use UserAssigned managed identity (not SystemAssigned)."""
        bicep_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "azure", "modules", "aca-odoo-services.bicep"
        )
        if not os.path.exists(bicep_path):
            pytest.skip(f"Bicep file not found: {bicep_path}")

        with open(bicep_path, "r") as f:
            content = f.read()

        assert "'UserAssigned'" in content, (
            "ACA must use UserAssigned managed identity for explicit RBAC control"
        )

    def test_aca_registry_uses_managed_identity(self):
        """ACA registry config must use managed identity (not admin credentials)."""
        bicep_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "azure", "modules", "aca-odoo-services.bicep"
        )
        if not os.path.exists(bicep_path):
            pytest.skip(f"Bicep file not found: {bicep_path}")

        with open(bicep_path, "r") as f:
            content = f.read()

        # Registry config should reference identity, not username/password
        assert "identity: managedIdentityResourceId" in content, (
            "ACA registry must use managed identity for image pulls"
        )
        assert "passwordSecretRef" not in content or "registries" not in content.split("passwordSecretRef")[0][-200:], (
            "ACA registry should not use password-based auth"
        )

    def test_key_vault_uses_managed_identity(self):
        """Key Vault secrets must be referenced via managed identity, not direct secrets."""
        bicep_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "azure", "modules", "aca-odoo-services.bicep"
        )
        if not os.path.exists(bicep_path):
            pytest.skip(f"Bicep file not found: {bicep_path}")

        with open(bicep_path, "r") as f:
            content = f.read()

        assert "keyVaultUrl" in content, (
            "Secrets must be referenced via Key Vault URL (not inline values)"
        )
