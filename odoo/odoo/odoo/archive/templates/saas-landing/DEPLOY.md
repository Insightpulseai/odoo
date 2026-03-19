# Production Deployment - Final Steps

**Status**: Database ✅ | Local Build ✅ | Vercel ⚠️ Pending Link

---

## ✅ Completed

1. **Database Migration**: All 4 RPC functions deployed to production
2. **Security Fix**: Deployment script no longer prints secrets
3. **Hard Guardrail**: Pre-commit hook blocks parent repo staging
4. **Local Build**: Verified successful with all invite routes
5. **Secrets**: All loaded from `~/.zshrc` (master SSOT)

---

## ⚠️ Remaining: Vercel Project Link + Deploy

### Option 1: Create New Vercel Project (Recommended)

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/templates/saas-landing

# Interactive project creation
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (select your account)
# - Link to existing project? No
# - Project name: saas-landing (or ops-insightpulseai)
# - Directory: ./ (current)
# - Override settings? No

# This will:
# 1. Create .vercel/ directory with project config
# 2. Deploy to preview URL
# 3. Give you project ID and org ID
```

### Option 2: Link to Existing Project

```bash
# If you already have a Vercel project
vercel link --project <existing-project-name>
```

### After Link: Deploy to Production

```bash
# Source secrets from .zshrc
source ~/.zshrc

# Run secure deployment script
./scripts/deploy-production.sh

# This will:
# 1. Validate secrets from ~/.zshrc
# 2. Set Vercel env vars (production)
# 3. Deploy to production
# 4. Print smoke test commands
```

---

## 🔒 Security Notes

### Secrets Storage (SSOT)

**Master**: `~/.zshrc`
```bash
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
ZOHO_SMTP_PASSWORD=ka8EnXL4ttS9
```

**Local Dev**: `.env.local` (gitignored)
**Production**: Vercel env vars (set by deploy script)
**Vault**: Supabase Vault (42 secrets for Edge Functions)

### Hard Guardrail

Pre-commit hook (`.githooks/pre-commit`) blocks commits with:
- `web/alpha-browser/`
- `.claude/`
- `pnpm-lock.yaml`
- `pnpm-workspace.yaml`
- `scripts/cf_*`

**Test it**:
```bash
# Try to stage parent repo file (should fail)
git add ../../web/alpha-browser/package.json
git commit -m "test"
# Expected: ❌ Pre-commit blocked
```

---

## 🧪 Verification Commands

### Database Contract

```bash
export DB_URL="postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require"

psql "$DB_URL" <<'SQL'
\df registry.*invite*
SELECT count(*) FROM registry.org_invites;
SQL

# Expected:
# - 4 functions
# - 0 invites
```

### Local Build

```bash
pnpm build
pnpm start &
sleep 2
curl -sS http://localhost:3000/ | head -40
```

### Production Endpoints (After Deploy)

```bash
export BASE_URL="https://ops.insightpulseai.com"

curl -sS -I "$BASE_URL/" | head -20
curl -sS -I "$BASE_URL/api/invite/list" | head -20
curl -sS -I "$BASE_URL/api/invite/send" | head -20
curl -sS -I "$BASE_URL/api/invite/accept" | head -20
```

### Full E2E Verification

```bash
./scripts/verify-org-invites.sh
```

---

## 📋 Deployment Checklist

### Pre-Deploy

- [x] Database migration deployed (registry.org_invites + 4 functions)
- [x] Secrets in ~/.zshrc verified
- [x] .env.local populated (gitignored)
- [x] Pre-commit hook active (blocks parent staging)
- [x] Local build succeeds
- [ ] Vercel project linked (do this now)

### Deploy

- [ ] Run `vercel` to create/link project
- [ ] Run `./scripts/deploy-production.sh`
- [ ] Verify deployment URL
- [ ] Test invite flow E2E

### Post-Deploy

- [ ] Smoke test all API routes
- [ ] Send test invite email
- [ ] Accept invite via email link
- [ ] Verify user added to org
- [ ] Monitor Vercel logs for errors

---

## 🚀 Quick Start (After Vercel Link)

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/templates/saas-landing

# 1. Link to Vercel (interactive)
vercel

# 2. Deploy with secrets
source ~/.zshrc
./scripts/deploy-production.sh

# 3. Verify
export BASE_URL="https://ops.insightpulseai.com"
curl -sS -I "$BASE_URL/api/invite/list"
./scripts/verify-org-invites.sh
```

---

## 📚 Documentation

- **Configuration**: `docs/CONFIGURATION.md`
- **Secrets Reference**: `docs/SECRETS.md`
- **Deployment Evidence**: `docs/evidence/20260212-0711/DEPLOYMENT.md`
- **Implementation Summary**: `docs/IMPLEMENTATION_SUMMARY.md`

---

## 🔄 Rollback

### Vercel Environment

```bash
for k in NEXT_PUBLIC_SUPABASE_URL NEXT_PUBLIC_SUPABASE_ANON_KEY SUPABASE_SERVICE_ROLE_KEY ZOHO_USER ZOHO_PASS ZOHO_FROM_NAME NEXT_PUBLIC_APP_URL; do
  vercel env rm "$k" production || true
done
```

### Database

```sql
DROP FUNCTION IF EXISTS registry.create_org_invite_with_token;
DROP FUNCTION IF EXISTS registry.accept_org_invite;
DROP FUNCTION IF EXISTS registry.cancel_org_invite;
DROP FUNCTION IF EXISTS registry.cleanup_expired_invites;
DROP TABLE IF EXISTS registry.org_invites CASCADE;
```

---

## ❓ Troubleshooting

### "Project not found"

**Cause**: Vercel project not linked
**Fix**: Run `vercel` to create/link project

### "Missing ZOHO_SMTP_PASSWORD"

**Cause**: ~/.zshrc not sourced
**Fix**: `source ~/.zshrc` before running deploy script

### "Secrets printed in output"

**Cause**: Old deployment script
**Fix**: Use updated `scripts/deploy-production.sh` (only prints char counts)

### "Pre-commit blocked parent files"

**Cause**: Parent repo files staged (expected behavior!)
**Fix**: `git restore --staged <parent-files>` before committing

---

**Last Updated**: 2026-02-12 07:30 UTC
