# Configuration Guide

Complete guide for configuring the saas-landing template for local development and production deployment.

---

## Configuration Hierarchy

```
1. .env.example        → Template (committed to git)
2. .env.local          → Local secrets (gitignored)
3. Vercel Dashboard    → Production secrets (remote)
```

---

## 1. Local Development Setup

### Create `.env.local`

This file contains your **actual secrets** and is **never committed to git**.

**Location**: `templates/saas-landing/.env.local`

**Required variables**:

```bash
# Supabase (Database & Auth)
NEXT_PUBLIC_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...IHBJ0c  # Safe for client
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...YboyvhU    # Server-only, never expose!

# Zoho Mail (Email sending)
ZOHO_USER=business@insightpulseai.com
ZOHO_PASS=<your-zoho-app-password>              # Get from Zoho settings
ZOHO_FROM_NAME=InsightPulse.ai

# App URL
NEXT_PUBLIC_APP_URL=http://localhost:3000       # Local dev
# NEXT_PUBLIC_APP_URL=https://ops.insightpulseai.com  # Production
```

**Optional variables** (for extended features):

```bash
# Odoo Integration
NEXT_PUBLIC_ODOO_URL=https://erp.insightpulseai.com
NEXT_PUBLIC_ODOO_DB=odoo
ODOO_API_KEY=your_api_key_here

# n8n Automation
N8N_WEBHOOK_URL=https://n8n.insightpulseai.com/webhook

# MCP Coordinator
MCP_API_URL=https://mcp.insightpulseai.com

# Platform Settings
NEXT_PUBLIC_PLATFORM_NAME=InsightPulse.ai
NEXT_PUBLIC_ENABLE_DEPLOYMENTS=true
NEXT_PUBLIC_ENABLE_SHELL=false

# Analytics (optional)
NEXT_PUBLIC_GA_TRACKING_ID=
NEXT_PUBLIC_SENTRY_DSN=
```

### Quick Setup

```bash
cd templates/saas-landing

# 1. Copy example to .env.local
cp .env.example .env.local

# 2. Edit .env.local with your actual secrets
nano .env.local
# OR
code .env.local

# 3. Install dependencies
pnpm install

# 4. Run development server
pnpm dev
```

### Verify Local Setup

```bash
# Test build
pnpm build

# Run verification script
./scripts/verify-org-invites.sh

# Test email sending (requires ZOHO_PASS)
curl -X POST http://localhost:3000/api/invite/send \
  -H "Content-Type: application/json" \
  -d '{
    "orgId": "test-org-id",
    "email": "test@example.com",
    "role": "member"
  }'
```

---

## 2. Production Deployment (Vercel)

### Option A: Using Deployment Script (Recommended)

```bash
cd templates/saas-landing

# Set secrets as environment variables
export SUPABASE_SERVICE_ROLE_KEY="eyJhbGci...YboyvhU"
export ZOHO_PASS="your-zoho-password"

# Run deployment script
./scripts/deploy-production.sh
```

This script will:
1. Set all Vercel environment variables
2. Deploy to production
3. Run verification tests

### Option B: Manual Vercel Configuration

**Via Vercel CLI**:

```bash
cd templates/saas-landing

# Set each variable for production
vercel env add NEXT_PUBLIC_SUPABASE_URL production <<<"https://spdtwktxdalcfigzeqrz.supabase.co"
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production <<<"eyJhbGci...IHBJ0c"
vercel env add SUPABASE_SERVICE_ROLE_KEY production <<<"eyJhbGci...YboyvhU"
vercel env add ZOHO_USER production <<<"business@insightpulseai.com"
vercel env add ZOHO_PASS production <<<"your-password"
vercel env add ZOHO_FROM_NAME production <<<"InsightPulse.ai"
vercel env add NEXT_PUBLIC_APP_URL production <<<"https://ops.insightpulseai.com"

# List to verify
vercel env ls production

# Deploy
vercel --prod
```

**Via Vercel Dashboard**:

1. Go to: https://vercel.com/dashboard
2. Select project → Settings → Environment Variables
3. Add each variable:
   - `NEXT_PUBLIC_SUPABASE_URL` = `https://spdtwktxdalcfigzeqrz.supabase.co`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = `eyJhbGci...IHBJ0c`
   - `SUPABASE_SERVICE_ROLE_KEY` = `eyJhbGci...YboyvhU`
   - `ZOHO_USER` = `business@insightpulseai.com`
   - `ZOHO_PASS` = `<your-password>`
   - `ZOHO_FROM_NAME` = `InsightPulse.ai`
   - `NEXT_PUBLIC_APP_URL` = `https://ops.insightpulseai.com`
4. Redeploy from dashboard or `vercel --prod`

---

## 3. Database Seed Data

### Initial Setup (Already Done ✅)

The organization invite system requires these database components:

```sql
-- Schema
CREATE SCHEMA IF NOT EXISTS registry;

-- Table
CREATE TABLE registry.org_invites (...);  -- Already deployed

-- Functions (RPC endpoints)
registry.create_org_invite_with_token()   -- Already deployed
registry.accept_org_invite()               -- Already deployed
registry.cancel_org_invite()               -- Already deployed
registry.cleanup_expired_invites()         -- Already deployed

-- RLS Policies
org_admins_can_select                      -- Already deployed
org_admins_can_insert                      -- Already deployed
users_can_select_their_invites             -- Already deployed
```

**Status**: ✅ All database components deployed to production (see `docs/evidence/20260212-0711/DEPLOYMENT.md`)

### Test Data (Optional)

If you want to seed test data for development:

```sql
-- Create test organization (via Supabase Auth)
-- This would typically be done through the app's signup flow

-- Example: Check invite table is empty
SELECT count(*) FROM registry.org_invites;
-- Expected: 0

-- Example: List all functions
\df registry.*invite*
-- Expected: 4 functions
```

**No manual seed data required** - invites are created through the app UI:
1. User signs up → creates org (auth.users entry)
2. User navigates to `/org/{orgId}`
3. User clicks "Invite Member"
4. System creates invite record via `create_org_invite_with_token()`

---

## 4. Where Secrets Come From

### Supabase Keys

**Get from**: Supabase Dashboard → Project Settings → API

```bash
Project URL: https://spdtwktxdalcfigzeqrz.supabase.co
Anon Key:    eyJhbGci...IHBJ0c  # Public, safe for client
Service Key: eyJhbGci...YboyvhU  # Secret, server-only!
```

**Direct link**: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/api

### Zoho App Password

**Get from**: Zoho Mail → Settings → Security → App Passwords

```bash
1. Go to: https://mail.zoho.com/
2. Click Settings → Security → App Passwords
3. Generate new app password for "Next.js App"
4. Copy the password (you can't see it again!)
5. Use in ZOHO_PASS environment variable
```

**Note**: Use **app password**, not your main Zoho account password.

### Database Connection String

**Get from**: Supabase Dashboard → Project Settings → Database

```bash
# Pooler connection (recommended for serverless)
postgres://postgres.spdtwktxdalcfigzeqrz:PASSWORD@aws-1-us-east-1.pooler.supabase.com:6543/postgres

# Direct connection (for migrations)
postgres://postgres.spdtwktxdalcfigzeqrz:PASSWORD@aws-1-us-east-1.pooler.supabase.com:5432/postgres
```

**Direct link**: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/database

---

## 5. Security Checklist

**Local Development**:
- [x] `.env.local` in `.gitignore`
- [x] Never commit actual secrets
- [x] Use placeholder values in `.env.example`

**Production**:
- [ ] Vercel environment variables set
- [ ] `SUPABASE_SERVICE_ROLE_KEY` marked as server-only (not exposed to client)
- [ ] `ZOHO_PASS` is app password (not main password)
- [ ] All secrets stored in Vercel, not in code

**Database**:
- [x] RLS policies enabled
- [x] Functions use `SECURITY DEFINER`
- [x] Token hashing (SHA-256)
- [x] Email validation
- [x] Expiration checks

---

## 6. Common Issues

### "Missing environment variable"

**Problem**: `.env.local` not loaded

**Fix**:
```bash
# Ensure file exists
ls -la .env.local

# Check Next.js is reading it
pnpm dev
# Look for: "Loaded env from /path/to/.env.local"
```

### "Email not sending"

**Problem**: ZOHO_PASS incorrect or not set

**Fix**:
```bash
# Verify password is set
echo ${ZOHO_PASS:0:5}...  # Should show first 5 chars

# Test SMTP connection
node -e "
const nodemailer = require('nodemailer');
const transport = nodemailer.createTransport({
  host: 'smtp.zoho.com',
  port: 587,
  auth: {
    user: 'business@insightpulseai.com',
    pass: process.env.ZOHO_PASS
  }
});
transport.verify().then(console.log).catch(console.error);
"
```

### "Supabase RPC error"

**Problem**: Migration not deployed or RLS blocking access

**Fix**:
```bash
# Verify functions exist
psql "postgres://postgres.spdtwktxdalcfigzeqrz:PASSWORD@..." <<'SQL'
\df registry.*invite*
SQL

# Should show 4 functions
```

---

## 7. Quick Reference

### File Locations

```
.env.example              → Template (commit)
.env.local                → Local secrets (gitignore)
supabase/config.toml      → Supabase CLI lock
supabase/migrations/      → Database migrations
scripts/deploy-production.sh → Automated deployment
docs/CONFIGURATION.md     → This file
```

### Commands

```bash
# Local dev
pnpm install
pnpm dev

# Build
pnpm build

# Deploy
vercel --prod

# Verify
./scripts/verify-org-invites.sh
```

### Support Links

- Supabase Dashboard: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz
- Vercel Dashboard: https://vercel.com/dashboard
- Zoho Mail: https://mail.zoho.com/
- Deployment Evidence: `docs/evidence/20260212-0711/DEPLOYMENT.md`

---

**Last Updated**: 2026-02-12
