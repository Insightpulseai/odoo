# PRD — Platform Auth Architecture

> Product requirements for unified authentication and authorization across the InsightPulse AI platform.

---

## Problem

Multiple systems (Odoo, Supabase, Plane, Shelf, CRM, n8n, MCP, web apps, mobile) each handle authentication independently. This creates credential sprawl, inconsistent security posture, and no unified identity model.

## Goal

Establish a single, auditable auth architecture where:
- Users authenticate once (SSO) and access all apps
- Services authenticate via dedicated credentials with least privilege
- n8n operates strictly as a service actor, never as an identity provider
- All auth events are audited

## Scope

### In Scope

| System | Auth Model | Grant Type |
|--------|-----------|------------|
| Web apps (workspace, ops-console) | OIDC / OAuth 2.0 | Authorization code + PKCE |
| Mobile app | OAuth 2.0 | Authorization code + PKCE |
| Odoo | OIDC via Keycloak | `ipai_auth_oidc` module |
| n8n UI | SSO/OIDC (admin only) | Authorization code |
| n8n → systems | Service accounts | Client credentials, API tokens |
| MCP gateway | Multi-path Bearer | Supabase JWT, JWKS, opaque token |
| GitHub | App installation tokens | Signed webhooks |

### Out of Scope

- Implicit grant (banned)
- Password grant (banned)
- n8n as user-facing login surface
- Odoo as OAuth2 server for external apps

## Requirements

### R-1: SSO for Human Users

All user-facing applications MUST support SSO via Supabase Auth (direct) or Keycloak (brokered OIDC). Users sign in once and access Odoo, web workspace, ops-console, mobile, Plane, Shelf, and CRM.

### R-2: Service Auth for Automation

n8n, MCP services, CI/CD, and webhooks MUST authenticate using dedicated service credentials. One credential per target system per environment. Secrets stored in n8n credential store or container env vars — never in workflow JSON.

### R-3: n8n Auth Boundaries

- n8n UI: SSO/OIDC for admins/operators only
- n8n → Supabase: scoped keys or dedicated endpoints (service role only when strictly necessary)
- n8n → Odoo: dedicated integration user via XML-RPC/JSON-RPC
- n8n → Plane/Shelf/CRM: OAuth app or scoped API token
- n8n → Databricks: dedicated service principal (never personal PAT in production)
- n8n → GitHub: App installation token via `pulser-hub`

### R-4: Token Lifecycle

- Supabase JWT: short-lived access (1h), rotated refresh tokens
- Service tokens: long-lived, scoped, rotatable on schedule
- GitHub installation tokens: short-lived, auto-renewed
- Proactive token refresh before expiry (address gap in auth_session FSM)

### R-5: Audit Trail

All auth events logged to `auth.audit_log_entries` and/or `ops.platform_events`. Access reviews quarterly (org membership, service credentials). n8n credential store reviewed monthly.

### R-6: Secret Management

All secrets stored in one of: `.env` (local dev, gitignored), GitHub Actions secrets (CI), container env vars / Supabase Vault (runtime), n8n credential store (workflows). No other storage paths.

## Success Criteria

- [ ] All user-facing apps support SSO login
- [ ] n8n uses dedicated service credentials for every target system
- [ ] No shared human credentials in any automation workflow
- [ ] No implicit or password grants in any system
- [ ] Auth audit trail covers all systems
- [ ] Quarterly access reviews documented

## Dependencies

- Supabase Auth (live)
- Keycloak at auth.insightpulseai.com (live)
- `ipai_auth_oidc` module (live, disabled by default)
- ADR-007 multi-path Bearer validation (live)

## References

- `docs/architecture/AUTH_ARCHITECTURE.md`
- `docs/architecture/SSOT_BOUNDARIES.md`
- `docs/adr/ADR-007-n8n-mcp-auth-strategy.md`
- `docs/contracts/C-10_GITHUB_SSO_SAML_POLICY.md`
