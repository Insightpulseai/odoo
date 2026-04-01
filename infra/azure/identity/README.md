# Azure Identity

Entra ID configuration, managed identities, RBAC assignments, and app registrations.

## Architecture

- IdP: Microsoft Entra ID (tenant `402de71a`, P2 licensed)
- Odoo OAuth: `ipai_auth_oidc` module with Entra app `07bd9669`
- Managed identities for service-to-service auth
- Key Vault access via managed identity (no shared secrets)

## Convention

- All ACA apps use system-assigned managed identity
- RBAC assignments over access policies for Key Vault
- App registrations for OAuth/OIDC flows only
- No Keycloak (decommission candidate)

<!-- TODO: Add Bicep/ARM templates for identity resources -->
