# SaaS Landing Template - Deployment Status

**Date**: 2026-02-12 15:30
**Scope**: Org invite system post-implementation deployment
**Status**: ⚠️ PARTIALLY COMPLETE - Manual steps required

---

## ✅ Completed

### 1. Git Workspace Cleanup
- **Status**: ✅ Complete
- **Actions**:
  - Unstaged parent repo files (`.claude/settings.local.json`, `apps/alpha-browser/*`, etc.)
  - Verified only template changes remain in scope
  - `.env.local` added to `.gitignore` (correct)
  - `.env.example` properly trackable

### 2. Code Implementation
- **Status**: ✅ Complete
- **Commits**:
  - `acc0b526` - docs(org): add implementation summary and verification script
  - `fea4fba4` - feat(org): implement organization invite system with Supabase RLS and Zoho email
- **Files Changed**:
  - 15 files: API routes, email templates, database types, migration SQL, verification scripts

---

## ⚠️ Blocked / Manual Steps Required

### 3. Database Migration (❌ BLOCKED)
- **Status**: ⚠️ Manual application required
- **Issue**: `supabase db push` fails with migration history mismatch
- **Error**:
  ```
  Remote migration versions not found in local migrations directory.
  Make sure your local git repo is up-to-date.
  ```

**Manual Resolution Required**:
1. Go to: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/sql/new
2. Copy/paste: `supabase/migrations/20260212_org_invites.sql`
3. Execute SQL
4. Verify:
   ```sql
   -- Check schema exists
   SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'registry';

   -- Check table exists
   SELECT table_name FROM information_schema.tables WHERE table_schema = 'registry' AND table_name = 'org_invites';

   -- Check functions exist (should be 4)
   SELECT routine_name FROM information_schema.routines WHERE routine_schema = 'registry' AND routine_name LIKE '%invite%';
   ```

**Migration Contents**:
- ✅ `registry` schema
- ✅ `org_invites` table (9 columns, 3 constraints, 6 indexes)
- ✅ RLS policies (3 policies: org admin SELECT/INSERT, user SELECT own invites)
- ✅ RPC functions:
  - `create_org_invite_with_token` (with SHA-256 hashing)
  - `accept_org_invite` (with expiry validation)
  - `cancel_org_invite` (admin-only)
  - `cleanup_expired_invites` (cron-ready)

### 4. Vercel Project Setup (❌ NOT STARTED)
- **Status**: ❌ Project not deployed to Vercel yet
- **Error**: `Project not found (VERCEL_PROJECT_ID: YOUR_VERCEL_PROJECT_ID_HERE)`

**Required Actions**:
1. **Create Vercel Project**:
   ```bash
   cd templates/saas-landing
   vercel --prod
   # Follow prompts to link/create project
   ```

2. **Set Environment Variables** (7 required):
   ```bash
   PROJECT_NAME="ops-insightpulseai"  # or actual project name

   # Supabase
   vercel env add NEXT_PUBLIC_SUPABASE_URL production <<< "https://spdtwktxdalcfigzeqrz.supabase.co"
   vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production <<< "$SUPABASE_ANON_KEY"
   vercel env add SUPABASE_SERVICE_ROLE_KEY production <<< "$SUPABASE_SERVICE_ROLE_KEY"

   # Zoho Mail
   vercel env add ZOHO_USER production <<< "business@insightpulseai.com"
   vercel env add ZOHO_PASS production <<< "$ZOHO_PASS"
   vercel env add ZOHO_FROM_NAME production <<< "InsightPulse.ai"

   # App URL
   vercel env add NEXT_PUBLIC_APP_URL production <<< "https://ops.insightpulseai.com"
   ```

3. **Deploy**:
   ```bash
   vercel --prod
   ```

4. **Configure Custom Domain** (if not auto-configured):
   - Add `ops.insightpulseai.com` in Vercel dashboard
   - Update DNS: CNAME → `cname.vercel-dns.com`

---

## 🔍 Verification Checklist (After Manual Steps)

### Database Contract
```bash
# From psql or Supabase SQL Editor
SELECT count(*) FROM registry.org_invites;  -- Should return 0 initially

# Check RPC functions
SELECT routine_name FROM information_schema.routines
WHERE routine_schema = 'registry' AND routine_name LIKE '%invite%';
-- Should show 4 functions
```

### API Endpoints
```bash
export BASE_URL="https://ops.insightpulseai.com"

# Health checks
curl -sS "$BASE_URL/api/org/create" -I | grep -E "HTTP|content-type"
curl -sS "$BASE_URL/api/invite/send" -I | grep -E "HTTP|content-type"
curl -sS "$BASE_URL/api/invite/accept" -I | grep -E "HTTP|content-type"
```

### Automated Verification
```bash
cd templates/saas-landing
chmod +x scripts/verify-org-invites.sh
./scripts/verify-org-invites.sh
```

### Manual E2E Test
1. Navigate to `/org/new`
2. Create organization
3. Go to `/org/{orgId}`
4. Send invite to test email
5. Check Zoho inbox for email
6. Click accept link
7. Verify redirect to org dashboard

---

## 📊 Current State Summary

| Component | Status | Action Required |
|-----------|--------|-----------------|
| Git Workspace | ✅ Clean | None |
| Code Implementation | ✅ Complete | None |
| Database Migration | ⚠️ Ready | Manual SQL execution |
| Vercel Project | ❌ Not Created | Project creation + env vars |
| DNS Configuration | ❓ Unknown | Verify CNAME after deploy |
| E2E Testing | ⏳ Pending | After deployment |

---

## 🔐 Security Status

- ✅ `SUPABASE_SERVICE_ROLE_KEY` configured as server-only
- ✅ `ZOHO_PASS` never committed to git
- ✅ `.env.local` in `.gitignore`
- ✅ `.env.example` has placeholder values only
- ✅ RLS policies enforce org admin permissions
- ✅ SHA-256 token hashing in database
- ✅ Email invite tokens expire in 7 days

---

## 📝 Next Steps (Priority Order)

1. **Database Migration** (5 min)
   - Apply `20260212_org_invites.sql` via Supabase SQL Editor
   - Verify schema, table, functions created

2. **Vercel Deployment** (15 min)
   - Create Vercel project: `vercel --prod`
   - Set 7 environment variables
   - Deploy and verify build success

3. **DNS Configuration** (5 min)
   - Add `ops.insightpulseai.com` CNAME → Vercel
   - Wait for propagation (1-5 min)

4. **End-to-End Verification** (10 min)
   - Run automated verification script
   - Manual E2E test flow
   - Document results in `docs/evidence/`

---

## 🚨 Rollback Procedures

### Database Rollback
```sql
DROP FUNCTION IF EXISTS registry.create_org_invite_with_token;
DROP FUNCTION IF EXISTS registry.accept_org_invite;
DROP FUNCTION IF EXISTS registry.cancel_org_invite;
DROP FUNCTION IF EXISTS registry.cleanup_expired_invites;
DROP TABLE IF EXISTS registry.org_invites;
DROP SCHEMA IF EXISTS registry CASCADE;
```

### Code Rollback
```bash
git revert --no-edit acc0b526 fea4fba4
git push origin feat/odooops-browser-automation-integration
```

### Vercel Rollback
```bash
vercel rollback
# Or via dashboard: Deployments → Previous → Promote
```

---

## 📁 Reference Files

- **Migration**: `supabase/migrations/20260212_org_invites.sql`
- **Verification**: `scripts/verify-org-invites.sh`
- **Implementation Summary**: `docs/IMPLEMENTATION_SUMMARY.md`
- **Org Invites Guide**: `docs/ORG_INVITES.md`
- **This Status**: `docs/evidence/20260212-1530/deployment-status.md`

---

**Last Updated**: 2026-02-12 15:30
**Next Review**: After manual migration + Vercel deployment
