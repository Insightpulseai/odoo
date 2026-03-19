# Constitution — Platform Auth

> Non-negotiable rules for authentication and authorization across the InsightPulse AI platform.

---

## C-1: Single Identity Provider

Supabase Auth is the SSOT for user identity. No other system may act as a primary identity provider.

## C-2: Relying Party Boundaries

Odoo, Plane, Shelf, CRM, and all web/mobile apps are relying parties. They consume identity — they do not produce it.

## C-3: Human vs Machine Auth Separation

- **Humans** authenticate via SSO/OIDC/OAuth 2.0 authorization code + PKCE.
- **Machines** (n8n, MCP, CI, webhooks) authenticate via service accounts, client credentials, scoped tokens, or signed webhooks.
- These two paths MUST NOT be conflated.

## C-4: n8n is a Service Actor

n8n authenticates TO systems as a service actor. Users do NOT use n8n as the main login surface. n8n is NOT an SSO broker, NOT a user identity source, NOT an end-user app shell.

## C-5: Banned Grant Types

- Implicit grant: BANNED (insecure, deprecated in OAuth 2.1).
- Password grant: BANNED (exposes credentials to client apps).

## C-6: One Credential Per System Per Environment

Each service-to-service integration uses a dedicated credential per target system per environment. No shared human credentials for automation. No personal developer tokens in production.

## C-7: Secrets Never Cross Boundaries in Plaintext

Secrets are never committed to git, echoed in CI logs, included in n8n workflow JSON, or passed as URL query parameters. See `SSOT_BOUNDARIES.md` and `docs/architecture/AUTH_ARCHITECTURE.md`.

## C-8: Keycloak is Federation Broker, Not Primary IdP

Keycloak brokers OIDC for systems that need a traditional OIDC provider (e.g., Odoo). It is NOT the primary identity provider — Supabase Auth is.

## C-9: Audit All Auth Events

All authentication and authorization events must be logged to `auth.audit_log_entries` (Supabase) or `ops.platform_events`. No silent auth failures.
