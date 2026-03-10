# Plan — Supabase Auth SSOT

**Version**: 1.0.0
**Status**: Active
**Depends on**: `prd.md` (FRs), `constitution.md` (governance)

## Implementation Order

Priority order follows P0 → P3. Each phase is independently deployable.

---

## Phase 0 — Schema & DB Baseline (prerequisite)

### 0.1 Supabase Migration — `auth_ssot_baseline`

Create the supporting schema that all later phases depend on:

```sql
-- File: supabase/migrations/20260221100000_auth_ssot_baseline.sql
CREATE TABLE IF NOT EXISTS ops.platform_events (...);  -- reuse existing if present
CREATE TABLE auth_ext.platform_roles (
  role_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name        text UNIQUE NOT NULL,  -- 'admin', 'finance', 'ops', 'viewer'
  description text,
  created_at  timestamptz DEFAULT now()
);
CREATE TABLE auth_ext.user_roles (
  user_id  uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  role_id  uuid REFERENCES auth_ext.platform_roles(role_id),
  PRIMARY KEY (user_id, role_id)
);
```

RLS: `auth_ext.user_roles` readable by service role only. Writable only via `provision-odoo-user` Edge Function.

### 0.2 Odoo Field Migration

Add `x_supabase_user_id` to `res.users`:

```xml
<!-- addons/ipai/ipai_auth_oidc/data/fields.xml -->
<record model="ir.model.fields" id="field_res_users_supabase_id">
  <field name="model">res.users</field>
  <field name="name">x_supabase_user_id</field>
  <field name="field_description">Supabase User ID</field>
  <field name="ttype">char</field>
  <field name="size">36</field>
  <field name="required">False</field>
  <field name="index">True</field>
  <field name="copy">False</field>
</record>
```

Or via `_inherit` in `ipai_auth_oidc/models/res_users.py`.

**Verification**: `SELECT x_supabase_user_id FROM res_users LIMIT 1;` on prod.

---

## Phase 1 — P0: Identity SSOT + Odoo Projection

### 1.1 `provision-odoo-user` Edge Function

**File**: `supabase/functions/provision-odoo-user/index.ts`

**Flow**:
```
Supabase Auth webhook (signup)
  → Edge Function validates JWT (service role)
  → Look up res.users WHERE x_supabase_user_id = auth.uid
  → If not found: POST /xmlrpc/2/object create res.users (internal, minimal fields)
  → If found: PATCH email/company if changed
  → Append row to ops.platform_events
  → Return 200 OK
```

**Odoo fields to set on create**:
- `login` = email
- `name` = display_name from Supabase metadata
- `x_supabase_user_id` = UUID
- `company_id` = 1 (default; can be overridden by metadata `odoo_company_id`)
- `groups_id` = [(4, portal_group_id)] — base access only; elevated by role hook

**Odoo fields NEVER set**:
- `password` / `password_crypt`
- Any `oauth_*` field from social provider
- Session tokens

### 1.2 Supabase Auth Hook Registration

Configure in Supabase Dashboard (P0 — no API):

- Auth → Hooks → After signup
- HTTP endpoint: `https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/provision-odoo-user`
- Secret: store as `PROVISION_ODOO_HOOK_SECRET` in Edge Function env

**[MANUAL_REQUIRED]**: Supabase Dashboard → Authentication → Hooks. Cannot be done via CLI alone.

---

## Phase 2 — P1: Auth Hooks + RBAC/RLS + MFA

### 2.1 RBAC baseline migration

**File**: `supabase/migrations/20260221200000_auth_rbac_baseline.sql`

```sql
-- Seed default roles
INSERT INTO auth_ext.platform_roles (name, description) VALUES
  ('admin',   'Full platform access'),
  ('finance', 'Finance module access'),
  ('ops',     'Operations and n8n access'),
  ('viewer',  'Read-only access')
ON CONFLICT (name) DO NOTHING;

-- RLS on integrations.* and bridge.* tables
ALTER TABLE integrations.zoho_accounts  ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations.zoho_tokens    ENABLE ROW LEVEL SECURITY;
ALTER TABLE bridge.odoo_mail_server_map ENABLE ROW LEVEL SECURITY;

-- Service role bypass (for Edge Functions)
CREATE POLICY "service_role_full" ON integrations.zoho_accounts
  USING (auth.role() = 'service_role');
-- (repeat for other tables)
```

### 2.2 MFA enforcement

Enable in Supabase Dashboard:
- Authentication → Multi-Factor Authentication → TOTP: Required for all users with `@insightpulseai.com` domain

**[MANUAL_REQUIRED]**: Supabase Dashboard → Authentication → MFA settings.

### 2.3 Odoo group derivation

Extend `provision-odoo-user` to:
1. Look up `auth_ext.user_roles` for the Supabase user
2. Map platform role → Odoo `res.groups` (`base.group_user`, `account.group_account_user`, etc.)
3. Call `write({'groups_id': [(6, 0, [group_ids])]})` on `res.users`

---

## Phase 3 — P2: JWT Trust + SSO (Supabase Pro)

### 3.1 JWKS declaration

**File**: `config/auth/jwt_trust.yaml`

```yaml
# Declared JWKS endpoints — must be explicitly configured in each consumer
jwks_providers:
  - name: supabase-insightpulseai
    url: https://spdtwktxdalcfigzeqrz.supabase.co/.well-known/jwks.json
    audience: authenticated
    consumers: [odoo, n8n]

enforcement:
  unsigned_jwt: forbidden
  unvalidated_jwt: forbidden
  implicit_trust: forbidden
```

### 3.2 Odoo JWT middleware

In `ipai_auth_oidc`:
- Add middleware to `ir.http` that validates `Authorization: Bearer <jwt>` against Supabase JWKS
- Cache validated tokens (5 min TTL) to avoid per-request JWKS fetches
- Reject invalid/expired tokens with `401 Unauthorized`

### 3.3 n8n JWT validation

In n8n webhook nodes that receive Supabase-signed payloads:
- Add header validation step using the JWKS endpoint
- Fail workflow if signature invalid

### 3.4 SAML SSO (P2 — requires Supabase Pro)

**[DEFERRED]**: Requires Supabase Pro plan upgrade AND a SAML IdP. Spec amendment required before enabling. Out of scope for initial implementation.

---

## Phase 4 — P3: OAuth 2.1 Server

**[DEFERRED]**: Supabase becomes OAuth2 IdP for external integrations. Replaces ad-hoc API keys in n8n and Edge Functions. Requires platform maturity from P0-P2 to be complete.

---

## File Map

| File | Phase | Action |
|------|-------|--------|
| `supabase/migrations/20260221100000_auth_ssot_baseline.sql` | 0 | Create |
| `supabase/migrations/20260221200000_auth_rbac_baseline.sql` | 2 | Create |
| `supabase/functions/provision-odoo-user/index.ts` | 1 | Create |
| `supabase/functions/provision-odoo-user/README.md` | 1 | Create |
| `config/auth/jwt_trust.yaml` | 3 | Create |
| `addons/ipai/ipai_auth_oidc/models/res_users.py` | 0 | Create/extend |
| `addons/ipai/ipai_auth_oidc/models/ir_http.py` | 3 | Create |
| `infra/supabase/vault_secrets.tf` | 1 | Append `provision_odoo_hook_secret` |
| `spec/supabase-auth-ssot/tasks.md` | — | DoD tracking |

---

## Verification Checklist

Per phase, before marking complete:

**Phase 0**:
- [ ] `SELECT x_supabase_user_id FROM res_users LIMIT 1` succeeds on prod DB
- [ ] Migration `20260221100000` applied without error

**Phase 1**:
- [ ] `deno check supabase/functions/provision-odoo-user/index.ts` passes
- [ ] Hook registered in Supabase Dashboard
- [ ] Test signup creates `res.users` row with `x_supabase_user_id` set

**Phase 2**:
- [ ] `SELECT * FROM auth_ext.platform_roles` returns 4 seed rows
- [ ] MFA TOTP required for `@insightpulseai.com` logins
- [ ] RLS: anon role cannot read `integrations.zoho_tokens`

**Phase 3**:
- [ ] `config/auth/jwt_trust.yaml` parses as valid YAML
- [ ] Odoo rejects requests with invalid JWT (returns 401)
- [ ] n8n webhook nodes validate Supabase-signed payloads

---

## Commit Convention

All implementation commits use:

```
feat(auth-ssot): <description>

Implements: spec/supabase-auth-ssot/tasks.md#T<NN>
```
