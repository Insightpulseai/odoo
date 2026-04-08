# Constitution — Entra Identity Migration

> Non-negotiable rules governing the migration from Keycloak to Microsoft Entra ID across the IPAI platform.

---

## C1: Greenfield Implementation, Not Migration

Keycloak (`ipai-auth-dev`) was deployed but **never operationalized** — no apps are actively authenticating through it. This means Entra ID is the first real IdP implementation, not a migration from a working Keycloak setup.

Implementation is sequenced per application. Each app must independently validate OIDC flow, group/role mapping, and user provisioning before going live.

`ipai-auth-dev` can be decommissioned without migration gates since no apps depend on it.

## C2: Break-Glass Account is a Go-Live Blocker

A break-glass emergency access account must exist in Entra ID before any production app cutover begins. This account:
- Bypasses Conditional Access policies
- Uses FIDO2 or hardware OATH token (not SMS/phone)
- Is monitored for any sign-in activity
- Has credentials stored in a physical safe or Azure Key Vault with restricted access

No app cutover proceeds without evidenced break-glass account.

## C3: Conditional Access MFA is Mandatory for Admin Accounts

All human admin accounts must be enrolled in MFA via Conditional Access policy before any production app cutover. MFA methods:
- Microsoft Authenticator (preferred)
- OATH hardware/software tokens
- FIDO2 security keys

Temporary Access Pass (TAP) is allowed for initial enrollment only.

## C4: Managed Identities for Service-to-Service Auth

ACA container apps, cron jobs, and workers use Azure Managed Identities — not service account passwords or API keys stored in Keycloak.

Managed identities are governed by:
- Least-privilege RBAC
- Scoped resource access
- Key Vault controls
- Monitoring and audit logging

Managed identities are NOT subject to user MFA policies. They are governed through infrastructure controls.

## C5: Entra Agent ID is Preview-Gated

Entra Agent ID requires M365 Copilot + Frontier program. It is not available without these licenses.

Rules:
- Do not architect production agent identity flows on Entra Agent ID until GA or Frontier access is confirmed
- Design agent identity contracts to be portable: Entra Agent ID when available, managed identity + RBAC as fallback
- Agent Factory passports/blueprints must map cleanly to Entra Agent ID concepts (blueprint → agent identity blueprint, passport → agent identity instance)

## C6: Odoo Remains the Relying Party

Odoo authenticates users via OIDC. Entra ID is the identity provider. Odoo never stores primary passwords for users with an Entra counterpart.

The `ipai_auth_oidc` module handles:
- OIDC authorization code flow
- Token validation
- User provisioning/matching (email-based)
- Group/role sync from Entra ID claims

## C7: Clean Implementation — No Dual-IdP Complexity

Since Keycloak was never operationalized, there is no dual-IdP period. Each app goes from no-SSO (or basic auth) directly to Entra ID OIDC.

- No credential forwarding or proxying needed
- No Keycloak migration gates needed
- Rollback path: revert to basic Odoo login (for Odoo) or disable OIDC (for other apps)

## C8: Evidence Required for Each Gate

Every migration gate must produce an evidence artifact in `docs/evidence/<stamp>/entra-migration/`:
- Break-glass account creation proof
- CA policy configuration export
- MFA enrollment proof per admin
- Per-app OIDC test (login flow screenshot or curl evidence)
- Group/role mapping validation
- Provisioning test results

No gate is considered passed without evidence.

## C9: Plane, Superset, and n8n Use Standard OIDC

These apps support OIDC natively. Their migration is:
1. Register as enterprise app in Entra ID
2. Configure OIDC redirect URI
3. Map groups/roles from Entra claims
4. Test login flow
5. Disable Keycloak client for that app

No custom auth modules needed for these apps.

## C10: Agent Identity Layering

Two identity layers exist for AI agents:

| Layer | Current | Target |
|-------|---------|--------|
| Human operators | Keycloak OIDC | Entra ID OIDC + MFA |
| Agent workloads | Managed identities + API keys | Entra Agent ID (when GA) + managed identities (fallback) |

The agent identity layer does not block the human identity migration. They proceed independently.
