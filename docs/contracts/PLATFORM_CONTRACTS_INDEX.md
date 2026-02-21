# Platform Contracts Index — InsightPulse AI

> A contract defines what crosses a boundary between two SSOT domains.
> Every contract has an owning SSOT, a consuming party, and a validation mechanism.
> Contracts marked **[pending]** have no committed document yet.
>
> Last updated: 2026-02-21

---

## Index

| # | Contract | Source SSOT domain | Consumer domain | Status | Validator |
|---|----------|--------------------|----------------|--------|-----------|
| C-01 | [DNS & Email](DNS_EMAIL_CONTRACT.md) | Cloudflare DNS (`infra/dns/`) | Zoho Mail, Vercel, Odoo | ✅ Active | `dns-ssot-apply.yml` |
| C-02 | [Outbound Mail Bridge](MAIL_BRIDGE_CONTRACT.md) | Odoo `mail.mail` | Supabase Edge Function `zoho-mail-bridge` | ✅ Active | `ipai-custom-modules-guard.yml` |
| C-03 | [JWT Trust](JWT_TRUST_CONTRACT.md) | Supabase Auth | Odoo middleware, Vercel Edge | 🔲 Pending | — |
| C-04 | [Task Queue](TASK_QUEUE_CONTRACT.md) | n8n workflows | `ops.task_queue` (Supabase) | 🔲 Pending | — |
| C-05 | [Design Tokens](DESIGN_TOKENS_CONTRACT.md) | Figma | `packages/design-tokens/tokens.json` | 🔲 Pending | — |
| C-06 | [Vercel Environment Variables](VERCEL_ENV_CONTRACT.md) | Vercel dashboard | Next.js apps | 🔲 Pending | `vercel-env-leak-guard.yml` |
| C-07 | [Supabase Vault Secrets](VAULT_SECRETS_CONTRACT.md) | Supabase Vault | Edge Functions, CI | 🔲 Pending | `platform-guardrails.yml` |
| C-08 | [Platform Audit Events](AUDIT_EVENTS_CONTRACT.md) | All services | `ops.platform_events` (Supabase) | 🔲 Pending | — |
| C-09 | [GitHub Actions Secrets](GH_SECRETS_CONTRACT.md) | GitHub org secrets | CI workflows | 🔲 Pending | `platform-guardrails.yml` |

---

## C-01 — DNS & Email Contract

**File**: `docs/contracts/DNS_EMAIL_CONTRACT.md`
**SSOT**: `infra/dns/subdomain-registry.yaml` + `infra/dns/zoho_mail_dns.yaml`
**Consumers**: Cloudflare (via Terraform), Zoho Mail SPF/DKIM, Vercel alias, Odoo `web.base.url`

**Invariants**:
- A subdomain must exist in `subdomain-registry.yaml` before any service uses it.
- SPF, DKIM, DMARC records live in `zoho_mail_dns.yaml` — never in the main registry.
- Terraform apply is the only valid way to push records to Cloudflare.

**Validator**: `dns-ssot-apply.yml` (path-triggered on `infra/dns/**`)

---

## C-02 — Outbound Mail Bridge Contract

**File**: `docs/contracts/MAIL_BRIDGE_CONTRACT.md` *(this section is the canonical definition)*
**SSOT**: `addons/ipai/ipai_mail_bridge_zoho/` (Odoo side) + `supabase/functions/zoho-mail-bridge/` (bridge side)
**Consumer**: Any Odoo `mail.mail` record with `state=outgoing`

**Protocol**:
```
POST <ZOHO_MAIL_BRIDGE_URL>?action=send_email
Headers:
  x-bridge-secret: <ZOHO_MAIL_BRIDGE_SECRET>   ← 32+ char random shared secret
  Content-Type: application/json
Body:
  { from, to, subject, htmlBody?, textBody?, replyTo? }
Response (200 OK):
  { ok: true }
Response (error):
  { ok: false, code: ErrorCode, message: string }
  ErrorCodes: UNAUTHORIZED | BAD_REQUEST | METHOD_NOT_ALLOWED | NOT_FOUND | SERVICE_ERROR | NOT_CONFIGURED
```

**Env vars (Odoo container)**:
- `ZOHO_MAIL_BRIDGE_URL` — Supabase Edge Function URL
- `ZOHO_MAIL_BRIDGE_SECRET` — 32+ char random secret (NOT the Supabase anon key)

**Env vars (Supabase Vault)**:
- `BRIDGE_SHARED_SECRET` — must match `ZOHO_MAIL_BRIDGE_SECRET`
- `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN`, `ZOHO_ACCOUNT_ID`

**Fallback behavior**: If `ZOHO_MAIL_BRIDGE_URL` or `ZOHO_MAIL_BRIDGE_SECRET` is absent, Odoo falls back to standard SMTP (`smtppro.zoho.com:587`). Note: this port is blocked on DigitalOcean droplets.

**Audit trail**: Every `send_email` call is audited to `ops.platform_events` (actor: `zoho-mail-bridge`).

**[MANUAL_REQUIRED]** Zoho OAuth2 credentials must be set in Supabase Vault before `send_email` works:
```bash
supabase secrets set --project-ref spdtwktxdalcfigzeqrz \
  ZOHO_CLIENT_ID=<from Zoho API Console> \
  ZOHO_CLIENT_SECRET=<from Zoho API Console> \
  ZOHO_REFRESH_TOKEN=<from OAuth2 flow> \
  ZOHO_ACCOUNT_ID=<from /api/accounts>
```

---

## C-03 — JWT Trust Contract [pending]

**File**: `docs/contracts/JWT_TRUST_CONTRACT.md` *(not yet created)*

**Purpose**: Define how Odoo (Python/Werkzeug middleware) validates Supabase-issued JWTs.

**Key fields to specify**:
- JWKS endpoint URL
- Audience (`aud`) claim expected value
- Issuer (`iss`) claim
- Required scopes / roles
- Token expiry handling (`jwt_expiry = 3600` in `supabase/config.toml`)

**Consumers**: Odoo session middleware (`ipai_auth_oidc`), Vercel Edge middleware

---

## C-04 — Task Queue Contract [pending]

**File**: `docs/contracts/TASK_QUEUE_CONTRACT.md` *(not yet created)*

**Purpose**: Define the schema of `ops.task_queue` (Supabase) and the n8n → queue → consumer flow.

**Key fields**: `task_type`, `payload`, `status`, `created_at`, `processed_at`, `error`

---

## C-05 — Design Tokens Contract [pending]

**File**: `docs/contracts/DESIGN_TOKENS_CONTRACT.md` *(not yet created)*

**Purpose**: Define the schema of `packages/design-tokens/tokens.json` and the Figma → export → commit flow.

---

## Contract Governance

### Adding a new contract

1. Create `docs/contracts/<NAME>_CONTRACT.md` with:
   - Source SSOT domain
   - Consumer domain
   - Protocol / schema
   - Invariants
   - Validator (CI workflow or script)
2. Add a row to the Index table above.
3. Add a path guard to `.github/workflows/ssot-surface-guard.yml`.

### Contract validation levels

| Level | Meaning |
|-------|---------|
| ✅ Active | Contract doc exists + CI enforces it |
| ⚠️ Partial | Contract doc exists but CI enforcement missing |
| 🔲 Pending | Contract conceptually defined here; no separate doc yet |
| ❌ Violated | Known violation — must be remediated |
