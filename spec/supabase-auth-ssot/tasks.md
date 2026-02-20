# Tasks — Supabase Auth SSOT

**Version**: 1.0.0
**Authority**: `spec/supabase-auth-ssot/prd.md`
**DoD**: Each task is complete only when evidence exists (log file or CI pass)

---

## P0 Tasks — Identity SSOT (Critical Path)

### T01 — Odoo `x_supabase_user_id` field
- **Scope**: `addons/ipai/ipai_auth_oidc/`
- **DoD**:
  - [ ] Field `x_supabase_user_id` (char 36, indexed, unique) added to `res.users`
  - [ ] `SELECT x_supabase_user_id FROM res_users LIMIT 1` succeeds on prod
  - [ ] Field NOT exposed in `portal` or `public` user views
- **Blocked by**: nothing (first task)

### T02 — Supabase `auth_ssot_baseline` migration
- **Scope**: `supabase/migrations/20260221100000_auth_ssot_baseline.sql`
- **DoD**:
  - [ ] Migration applied to Supabase project `spdtwktxdalcfigzeqrz`
  - [ ] `SELECT * FROM auth_ext.platform_roles` returns 0 rows (seeded in T06)
  - [ ] `SELECT * FROM auth_ext.user_roles` returns 0 rows
  - [ ] RLS: service role can INSERT; anon role cannot SELECT
- **Blocked by**: nothing

### T03 — `provision-odoo-user` Edge Function (core)
- **Scope**: `supabase/functions/provision-odoo-user/index.ts`
- **DoD**:
  - [ ] `deno check supabase/functions/provision-odoo-user/index.ts` exits 0
  - [ ] Creates `res.users` via XML-RPC on first-time signup
  - [ ] Updates email if changed on re-signup
  - [ ] Does NOT write password, social tokens, or MFA state to Odoo
  - [ ] Every invocation appends row to `ops.platform_events`
  - [ ] Deployed: `supabase functions deploy provision-odoo-user`
- **Blocked by**: T01, T02

### T04 — Auth hook registration (Supabase Dashboard)
- **Type**: [MANUAL_REQUIRED]
- **What**: Register T03 function as "After signup" hook in Supabase Dashboard
- **Why**: No CLI API for hook registration
- **Minimal human action**:
  - Dashboard → Authentication → Hooks → After signup
  - URL: `https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/provision-odoo-user`
  - Enable and save
- **DoD**:
  - [ ] Hook appears in Dashboard as active
  - [ ] Test signup (new `@insightpulseai.com` email) creates `res.users` row
- **Blocked by**: T03

### T05 — Vault: `provision_odoo_hook_secret`
- **Scope**: `infra/supabase/vault_secrets.tf`
- **DoD**:
  - [ ] Variable `provision_odoo_hook_secret` added with `sensitive = true`
  - [ ] Secret loaded in Edge Function via `Deno.env.get("PROVISION_ODOO_HOOK_SECRET")`
  - [ ] No secret value committed to git
- **Blocked by**: T03

---

## P1 Tasks — Auth Hooks + RBAC + MFA

### T06 — Platform roles seed + RLS
- **Scope**: `supabase/migrations/20260221200000_auth_rbac_baseline.sql`
- **DoD**:
  - [ ] `auth_ext.platform_roles` has 4 rows: `admin`, `finance`, `ops`, `viewer`
  - [ ] `integrations.zoho_accounts` RLS enabled (service role can read/write; anon cannot)
  - [ ] `integrations.zoho_tokens` RLS enabled (service role only)
  - [ ] `bridge.odoo_mail_server_map` RLS enabled
  - [ ] CI: migration passes `psql` syntax check
- **Blocked by**: T02

### T07 — Odoo group derivation in `provision-odoo-user`
- **Scope**: `supabase/functions/provision-odoo-user/index.ts` (extend)
- **DoD**:
  - [ ] Function reads `auth_ext.user_roles` for the user
  - [ ] Maps platform role → Odoo group (documented mapping table in README)
  - [ ] Updates `res.users.groups_id` via XML-RPC `write()`
  - [ ] Fallback: if no role, assign `base.group_user` only
- **Blocked by**: T04, T06

### T08 — MFA TOTP enforcement (Supabase Dashboard)
- **Type**: [MANUAL_REQUIRED]
- **What**: Enable mandatory TOTP MFA for `@insightpulseai.com` users
- **Why**: MFA enforcement is a Supabase Dashboard setting
- **Minimal human action**:
  - Dashboard → Authentication → Multi-Factor Authentication
  - Set TOTP: Required for internal users
- **DoD**:
  - [ ] New internal user signup requires TOTP enrollment
  - [ ] Unenrolled users cannot complete login
- **Blocked by**: T04

### T09 — CI guard: `spec/supabase-auth-ssot` allowlist
- **Scope**: `.github/workflows/pr-scope-guard.yml`
- **DoD**:
  - [ ] PR with branch/title containing `auth-ssot` enforces allowlist:
    - `spec/supabase-auth-ssot/`
    - `supabase/migrations/*_auth_*`
    - `supabase/functions/provision-odoo-user/`
    - `addons/ipai/ipai_auth_oidc/`
    - `config/auth/`
    - `infra/supabase/vault_secrets.tf`
    - `docs/architecture/SSOT_BOUNDARIES.md`
  - [ ] PR with out-of-scope files is blocked
- **Blocked by**: nothing (CI task, independent)

---

## P2 Tasks — JWT Trust + SSO

### T10 — JWKS declaration file
- **Scope**: `config/auth/jwt_trust.yaml`
- **DoD**:
  - [ ] File created with Supabase JWKS endpoint declared
  - [ ] `python3 -c "import yaml; yaml.safe_load(open('config/auth/jwt_trust.yaml'))"` exits 0
  - [ ] Consumers listed: `[odoo, n8n]`
- **Blocked by**: nothing

### T11 — Odoo JWT middleware
- **Scope**: `addons/ipai/ipai_auth_oidc/models/ir_http.py`
- **DoD**:
  - [ ] Middleware validates `Authorization: Bearer <jwt>` against Supabase JWKS
  - [ ] Invalid/expired token → `401 Unauthorized`
  - [ ] Token cache TTL 5 min (avoids per-request JWKS fetches)
  - [ ] Unit test covers: valid token → pass, expired token → 401, tampered token → 401
- **Blocked by**: T10

### T12 — n8n JWT validation for Supabase webhooks
- **Scope**: n8n workflows that receive Supabase-signed payloads (manual workflow update)
- **Type**: [MANUAL_REQUIRED]
- **DoD**:
  - [ ] Affected workflows identified and listed
  - [ ] Header validation node added to each
  - [ ] Workflow fails if JWT signature invalid
- **Blocked by**: T10

### T13 — SSO SAML (deferred — Supabase Pro required)
- **Status**: DEFERRED
- **Prerequisites**: Supabase Pro plan upgrade + SAML IdP selection + spec amendment
- **No action until**: spec amendment approved and Pro plan active

---

## P3 Tasks — OAuth 2.1 Server

### T14 — OAuth 2.1 Server (deferred)
- **Status**: DEFERRED
- **Prerequisites**: P0-P2 complete, platform maturity established
- **Unblocks**: Replacement of ad-hoc API keys in n8n and Edge Functions

---

## Done Definition (Global)

All tasks require:
1. Code committed with message `feat(auth-ssot): ... Implements: spec/supabase-auth-ssot/tasks.md#TNN`
2. Verification evidence in `web/docs/evidence/<YYYYMMDD-HHMM+0800>/auth-ssot/logs/`
3. No secrets in git — vault references only

---

## P0→P3 Adoption Backlog (migrated from `docs/architecture/SSOT_BOUNDARIES.md §6`)

| Priority | Task | Status |
|----------|------|--------|
| P0 | `x_supabase_user_id` on `res.users` | T01 — pending |
| P0 | Supabase auth schema migration | T02 — pending |
| P0 | `provision-odoo-user` Edge Function | T03 — pending |
| P0 | Auth hook registration | T04 — pending [MANUAL] |
| P1 | Platform roles + RLS | T06 — pending |
| P1 | Odoo group derivation | T07 — pending |
| P1 | MFA enforcement | T08 — pending [MANUAL] |
| P2 | JWKS declaration + Odoo JWT middleware | T10, T11 — pending |
| P2 | n8n JWT validation | T12 — pending [MANUAL] |
| P2 | SAML SSO | T13 — DEFERRED |
| P3 | OAuth 2.1 server | T14 — DEFERRED |
