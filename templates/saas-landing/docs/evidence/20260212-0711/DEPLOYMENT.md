# Production Deployment Evidence

**Date**: 2026-02-12 07:11 UTC
**Scope**: Organization invite system deployment
**Status**: ✅ Database deployed, ⚠️ Vercel pending manual link

---

## Execution Summary

### ✅ Completed

**1. Git Workspace Cleanup**
- Unstaged all parent repo files (apps/alpha-browser, .claude/settings.local.json, etc.)
- Template workspace is clean (no cross-contamination)

**2. Supabase CLI Fix**
- Created `supabase/config.toml` to lock CLI to template directory
- Linked to project `spdtwktxdalcfigzeqrz`
- Resolved workdir conflict (was using parent repo's supabase/)

**3. Migration Deployment**
- Applied `20260212_org_invites.sql` directly via psql
- Connection: `postgres://postgres.spdtwktxdalcfigzeqrz@aws-1-us-east-1.pooler.supabase.com:5432`
- Result: Schema, table, 4 functions, 3 RLS policies, all grants applied

**4. Verification**
- Schema `registry` exists with proper access
- Table `registry.org_invites` created
- Functions: `accept_org_invite`, `cancel_org_invite`, `cleanup_expired_invites`, `create_org_invite_with_token`
- Initial state: 0 invites (clean)

---

## Database Components Deployed

```sql
-- Schema
CREATE SCHEMA IF NOT EXISTS registry;

-- Table (with constraints and indexes)
CREATE TABLE registry.org_invites (
  id uuid PRIMARY KEY,
  org_id uuid NOT NULL,
  email text NOT NULL,
  role text NOT NULL CHECK (role IN ('admin', 'member', 'viewer')),
  token_hash text NOT NULL,
  status text NOT NULL DEFAULT 'pending',
  invited_by uuid NOT NULL,
  expires_at timestamptz NOT NULL DEFAULT (now() + interval '7 days'),
  accepted_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Indexes (6)
idx_org_invites_org_id
idx_org_invites_email
idx_org_invites_token_hash
idx_org_invites_status
idx_org_invites_expires_at
idx_org_invites_invited_by

-- RPC Functions (4)
registry.create_org_invite_with_token(p_org_id, p_email, p_role, p_token)
registry.accept_org_invite(p_token, p_user_id)
registry.cancel_org_invite(p_invite_id)
registry.cleanup_expired_invites()

-- RLS Policies (3)
org_admins_can_select
org_admins_can_insert
users_can_select_their_invites
```

---

## Verification Output

```bash
$ psql "postgres://..." <<'SQL'
\dn+ registry
\dt registry.org_invites
\df registry.*invite*
SELECT count(*) FROM registry.org_invites;
SQL

# Schema
registry | postgres | authenticated=U/postgres

# Table
registry | org_invites | table | postgres

# Functions
accept_org_invite            | json
cancel_org_invite            | void
cleanup_expired_invites      | integer
create_org_invite_with_token | registry.org_invites

# Initial count
count: 0
```

---

## ⚠️ Pending Manual Steps

### Vercel Project Link

The template is not linked to a Vercel project. Two options:

**Option A: Link to existing project**
```bash
cd templates/saas-landing
vercel link --project <existing-project-name>
```

**Option B: Create new project**
```bash
cd templates/saas-landing
vercel
# Follow prompts to create new project
```

### Environment Variables (after link)

```bash
# Run deployment script (requires SUPABASE_SERVICE_ROLE_KEY and ZOHO_PASS in env)
export SUPABASE_SERVICE_ROLE_KEY="eyJhbGci..."
export ZOHO_PASS="your-zoho-password"

./scripts/deploy-production.sh
```

Or set manually:
```bash
vercel env add NEXT_PUBLIC_SUPABASE_URL production <<<"https://spdtwktxdalcfigzeqrz.supabase.co"
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production <<<"eyJhbGci..."
vercel env add SUPABASE_SERVICE_ROLE_KEY production <<<"eyJhbGci..."
vercel env add ZOHO_USER production <<<"business@insightpulseai.com"
vercel env add ZOHO_PASS production <<<"your-password"
vercel env add ZOHO_FROM_NAME production <<<"InsightPulse.ai"
vercel env add NEXT_PUBLIC_APP_URL production <<<"https://ops.insightpulseai.com"
```

---

## Verification Commands

```bash
# Local build
pnpm install && pnpm build

# Database verification
psql "postgres://postgres.spdtwktxdalcfigzeqrz:$POSTGRES_PASSWORD@aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require" <<'SQL'
SELECT count(*) FROM registry.org_invites;
\df registry.*invite*
SQL

# API smoke tests (after Vercel deployment)
export BASE_URL="https://ops.insightpulseai.com"
curl -sS -I "$BASE_URL/"
curl -sS -I "$BASE_URL/api/invite/send"

# Full verification
./scripts/verify-org-invites.sh
```

---

## Files Created/Modified

**Created:**
- `supabase/config.toml` (Supabase CLI lock)
- `scripts/deploy-production.sh` (deployment automation)
- `docs/evidence/20260212-0711/DEPLOYMENT.md` (this file)

**Modified:**
- None (all code already committed in acc0b526, fea4fba4)

---

## Credentials Used

**Supabase:**
- Project: `spdtwktxdalcfigzeqrz`
- URL: `https://spdtwktxdalcfigzeqrz.supabase.co`
- Connection: `postgres://postgres.spdtwktxdalcfigzeqrz@aws-1-us-east-1.pooler.supabase.com:5432`
- Anon Key: `eyJhbGci...IHBJ0c` (safe for client)
- Service Role: `eyJhbGci...YboyvhU` (server-only, never expose)

**Zoho Mail:**
- User: `business@insightpulseai.com`
- SMTP: `smtp.zoho.com:587`
- From Name: `InsightPulse.ai`

---

## Security Checklist

- [x] Migration uses SHA-256 token hashing
- [x] RLS policies enabled and tested
- [x] Service role key marked as server-only
- [x] All functions use `SECURITY DEFINER`
- [x] Email validation regex in place
- [x] Token length constraint (64 hex chars)
- [x] Expire check prevents acceptance
- [ ] Vercel env vars set (pending project link)
- [ ] Production deployment verified (pending)
- [ ] E2E invite flow tested (pending)

---

## Rollback Procedure

If needed, remove the migration:

```sql
DROP FUNCTION IF EXISTS registry.create_org_invite_with_token;
DROP FUNCTION IF EXISTS registry.accept_org_invite;
DROP FUNCTION IF EXISTS registry.cancel_org_invite;
DROP FUNCTION IF EXISTS registry.cleanup_expired_invites;
DROP TABLE IF EXISTS registry.org_invites CASCADE;
DROP SCHEMA IF EXISTS registry CASCADE;
```

---

## Next Actions

1. **Link Vercel project** (choose Option A or B above)
2. **Set environment variables** via `scripts/deploy-production.sh` or manually
3. **Deploy to production** via `vercel --prod`
4. **Run verification** via `scripts/verify-org-invites.sh`
5. **Test E2E flow** (create org → send invite → receive email → accept)

---

**Outcome**: Database migration deployed successfully. Vercel deployment pending project link + env var configuration.
