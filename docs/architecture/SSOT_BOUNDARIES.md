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

---

## §5 — CI Enforcement

### Path guards (to be added)

| PR pattern | Allowed paths | Blocked if outside |
|-----------|---------------|-------------------|
| `zoho-bridge` title | `addons/ipai/ipai_zoho_mail/**`, `config/odoo/mail_settings.yaml`, `scripts/odoo/apply_mail_settings.py`, `infra/dns/zoho_mail_dns.yaml`, `docs/contracts/DNS_EMAIL_CONTRACT.md`, `supabase/*/zoho-mail-bridge/**`, `spec/zoho-mail-bridge/**`, `infra/supabase/vault_secrets.tf` | Anything else |
| `auth` title | `supabase/migrations/*auth*`, `supabase/functions/*auth*`, `spec/*auth*`, `docs/architecture/SSOT_BOUNDARIES.md` | Odoo addons, n8n |

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
