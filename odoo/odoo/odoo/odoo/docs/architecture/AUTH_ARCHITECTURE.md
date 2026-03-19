# Auth Architecture — InsightPulse AI Platform

> Authoritative reference for authentication and authorization across all platform services.
> Extends: `SSOT_BOUNDARIES.md §1`, `ADR-007`, `C-10_GITHUB_SSO_SAML_POLICY.md`
> Last updated: 2026-03-08

---

## Design Principles

1. **One identity strategy, many integrated apps** — no system invents its own login model independently.
2. **Supabase Auth is the platform IdP** — all other systems are relying parties.
3. **Human auth ≠ machine auth** — users authenticate via SSO/OIDC; services authenticate via credentials/tokens.
4. **n8n is an automation engine, not an identity platform** — service-actor only.
5. **Least privilege per boundary** — scoped tokens, dedicated service accounts, no shared human credentials.

---

## Auth Model Progression (What We Use)

```
❌ basic auth          — never
❌ session-only        — not across systems (OK within Odoo for ERP sessions)
✅ JWT / token-based   — APIs, SPAs, distributed systems
✅ SSO / OIDC          — cross-app user identity
✅ OAuth 2.0           — delegated authorization
```

### Grant Types

| Grant | Use | Status |
|-------|-----|--------|
| Authorization Code + PKCE | Web apps, mobile apps, user login | **Primary** |
| Client Credentials | Server-to-server, n8n, MCP, automation | **Primary** |
| Implicit | — | **Banned** (legacy, insecure) |
| Password | — | **Banned** (legacy, insecure) |

---

## System Auth Map

### Identity Provider (SSOT)

```
┌─────────────────────────────────────────┐
│           Supabase Auth (IdP)           │
│                                         │
│  • User identities (UUID, email)        │
│  • Sessions + refresh tokens            │
│  • MFA (TOTP)                           │
│  • JWT signing (asymmetric)             │
│  • Social/OAuth federation              │
│  • SAML SSO                             │
│  • RBAC + RLS policies                  │
│  • Auth hooks + audit events            │
│  • Identity emails via Zoho SMTP        │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┼─────────┬──────────┬──────────┬──────────┐
    ▼         ▼         ▼          ▼          ▼          ▼
  Odoo      Web       Mobile    Plane      Shelf      CRM
  (RP)      Apps      App       (RP)       (RP)       (RP)
```

### Per-System Auth Configuration

#### Odoo (Relying Party)

```
Auth method:  OIDC via Keycloak (ipai_auth_oidc module)
Session:      Server-side session cookie (Odoo-internal)
IdP client:   Keycloak realm "insightpulse", client "ipai-odoo"
Fallback:     Local Odoo password (users without Supabase counterpart only)
```

**Rules:**
- Odoo CANNOT be an OAuth2 server for external apps
- Odoo CANNOT store primary passwords for Supabase-synced users
- Mirror contract: only `x_supabase_user_id`, `login`, `company_ids`, `groups_id` cross boundary
- See `SSOT_BOUNDARIES.md §1` for full mirror contract

#### Web Applications (workspace, ops-console, marketing)

```
Auth method:  OIDC / OAuth 2.0 authorization code + PKCE
Session:      Secure httpOnly cookie or Supabase session token
IdP:          Supabase Auth (direct)
```

**Rules:**
- Authorization code flow with PKCE — never implicit grant
- Server-side session management preferred over client-side JWT storage
- Refresh tokens stored securely (httpOnly cookie or secure storage)

#### Mobile App (iOS/Android)

```
Auth method:  OAuth 2.0 authorization code + PKCE
Session:      Secure device storage (Keychain / Keystore)
IdP:          Supabase Auth (direct)
```

**Rules:**
- PKCE mandatory — no implicit grant, no password grant
- Biometric unlock for session restoration (future)
- Token refresh handled by Supabase client SDK

#### Keycloak (Federation Broker)

```
Deployment:   auth.insightpulseai.com (self-hosted, DO droplet)
Realm:        insightpulse
Role:         Federation broker between Supabase Auth and legacy systems
Clients:      ipai-odoo, ipai-n8n (admin UI only)
```

**Rules:**
- Keycloak is NOT the primary IdP — Supabase Auth is
- Keycloak brokers OIDC for systems that need a traditional OIDC provider (Odoo)
- User management syncs from Supabase Auth → Keycloak → downstream

---

## Machine Auth (Service-to-Service)

### n8n — Automation Engine (Service Actor)

n8n is an **event/workflow orchestrator**. It is NOT:
- A primary login provider
- An SSO broker
- A source of truth for user identity

#### n8n UI Access

```
Auth method:  SSO / OIDC (if deployment tier supports it)
Fallback:     Tightly controlled internal auth
Users:        Admins, automation builders, operators only
```

Normal end users NEVER access n8n directly.

#### n8n → Target Systems

| Target | Auth Pattern | Credential Type |
|--------|-------------|-----------------|
| Supabase | Scoped keys / dedicated endpoints | Service role (sparingly), anon key + RLS |
| Odoo | Dedicated integration user | XML-RPC / JSON-RPC credentials |
| Plane | OAuth app or scoped API token | Per-environment token |
| Shelf | OAuth app or scoped API token | Per-environment token |
| CRM | OAuth app or scoped API token | Per-environment token |
| Databricks | Service principal / PAT | Dedicated integration principal |
| GitHub | GitHub App installation token | `pulser-hub` app (ID: 2191216) |
| Slack | Bot token | `xoxb-*` scoped token |

**Rules:**
- One dedicated service credential per target system per environment
- Secrets stored in n8n credential store (never in workflow JSON)
- No shared human credentials for automation
- Least privilege per workflow family
- Never use personal developer tokens as long-term production credentials
- Webhook secrets / signed requests for inbound triggers

#### n8n Workflow JSON Rules

```
✅ Use: {{ $credentials.<name>.<field> }}
✅ Use: {{ $env.<VAR_NAME> }}
❌ Never: literal passwords, API keys, or tokens in JSON
```

### MCP Services

```
Auth method:  Multi-path Bearer token validation (ADR-007)
Paths:        1. Supabase JWT  2. External JWKS  3. Opaque token lookup
Audit:        All requests logged to ops.run_events
```

### GitHub Integration

```
Auth method:  GitHub App installation tokens (pulser-hub)
Webhook:      Signed (X-Hub-Signature-256)
SSO:          SAML via Keycloak (when Enterprise tier active)
2FA:          Mandatory for all org members (C-10 policy)
```

---

## Auth Flow Diagrams

### User Login (Web/Mobile)

```
User                    App                 Supabase Auth        Keycloak (if needed)
  │                      │                       │                      │
  ├─── open app ────────►│                       │                      │
  │                      ├── redirect to login ──►                      │
  │                      │                       ├── show login form ───►
  │                      │                       │   (or federate)      │
  │◄─── enter creds ─────┤                       │                      │
  │                      │                       ├── validate ──────────►
  │                      │                       │◄── token ────────────┤
  │                      │◄── JWT + refresh ─────┤                      │
  │◄─── session ─────────┤                       │                      │
  │                      │                       │                      │
```

### n8n Workflow Execution (Machine Auth)

```
Trigger (webhook/cron/event)
  │
  ▼
n8n Workflow Engine
  │
  ├── Load credential ref from credential store
  │   (NEVER from workflow JSON)
  │
  ├── Authenticate to target system
  │   ├── Odoo: XML-RPC with integration user
  │   ├── Supabase: service role or scoped key
  │   ├── Plane: API token
  │   └── GitHub: App installation token
  │
  ├── Execute workflow steps
  │
  └── Audit log → ops.platform_events
```

---

## Secret Management

### Storage Layers

| Layer | Store | What Goes Here |
|-------|-------|----------------|
| Local dev | `.env` / `.env.local` (gitignored) | Dev-only credentials |
| CI/CD | GitHub Actions secrets | Build/test credentials |
| Runtime | Container env vars, Supabase Vault | Production credentials |
| n8n | n8n credential store | Workflow credentials |
| Keycloak | Realm client secrets | OIDC client secrets |

### Rules (Non-Negotiable)

- Secrets NEVER committed to git (except `*.example` for names only)
- Secrets NEVER echoed in CI logs
- Secrets NEVER in n8n workflow JSON exports
- Secrets NEVER passed as URL query parameters
- When a secret is missing: state the env var name + expected source, nothing more

---

## Token Lifecycle

### Supabase JWT

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Authenticate │────►│ Authenticated│────►│  Refreshing  │
│              │     │  (JWT valid) │     │              │
└──────────────┘     └──────┬───────┘     └──────┬───────┘
                            │                     │
                     ┌──────▼───────┐     ┌──────▼───────┐
                     │   Expired    │     │    Error     │
                     └──────────────┘     └──────────────┘
```

- Access token: short-lived (default 1 hour)
- Refresh token: long-lived, rotated on use
- Proactive refresh: recommended before expiry (gap identified in auth_session FSM)
- Revocation: via Supabase Auth API or session invalidation

### Service Tokens

- API keys: long-lived, scoped, rotatable
- Installation tokens (GitHub): short-lived, auto-renewed
- OAuth tokens: per-grant lifecycle, refresh where supported

---

## Compliance & Audit

### Audit Trail

All auth events logged to:
- `auth.audit_log_entries` (Supabase — identity events)
- `ops.platform_events` (Supabase — cross-system events)
- Odoo `ir.logging` (ERP-specific auth events)

### Access Review Cadence (C-10)

| Review | Frequency |
|--------|-----------|
| Org membership | Quarterly |
| Service credentials | Quarterly |
| n8n credential store | Monthly |
| GitHub 2FA compliance | Continuous |

---

## Anti-Patterns (Banned)

| Pattern | Why |
|---------|-----|
| Every system invents its own login | Fragmented identity, credential sprawl |
| n8n as user login surface | n8n is automation, not end-user app |
| Implicit grant (OAuth) | Insecure, deprecated in OAuth 2.1 |
| Password grant (OAuth) | Exposes credentials to client apps |
| Shared human creds for automation | No audit trail, no least privilege |
| Personal dev tokens in production | Single point of failure, no rotation |
| Raw session-only across all systems | Doesn't scale for APIs/mobile/services |
| Basic auth for anything external | Credentials in every request |

---

## Implementation Status

| System | Auth Method | Status |
|--------|------------|--------|
| Supabase Auth (IdP) | JWT + sessions + MFA | **Live** |
| Keycloak | OIDC broker | **Live** (auth.insightpulseai.com) |
| Odoo OIDC | `ipai_auth_oidc` module | **Live** (disabled by default) |
| Web apps | Supabase Auth direct | **Scaffolded** |
| Mobile app | Authorization code + PKCE | **Planned** |
| n8n UI SSO | OIDC via Keycloak | **Planned** |
| n8n service auth | Credential store | **Live** |
| MCP gateway | Multi-path Bearer (ADR-007) | **Live** |
| GitHub SAML SSO | Keycloak federation | **Planned** (needs Enterprise tier) |

---

## Related Documents

| Document | Path |
|----------|------|
| SSOT Boundaries | `docs/architecture/SSOT_BOUNDARIES.md` |
| ADR-007: MCP Auth | `docs/adr/ADR-007-n8n-mcp-auth-strategy.md` |
| GitHub SSO Policy | `docs/contracts/C-10_GITHUB_SSO_SAML_POLICY.md` |
| Supabase Auth SMTP | `docs/contracts/SUPABASE_AUTH_SMTP_CONTRACT.md` |
| Mail Architecture | `docs/contracts/MAIL_ARCHITECTURE_CONTRACT.md` |
| Auth Session FSM | `docs/state_machines/scout/auth_session.md` |
| Auth/JWT Runbook | `docs/runbooks/supabase/auth_jwt.md` |
| Keycloak Deployment | `docs/KEYCLOAK_IDENTITY_PROVIDER_DEPLOYMENT.md` |
