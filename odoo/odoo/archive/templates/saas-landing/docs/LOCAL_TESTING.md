# Local Testing Guide

Complete guide for testing the saas-landing template locally before production deployment.

---

## Quick Test

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/templates/saas-landing

# Run automated tests
./scripts/test-local.sh
```

**Expected result**: All tests ✅ pass

---

## Manual Browser Testing

### 1. Start Dev Server

```bash
pnpm dev

# Server starts at: http://localhost:3000
```

### 2. Test Pages

| Page | URL | Expected |
|------|-----|----------|
| Homepage | http://localhost:3000/ | Landing page with hero section |
| Dashboard | http://localhost:3000/dashboard | Dashboard interface |
| Org Create | http://localhost:3000/org/new | Organization creation form |
| Invite Accept | http://localhost:3000/invite/accept | Invite acceptance page |

### 3. Test Authentication Flow

**Note**: Full E2E testing requires actual Supabase authentication. Without a logged-in user, you'll see auth prompts.

**What you can verify**:
- ✅ Pages load without errors
- ✅ No console errors (open DevTools → Console)
- ✅ Supabase client initialized (check Network tab for API calls)
- ✅ Redirect to login when accessing protected routes

---

## Automated Test Results

### ✅ All Tests Passing

```
Test 1: Homepage
✅ Homepage loads (HTTP 200)

Test 2: Dashboard
✅ Dashboard loads (HTTP 200)

Test 3: API Routes
✅ /api/invite/list exists (HTTP 401 - auth required)
✅ /api/org/create exists (HTTP 401 - auth required)
✅ /api/invite/send exists (HTTP 401 - auth required)
✅ /api/invite/accept exists (HTTP 401 - auth required)

Test 4: Environment Variables
✅ .env.local exists
✅ SUPABASE_URL configured
✅ SUPABASE_SERVICE_ROLE_KEY configured
✅ ZOHO_PASS configured

Test 5: Database Connection
✅ Database credentials available
✅ Database migration deployed (4 functions found)

Test 6: Build Test
✅ Production build succeeds
```

---

## What Gets Tested

### ✅ **Verified Locally**

1. **Pages Load**: Homepage, dashboard, org pages
2. **API Routes Exist**: All invite endpoints respond correctly
3. **Authentication**: Protected routes require auth (401 responses)
4. **Environment**: All secrets configured
5. **Database**: Migration deployed (4 RPC functions)
6. **Build**: Production build succeeds

### ⚠️ **Requires Auth (Can't Test Locally Without Login)**

1. **Create Organization**: Requires authenticated user
2. **Send Invite**: Requires org admin auth
3. **Accept Invite**: Requires invite token + auth
4. **Email Sending**: Requires server-side action (can test in prod)

### ✅ **Will Be Tested in Production**

1. **Full E2E Flow**:
   - Sign up → Create org → Send invite → Receive email → Accept invite
2. **Email Delivery**: Zoho SMTP integration
3. **DNS Resolution**: ops.insightpulseai.com → Vercel
4. **SSL/TLS**: HTTPS working correctly
5. **RLS Policies**: Database security enforcement

---

## Testing Checklist

### Pre-Deployment Checklist

- [x] Dev server starts without errors
- [x] Homepage loads (HTTP 200)
- [x] Dashboard loads (HTTP 200)
- [x] All API routes exist (401 for auth-required)
- [x] Environment variables configured
- [x] Database migration deployed (4 functions)
- [x] Production build succeeds
- [ ] Browser testing complete (manual)
- [ ] No console errors in DevTools
- [ ] Ready for production deployment

### Post-Deployment Checklist (Production)

- [ ] DNS resolves: ops.insightpulseai.com
- [ ] HTTPS works (SSL certificate)
- [ ] Homepage loads in production
- [ ] Sign up flow works
- [ ] Create organization works
- [ ] Send invite email works
- [ ] Email received in inbox
- [ ] Accept invite link works
- [ ] User added to organization

---

## Browser DevTools Checklist

### Console Tab

**Should NOT see**:
- ❌ Errors about missing environment variables
- ❌ Failed API calls (except 401 auth required)
- ❌ CORS errors
- ❌ Supabase initialization errors

**OK to see**:
- ✅ 401 Unauthorized (for protected routes when not logged in)
- ✅ Warnings about development mode
- ✅ HMR (Hot Module Replacement) messages

### Network Tab

**Should see**:
- ✅ API calls to `localhost:3000/api/*`
- ✅ Supabase calls to `spdtwktxdalcfigzeqrz.supabase.co`
- ✅ 200 responses for pages
- ✅ 401 responses for auth-required APIs

### Application Tab

**Should see**:
- ✅ localStorage with Supabase session data (after login)
- ✅ Cookies set correctly

---

## Common Issues & Fixes

### "Dev server won't start"

**Cause**: Port 3000 already in use

**Fix**:
```bash
# Kill existing dev servers
pkill -f "next dev"

# Or use a different port
pnpm dev --port 3001
```

### "API returns 500 Internal Server Error"

**Cause**: Missing environment variables or database connection issue

**Fix**:
```bash
# Check .env.local exists and has all secrets
cat .env.local | grep -E "SUPABASE|ZOHO"

# Restart dev server
pkill -f "next dev"
pnpm dev
```

### "Build fails"

**Cause**: TypeScript errors or missing dependencies

**Fix**:
```bash
# View build log
pnpm build 2>&1 | tee /tmp/build.log

# Check for errors
cat /tmp/build.log | grep -i error
```

### "Database connection test fails"

**Cause**: psql not installed or wrong credentials

**Fix**:
```bash
# Install psql (if needed)
brew install postgresql  # macOS

# Test connection manually
psql "postgres://postgres.spdtwktxdalcfigzeqrz:PASSWORD@..." -c "\df registry.*invite*"
```

---

## Test Logs

All test logs are saved to `/tmp/`:

```bash
# Dev server log
tail -f /tmp/dev-server.log

# Build test log
cat /tmp/build-test.log
```

---

## Next Steps After Local Testing

Once all local tests pass:

```bash
# 1. Deploy to Vercel (first time)
./scripts/vercel-first-deploy.sh

# 2. Add Cloudflare DNS (see DNS_SETUP.md)

# 3. Deploy to production
source ~/.zshrc
./scripts/deploy-production.sh

# 4. Run E2E verification
./scripts/verify-org-invites.sh
```

---

## Related Documentation

- **DNS Setup**: `docs/DNS_SETUP.md`
- **Configuration**: `docs/CONFIGURATION.md`
- **Deployment**: `DEPLOY.md`
- **Verification Script**: `scripts/verify-org-invites.sh`

---

**Last Updated**: 2026-02-12
