# SSOT Boundaries — InsightPulse AI Platform

> This document is the authoritative definition of which system owns which concern.
> When two systems could each claim ownership of a datum, this file decides.
> Last updated: 2026-02-21

---

## Boundary Map

| Domain | SSOT | Relying Party / SOR | Mirror Contract |
|--------|------|---------------------|-----------------|
| **Identity & Access** | Supabase Auth | Odoo (`res.users`) | Minimal projection only — see §1 |
| **Mail Configuration** | `config/odoo/mail_settings.yaml` | Odoo `ir.mail_server` / `fetchmail.server` | Applied by `apply_mail_settings.py` |
| **DNS Records** | `infra/dns/subdomain-registry.yaml` + `infra/dns/zoho_mail_dns.yaml` | Cloudflare | Via Terraform |
| **Secrets** | Supabase Vault + container env vars | Odoo conf, Edge Functions | Never committed |
| **ERP Data** | Odoo PostgreSQL (`odoo_prod`) | Supabase (read-only projections) | Bridge functions only |
| **Automation Workflows** | n8n (live instance) + `automations/n8n/` JSON | Supabase task queue | Deployed via `deploy_n8n_all.py` |
| **Module Code** | `addons/ipai/` (OCA-style) | Odoo runtime | Installed via `odoo -i <module>` |
| **Specs / Contracts** | `spec/<feature>/` (spec-kit) | CI, agent instructions | Enforced by `spec_validate.sh` |
| **Platform Events / Audit** | `ops.platform_events` (Supabase) | All services append | Append-only, no deletes |

---

## §1 — Identity & Access: Supabase Auth is SSOT

### Supabase owns

- User identities (UUID, email, phone)
- Sessions and refresh tokens
- MFA methods and state
- Social / OAuth provider links
- SAML SSO federation
- JWT signing keys (asymmetric)
- RBAC roles and grants
- Row-Level Security policies (Postgres)
- Auth hooks and audit events

### Odoo is a relying party

Odoo is **not** an identity provider. It cannot:
- Store primary passwords (only hashed Odoo-internal passwords for users who have no Supabase counterpart)
- Act as an OAuth2 server for external apps
- Be the primary session authority

### Mirror contract — what crosses the boundary

Only these fields may be written from Supabase → Odoo:

| Supabase field | Odoo field | Notes |
|----------------|-----------|-------|
| `auth.users.id` (UUID) | `res.users.x_supabase_user_id` | Linkage key |
| `auth.users.email` | `res.users.login` / `res.partner.email` | Kept in sync |
| Org / company ID | `res.users.company_ids` | Derived from Supabase org membership |
| Role label | `res.users.groups_id` (via bridge) | Mapped, not authoritative |

**Explicitly forbidden from mirroring:**
- Passwords, MFA factors, sessions, tokens
- Social identity provider metadata
- Raw JWT claims

### Provisioning rule

| User type | Provisioned when | By what |
|-----------|-----------------|---------|
| Internal ERP user | On-demand only (admin action or Edge Function hook) | Auth hook → `supabase/functions/provision-odoo-user` |
| Portal / external user | Never auto-provisioned in Odoo | Odoo portal disabled by default |
| Service account | Pre-seeded in `scripts/odoo/` bootstrap | No Supabase counterpart |

### Identity emails (Invites / Reset / Magic Links)

**SSOT Owner:** Supabase Auth
**Email Provider:** Zoho SMTP (configured in Supabase Auth SMTP settings)
**Contract:** `docs/contracts/SUPABASE_AUTH_SMTP_CONTRACT.md`

**Odoo MUST NOT send invitation or identity lifecycle emails.**
Odoo only receives user projections when ERP access is required (on-demand provisioning).
The `ipai_mail_bridge_zoho` addon is for ERP document email (invoices, POs, CRM) — not identity.

| Email type | Sent by | Provider |
|-----------|---------|---------|
| User invitation | Supabase Auth | Zoho SMTP (`smtppro.zoho.com:587`) |
| Password reset | Supabase Auth | Zoho SMTP |
| Magic link / OTP | Supabase Auth | Zoho SMTP |
| Invoice / PO / ERP document | Odoo (`ipai_mail_bridge_zoho`) | Zoho Mail API (HTTPS bridge) |
| Catchall / inbound | Zoho Mail | n/a |

---

## §2 — Mail: YAML is SSOT, Odoo DB is derived

```
config/odoo/mail_settings.yaml          ← SSOT (edit this)
        │
        ▼
scripts/odoo/apply_mail_settings.py     ← idempotent applier
        │
        ▼
Odoo DB: ir_mail_server, fetchmail_server  ← derived (SOR for sending)
```

**Rule:** Any manual change in Odoo Settings → Email must be reflected back to YAML. The YAML is truth. The DB row is a cache.

**Canonical endpoints (US DC):**

| Protocol | Host | Port | Encryption |
|----------|------|------|------------|
| SMTP | `smtppro.zoho.com` | 587 | STARTTLS |
| IMAP | `imappro.zoho.com` | 993 | SSL/TLS |

**Never use** `smtp.zoho.com` or `imap.zoho.com` for `@insightpulseai.com` — those are global endpoints and fail auth for the US datacenter account.

---

## §3 — Secrets: Never in Git

| Secret | Storage | Access pattern |
|--------|---------|---------------|
| Zoho SMTP App Password | Container env var `ZOHO_SMTP_APP_PASSWORD` | Injected at container start |
| Zoho IMAP App Password | Container env var `ZOHO_IMAP_APP_PASSWORD` | Injected at container start |
| Zoho OAuth2 client_id/secret/refresh_token | Supabase Vault → Edge Function secrets | `Deno.env.get()` |
| Odoo admin password | Container env var `ODOO_ADMIN_PASSWORD` | Injected at container start |
| DB password (`doadmin`) | Container CMD arg (DigitalOcean managed) | `docker inspect` — never log |
| Supabase service role key | GitHub Actions secret + Vault | Never in files |

**Log hygiene rule:** Scripts must print only `host`, `port`, `user`, `PASS/FAIL`. Never print a token, password, or key — even partially.

---

## §4 — Supabase Auth Feature Adoption Plan

Features to adopt (in priority order):

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Email login | P0 | Enabled | Used for platform apps |
| Magic links | P0 | Enabled | Default passwordless |
| MFA (TOTP) | P1 | Pending | Add to internal users |
| Social login (GitHub, Google) | P1 | Pending | For dev self-service |
| Auth hooks | P1 | Pending | Trigger Odoo provisioning |
| RBAC + RLS | P1 | Partial | Migration pending |
| Third-party JWT trust | P2 | Pending | For Odoo ↔ Supabase trust |
| SSO with SAML | P2 | Pending | Needs Supabase Pro |
| OAuth 2.1 Server | P3 | Pending | Turn Supabase into IdP |
| JWT signing keys (asymmetric) | P1 | Pending | Harden JWT validation |
| Captcha protection | P2 | Pending | Sign-up flows |
| Custom domains | P2 | Pending | White-label auth endpoints |
| **Phone OTP login (SMS)** | P2 | Pending | Requires messaging provider (Twilio / MessageBird) |
| **Phone OTP login (WhatsApp)** | P3 | Pending | WhatsApp OTP only via Twilio / Twilio Verify — same provider config as Phone MFA |

### §4.1 — Phone OTP Login

Phone OTP (passwordless) is an additional **credential channel** for Supabase Auth — not a separate IdP.

```
User enters phone  →  Supabase signInWithOtp({ phone, channel: 'sms'|'whatsapp' })
                                    │
                             messaging provider sends OTP
                                    │
User enters token  →  Supabase verifyOtp({ phone, token, type: 'sms' })
                                    │
                              session JWT issued
                                    │
                           RLS-protected queries work normally
```

**Constraints to codify before enabling**:

| Constraint | Detail |
|------------|--------|
| WhatsApp OTP | Only supported via **Twilio / Twilio Verify** providers |
| SMS OTP | Supported via Twilio, MessageBird, Vonage, and others |
| Shared provider config | Messaging provider config (Twilio creds) powers **both** Phone OTP login and Phone MFA — one config, two use-cases |
| PK-less users | Phone-only users have no email — Odoo projection must handle `null` email gracefully |
| Rate limits | Supabase applies per-IP and per-phone rate limiting — add Edge Function rate-limit wrapper if exposed publicly |

**When to enable (decision criteria)**:
- Phone login is appropriate when users onboard **without email** (mobile-first flow).
- If the only requirement is **sending invitations**, phone login is out of scope — use email + Zoho SMTP bridge.

**Implementation scope** (deferred — consumer not yet identified):
- `phone_login.ts` helper: `signInWithOtp` + `verifyOtp` + session validation
- Rate-limit guard at Edge Function boundary for public-facing flows
- Test plan: OTP request succeeds → OTP verify yields JWT → RLS query passes

**Blocked on**: consumer app identification (Odoo portal / Vercel Next.js / n8n-only).

---

## §5 — CI Enforcement

### Path guards (to be added)

| PR pattern | Allowed paths | Blocked if outside |
|-----------|---------------|-------------------|
| `zoho-bridge` title | `addons/ipai/ipai_zoho_mail/**`, `config/odoo/mail_settings.yaml`, `scripts/odoo/apply_mail_settings.py`, `infra/dns/zoho_mail_dns.yaml`, `docs/contracts/DNS_EMAIL_CONTRACT.md`, `supabase/*/zoho-mail-bridge/**`, `spec/zoho-mail-bridge/**`, `infra/supabase/vault_secrets.tf` | Anything else |
| `auth` title | `supabase/migrations/*auth*`, `supabase/functions/*auth*`, `spec/*auth*`, `docs/architecture/SSOT_BOUNDARIES.md` | Odoo addons, n8n |

---

## §6 — ETL / OLAP Replication: Supabase Postgres remains SSOT

### Rule: ETL destinations are analytics replicas, not authoritative sources

Supabase ETL (CDC via Postgres WAL / logical replication) copies data from the OLTP database into
analytics destinations. The copied data is **never** the source of truth.

```
Supabase Postgres (SSOT/OLTP)
         │
         │  CDC via logical replication (WAL)
         │  append-only changelog + cdc_operation column
         ▼
Analytics Destination (read-only replica)
  • Analytics Buckets (Iceberg) — Supabase-native, first-class
  • BigQuery — external, for heavy cross-system OLAP
         │
         ▼
BI Tools (Superset, Tableau, etc.)  — never write back
```

### Invariants

| Rule | Rationale |
|------|-----------|
| No write-backs from analytics → SSOT | ETL destinations are append-only replicas; writes must go through Odoo or Supabase edge functions |
| Only explicit pipelines may sync analytics → SSOT | Feedback loops (e.g. enriched labels) require a formal pipeline with audit trail in `ops.platform_events` |
| ETL outputs are non-authoritative | A BigQuery row or Iceberg file is evidence of what happened, not a system of record |
| Schema changes require migration first | ETL has limited DDL support; structural changes must land in Supabase migration before ETL can replicate them |

### What should be replicated

| Source table / schema | Destination | Rationale |
|-----------------------|-------------|-----------|
| `ops.platform_events` | Analytics Buckets | Compliance audit history without OLTP pressure |
| `ops.repo_hygiene_runs/findings` | Analytics Buckets | Historical hygiene trends for dashboards |
| Odoo → Supabase projections (invoices, tasks) | Analytics Buckets / BigQuery | OLAP queries, Superset dashboards |

### What must NOT be replicated

| Data | Reason |
|------|--------|
| `vault.secrets` / `vault.decrypted_secrets` | Secrets never leave Vault |
| `auth.users` (raw) | PII; replicate only derived/anonymized projections |
| Supabase internal schema tables | System tables, not application data |

### Contract

Full operational policy: `docs/contracts/SUPABASE_ETL_CONTRACT.md` (C-14)

### Secret scan gate

CI must run `git log -p | grep -E "password|secret|token" | grep -v placeholder` and fail if real-looking secrets are in the diff.

---

## §6 — Tasks to Implement This Contract

### Auth SSOT tasks

- [ ] `x_supabase_user_id` field on `res.users` (migration + `ipai_auth_oidc`)
- [ ] Edge Function `provision-odoo-user`: idempotent create-or-update `res.users` on Supabase signup hook
- [ ] Auth hook wired in Supabase dashboard (signup → `provision-odoo-user`)
- [ ] RBAC tables + RLS baseline migration (`supabase/migrations/YYYYMMDD_rbac_baseline.sql`)
- [ ] MFA enforced for `@insightpulseai.com` internal users
- [ ] Third-party JWT trust configured (Supabase JWT secret → Odoo `server_env_ir_actions_server` or middleware)

### Mail SSOT tasks

- [ ] `apply_mail_settings.py --env prod --verify` added to CI smoke test
- [ ] Zoho DKIM TXT value retrieved from Zoho Admin and committed to `infra/dns/zoho_mail_dns.yaml` (replaces placeholder)
- [ ] IMAP App Password generated for `catchall@insightpulseai.com` and stored in container env

### Governance tasks

- [ ] PR path guard CI added (`.github/workflows/pr-scope-guard.yml`)
- [ ] Secret scan gate added to pre-commit or CI

---

## §7 — Supabase Control Plane: Cloud Console is SSOT

The Supabase project `spdtwktxdalcfigzeqrz` is the authoritative control plane for:

| Concern | SSOT location | Committed artifact |
|---------|---------------|--------------------|
| Edge Function code | `supabase/functions/<name>/index.ts` | Git (SSOT) |
| Edge Function config (`verify_jwt`) | `supabase/config.toml` `[functions.<name>]` | Git (SSOT) |
| Vault secrets | Supabase Vault (cloud console) | `infra/supabase/vault_secrets.tf` (names only, not values) |
| Database migrations | `supabase/migrations/*.sql` (sequential) | Git (SSOT) |
| RLS policies | `supabase/migrations/` SQL files | Git (SSOT) |
| Auth config (JWT expiry, redirects) | `supabase/config.toml` `[auth]` | Git (SSOT) |
| Realtime subscriptions | Application code (`supabase-js`) | Git (SSOT) |

**Rules:**
- Never create Edge Functions or migrations via the Supabase dashboard UI — Git is SSOT.
- Vault secret **names** live in `infra/supabase/vault_secrets.tf`; **values** never in git.
- `supabase/config.toml` `[db].major_version` must be `15` (Supabase cloud PG version).
- `deploy --no-verify-jwt` is the default for internal bridge functions; public-facing functions must set `verify_jwt = true`.

---

## §8 — n8n Automation: JSON exports are SSOT

| Concern | SSOT location | Sync mechanism |
|---------|---------------|----------------|
| Workflow definitions | `automations/n8n/workflows/<name>.json` | `scripts/automations/deploy_n8n_all.py` |
| Credential definitions (names only) | `automations/n8n/credentials/` YAML manifests | Never synced — manual credential entry |
| n8n instance config | n8n env vars (container) | Not in Git |
| Workflow execution logs | n8n DB (not in Git) | — |

**Rules:**
- Workflow JSON files must be exported from live n8n and committed here before any structural change.
- `deploy_n8n_all.py --dry-run` before `--apply` (CI runs audit-only; no apply).
- Credentials are **never** stored in JSON — they are environment references (`{{ $credentials.zoho_smtp }}`).
- Stale workflows (no execution in 90+ days) must be archived under `automations/n8n/workflows/archive/`.
- Secret scan: n8n JSON exports must not contain literal passwords, tokens, or API keys.

---

## §9 — Vercel Edge: `vercel.json` + framework config is SSOT

| Concern | SSOT location | Notes |
|---------|---------------|-------|
| Route rewrites / headers | `vercel.json` (per app) | Never edit via dashboard |
| Environment variable names | `vercel.json` `env` block (names only) | Values set via Vercel dashboard or CLI |
| Environment variable values | Vercel dashboard / `vercel env pull` (local only) | Never in Git |
| Build output config | `next.config.*` / framework file | Git (SSOT) |
| Custom domains | `vercel.json` `alias` block | Mirrors Cloudflare CNAME |

**Rules:**
- `vercel.json` is the SSOT for routing; dashboard overrides must be reverted.
- Environment variable **values** must never appear in `vercel.json` or any committed file.
- The `vercel-env-leak-guard.yml` CI workflow enforces this at PR time.
- Domain assignments: Cloudflare DNS YAML is SSOT; `vercel.json` `alias` is derived.

---

## §10 — Figma Design: Component library is SSOT for design tokens

| Concern | SSOT location | Sync mechanism |
|---------|---------------|----------------|
| Design tokens (colors, spacing, typography) | Figma file (canonical) | `scripts/design/export_tokens.sh` → `packages/design-tokens/` |
| Component specs | Figma file | Manual reference only — no auto-sync |
| Brand assets (logos, icons) | `packages/assets/` | Committed after Figma export |

**Rules:**
- `packages/design-tokens/tokens.json` is the **repo-committed** SSOT; Figma is the upstream authority.
- Never hand-edit `tokens.json` — re-run `export_tokens.sh` and commit the diff.
- Icons added to Figma must be exported as SVG and committed to `packages/assets/icons/` before use in code.

---

## §11 — DigitalOcean Infrastructure: Terraform + compose files are SSOT

| Concern | SSOT location | Notes |
|---------|---------------|-------|
| Droplet provisioning | `infra/terraform/` | Terraform state in DO |
| Container orchestration | `deploy/odoo-prod.compose.yml` | Git (SSOT) |
| Droplet env vars | Container env block in compose file | Sensitive values: not in Git |
| App Platform apps | `infra/do/` YAML specs | Applied via `doctl apps update` |
| Firewall rules | `infra/terraform/firewall.tf` | Git (SSOT) |
| Volumes / snapshots | DO console + Terraform state | Terraform state file not in Git |

**Rules:**
- No manual droplet changes via DO console — use Terraform or compose file.
- Sensitive env vars in compose files use `${VAR_NAME}` expansion; actual values are set on the host or via secrets manager.
- Compose file changes must be applied with `docker-compose -f <file> --project-name deploy up -d --force-recreate <service>`.
- SMTP ports 25, 465, 587 are blocked by DO; route all outbound mail via HTTPS bridge (`ipai_mail_bridge_zoho`).

---

## §12 — Cloudflare DNS/CDN: `infra/dns/subdomain-registry.yaml` is SSOT

This extends the Boundary Map entry. Full workflow:

```
infra/dns/subdomain-registry.yaml     ← edit this ONLY
        │
        ▼
scripts/generate-dns-artifacts.sh     ← regenerates derived files
        │
        ├─► infra/cloudflare/envs/prod/subdomains.auto.tfvars
        ├─► docs/architecture/runtime_identifiers.json
        └─► infra/dns/dns-validation-spec.json
                │
                ▼
        CI: dns-sync-check.yml        ← fails if artifacts are out of sync
                │
                ▼
        Terraform apply               ← applies to Cloudflare API
```

**Rules:**
- Never edit `*.auto.tfvars` or `runtime_identifiers.json` directly — regenerate from YAML.
- Never add DNS records via Cloudflare dashboard — they will be overwritten by Terraform.
- DKIM / SPF / DMARC records live in `infra/dns/zoho_mail_dns.yaml` (separate SSOT for mail DNS).
- CI enforces sync: `dns-ssot-apply.yml` validates on every PR touching `infra/dns/`.

---

## §13 — GitHub Enterprise: `.github/` directory is SSOT

| Concern | SSOT location | Notes |
|---------|---------------|-------|
| CI/CD workflows | `.github/workflows/` | Git (SSOT) — 153+ workflows |
| Branch protection rules | `.github/settings.yml` (if using github-settings bot) | Or manual (document in `docs/ai/GITHUB.md`) |
| Required status checks | Workflow names → branch protection | Must match workflow `name:` field |
| GitHub Apps config | GitHub org settings (not in Git) | Document in `docs/ai/GITHUB.md` |
| Secrets / variables | GitHub Actions secrets (not in Git) | Names listed in `docs/ai/CI_WORKFLOWS.md` |
| Issue / PR templates | `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md` | Git (SSOT) |

**Rules:**
- Workflow file names are canonical IDs — rename only with a deprecation comment.
- Never disable a required status check without updating the corresponding workflow.
- GitHub secrets names must be documented in `docs/ai/CI_WORKFLOWS.md` (values never in Git).
- All new CI gates must be idempotent: a passing baseline must not trigger a false positive on the first run.

---

## §14 — Cross-Domain Contract Objects

These objects cross SSOT boundaries and require explicit mirror contracts:

| Object | Source SSOT | Consumer | Contract doc | Sync mechanism |
|--------|------------|----------|-------------|----------------|
| Supabase JWT | Supabase Auth | Odoo (middleware), Vercel (Edge middleware) | `docs/contracts/JWT_TRUST_CONTRACT.md` (pending) | JWT signing key published via JWKS endpoint |
| Outbound email | `ipai_mail_bridge_zoho` (Odoo → bridge) | Zoho Mail API | `docs/contracts/DNS_EMAIL_CONTRACT.md` | HTTPS POST with `x-bridge-secret` |
| DNS record set | `infra/dns/subdomain-registry.yaml` | Cloudflare, Vercel alias, Odoo `web.base.url` | `docs/contracts/DNS_EMAIL_CONTRACT.md` | Terraform apply |
| n8n → Supabase task queue | n8n workflows | `ops.task_queue` (Supabase) | `docs/contracts/TASK_QUEUE_CONTRACT.md` (pending) | REST POST to Supabase Edge Function |
| Odoo → Supabase audit events | Odoo (hooks) + Edge Functions | `ops.platform_events` | §1 this doc | Append-only INSERT |
| Design tokens | Figma (canonical) | `packages/design-tokens/tokens.json`, Tailwind, MUI | `docs/contracts/DESIGN_TOKENS_CONTRACT.md` (pending) | `export_tokens.sh` |
| Vercel env vars | Vercel dashboard | Next.js apps | `docs/contracts/VERCEL_ENV_CONTRACT.md` (pending) | `vercel env pull` (local only) |

**Invariants (never violate):**
1. A secret value must not cross an SSOT boundary in plaintext via Git or logs.
2. A domain record must not be created in Cloudflare unless it exists in `subdomain-registry.yaml`.
3. An n8n workflow that handles PII must audit each execution to `ops.platform_events`.
4. An Odoo module must not bypass `mail.mail.send()` to SMTP directly — use the bridge when env vars are set.
5. A Supabase migration must not drop or truncate a table named `ops.*` without a superseding migration.
