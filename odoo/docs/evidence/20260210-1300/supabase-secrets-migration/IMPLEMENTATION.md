# Supabase Secrets Migration Implementation

**Date**: 2026-02-10 13:00
**Status**: ✅ Implemented (awaiting deployment)
**Agent**: Claude Code (Sonnet 4.5)

---

## Summary

Implemented complete Supabase SSOT architecture for secrets management, migrating from flat `.env.platform.local` files to:
1. **Edge Secrets** for runtime access in Edge Functions
2. **Management API** configuration for Auth (SMTP, URLs, email templates)
3. **CI/CD workflow** for automated deployment
4. **Dev-only** flag for local `.env.platform.local`

---

## Files Created

### Scripts (8 files)

1. **`scripts/supabase/env.example`**
   - Template for required environment variables
   - 44 secrets across 8 domains
   - Copy to `.env.platform.local` for local dev

2. **`scripts/supabase/set_edge_secrets.sh`**
   - Push runtime secrets to Edge Secrets
   - Idempotent (safe to re-run)
   - Verifies prerequisites before execution

3. **`scripts/supabase/configure_auth_smtp_and_urls.sh`**
   - Configure Auth SMTP (Zoho Mail PRO)
   - Set site URL + redirect allowlist
   - Uses Management API (no UI clicks)

4. **`scripts/supabase/configure_auth_email_templates.sh`**
   - Configure 5 email templates:
     - Magic Link (clickable URL)
     - Email OTP (6-digit code)
     - Account Confirmation
     - Password Recovery
     - User Invitation
   - Uses template variables: `{{ .ConfirmationURL }}`, `{{ .Token }}`

5. **`scripts/supabase/verify_auth_config.sh`**
   - Verify configuration applied successfully
   - Checks site URL, SMTP, redirect URLs, templates
   - Returns exit code 0 (success) or 1 (failure)

6. **`scripts/supabase/apply_all.sh`**
   - Master orchestrator for all configuration
   - Runs all scripts in sequence
   - Usage: `./apply_all.sh .env.platform.local`

7. **`scripts/supabase/test_magic_link.js`**
   - Test Magic Link authentication flow
   - Sends magic link to test email
   - Verifies email delivery

8. **`scripts/supabase/test_email_otp.js`**
   - Test Email OTP authentication flow
   - Sends 6-digit code to test email
   - Verifies OTP delivery

### Edge Function

**`supabase/functions/secret-smoke/index.ts`**
- Health check for Edge Secrets
- Verifies presence (not values) of 7 required secrets
- Returns 200 if all present, 500 if any missing
- Output: `{"ok": true, "present": 7, "missing": 0}`

### CI/CD Workflow

**`.github/workflows/supabase-secrets-deploy.yml`**
- Deploy secrets to Supabase via CI
- Manual trigger only (security)
- Auto-trigger on script changes
- Steps:
  1. Deploy Edge Secrets
  2. Configure Auth SMTP/URLs
  3. Configure Email Templates
  4. Verify Configuration
  5. Deploy Secret Smoke Function
  6. Test Secret Smoke Function

### Documentation

**`scripts/supabase/README.md`**
- Complete reference for secrets management
- Quick start guide
- Scripts reference table
- Security checklist
- Troubleshooting guide
- Success criteria

---

## Configuration Changes

### `.env.platform.local`

**Added Header**:
```bash
# ========================================
# DEV-ONLY SECRETS (never deploy this file)
# ========================================
# Production SSOT: Supabase Edge Secrets + Vault
# This file is for local development convenience only.
# To push to production: ./scripts/supabase/apply_all.sh .env.platform.local
# ========================================
```

**Purpose**: Mark file as dev-only to prevent accidental deployment

---

## Architecture

### Before (Flat Files)

```
.env.platform.local → (gitignored but risk of leak)
                    ↓
         Local dev + Production (confused contexts)
```

### After (Supabase SSOT)

```
Development:
  .env.platform.local → apply_all.sh → Supabase Edge Secrets (SSOT)

Production:
  GitHub Secrets → CI Workflow → Supabase Edge Secrets (SSOT)
                                       ↓
                               Edge Functions (runtime)
                                       ↓
                               Vault (DB-side, future)
```

---

## Edge Secrets Migrated

| Secret | Purpose | Access |
|--------|---------|--------|
| `OPENAI_API_KEY` | OpenAI API access | All Edge Functions |
| `ANTHROPIC_API_KEY` | Anthropic Claude API | All Edge Functions |
| `OCR_BASE_URL` | OCR service endpoint | OCR-related functions |
| `OCR_API_KEY` | OCR authentication | OCR-related functions |
| `N8N_BASE_URL` | n8n automation | Workflow functions |
| `SUPERSET_BASE_URL` | Apache Superset BI | Analytics functions |
| `MCP_BASE_URL` | MCP coordination | Agent functions |

---

## Auth Configuration

### SMTP (Zoho Mail PRO)

| Setting | Value |
|---------|-------|
| **Host** | `smtppro.zoho.com` |
| **Port** | `587` (TLS) |
| **User** | `business@insightpulseai.com` |
| **From** | `no-reply@insightpulseai.com` |
| **Sender** | `InsightPulseAI` |

### Site URLs

| Type | URL |
|------|-----|
| **Site URL** | `https://auth.insightpulseai.com` |
| **Redirects** | `https://erp.insightpulseai.com` |
|  | `https://n8n.insightpulseai.com` |
|  | `https://superset.insightpulseai.com` |
|  | `http://localhost:3000` (dev) |
|  | `http://localhost:8069` (dev) |

### Email Templates

| Template | Subject | Variables |
|----------|---------|-----------|
| **Magic Link** | Sign in to InsightPulseAI | `{{ .ConfirmationURL }}` |
| **Email OTP** | Your verification code | `{{ .Token }}` |
| **Confirmation** | Confirm your account | `{{ .ConfirmationURL }}` |
| **Recovery** | Reset your password | `{{ .ConfirmationURL }}` |
| **Invitation** | You've been invited | `{{ .ConfirmationURL }}` |

---

## Security Improvements

### Before

- ❌ Secrets in flat file (`.env.platform.local`)
- ❌ Same file used for dev and prod contexts
- ❌ No rotation mechanism
- ❌ No audit trail
- ❌ Risk of git commit leak

### After

- ✅ Secrets in Supabase Edge Secrets (encrypted at rest)
- ✅ Clear dev/prod separation
- ✅ Rotation via script re-run
- ✅ Audit via Supabase Logs
- ✅ Git history clean (dev-only marker)

---

## Verification Steps

### 1. Deploy Edge Secrets

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
./scripts/supabase/apply_all.sh .env.platform.local
```

**Expected Output**:
```
🚀 Supabase Secrets Migration - Master Orchestrator
====================================================

Step 1/4: Deploying Edge Secrets...
→ Linking to Supabase project spdtwktxdalcfigzeqrz...
→ Setting Edge Secrets...
✅ Edge Secrets deployed successfully

Step 2/4: Configuring Auth SMTP and URLs...
→ Applying configuration via Management API...
✅ Auth SMTP and URLs configured successfully

Step 3/4: Configuring Email Templates...
→ Applying email templates via Management API...
✅ Email templates configured successfully

Step 4/4: Verifying Configuration...
→ Checking configuration...
  ✅ site_url: https://auth.insightpulseai.com
  ✅ smtp_host: smtppro.zoho.com
  ✅ additional_redirect_urls: 5 URLs
  ✅ Magic Link template: Sign in to InsightPulseAI
  ✅ Email OTP template: Your InsightPulseAI verification code

✅ All auth configuration verified successfully

====================================================
✅ All configuration applied successfully!
```

### 2. Deploy Secret Smoke Function

```bash
supabase functions deploy secret-smoke
```

**Expected Output**:
```
Deploying function secret-smoke (project ref: spdtwktxdalcfigzeqrz)
Function deployed successfully
```

### 3. Test Secret Smoke

```bash
supabase functions invoke secret-smoke
```

**Expected Output**:
```json
{
  "ok": true,
  "present": 7,
  "missing": 0,
  "missingSecrets": [],
  "timestamp": "2026-02-10T13:00:00.000Z"
}
```

### 4. Test Magic Link

```bash
export SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
export SUPABASE_ANON_KEY="eyJhbGc..."
export TEST_EMAIL="test@insightpulseai.com"
node scripts/supabase/test_magic_link.js
```

**Expected Output**:
```
🔗 Testing Magic Link Flow...
→ Sending magic link to: test@insightpulseai.com
✅ Magic Link sent successfully
→ Check email inbox for magic link
→ Link expires in 24 hours
```

### 5. Test Email OTP

```bash
node scripts/supabase/test_email_otp.js
```

**Expected Output**:
```
🔢 Testing Email OTP Flow...
→ Sending OTP to: test@insightpulseai.com
✅ OTP sent successfully
→ Check email inbox for 6-digit code
→ Code expires in 5 minutes
```

---

## Immediate Actions Required

### 1. Rotate Zoho App Password

**Reason**: Current password exposed in previous chat

**Steps**:
1. Login to Zoho Admin: https://admin.zoho.com
2. Navigate to: Security & Compliance → Application-Specific Passwords
3. Generate new password for "Supabase Auth"
4. Update `.env.platform.local`:
   ```bash
   ZOHO_SMTP_PASS=<new_password>
   ```
5. Re-run migration:
   ```bash
   ./scripts/supabase/apply_all.sh .env.platform.local
   ```
6. Update GitHub Actions secret:
   ```bash
   gh secret set SMTP_PASS --body "<new_password>"
   ```

### 2. Verify No Secrets in Git History

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo

# Check for exposed Zoho password
git log --all -S'5Kww9uyvJcb7'

# Check for exposed JWT secret
git log --all -S'Zk3D3Zh+XZBjEw0v2bqhoyWU2KCO9VzTHuEhh7hNxuM='

# If found, use BFG Repo-Cleaner to remove from history
```

### 3. Add GitHub Actions Secrets

```bash
# Supabase
gh secret set SUPABASE_PROJECT_REF --body "spdtwktxdalcfigzeqrz"
gh secret set SUPABASE_ACCESS_TOKEN --body "<management_api_token>"

# AI Providers
gh secret set OPENAI_API_KEY --body "<key>"
gh secret set ANTHROPIC_API_KEY --body "<key>"

# OCR Service
gh secret set OCR_BASE_URL --body "https://ocr.insightpulseai.com"
gh secret set OCR_API_KEY --body "<key>"

# Internal Services
gh secret set N8N_BASE_URL --body "https://n8n.insightpulseai.com"
gh secret set SUPERSET_BASE_URL --body "http://localhost:8088"
gh secret set MCP_BASE_URL --body "https://mcp.insightpulseai.com"

# Auth URLs
gh secret set AUTH_SITE_URL --body "https://auth.insightpulseai.com"
gh secret set AUTH_ADDITIONAL_REDIRECT_URLS --body "https://erp.insightpulseai.com,https://n8n.insightpulseai.com,https://superset.insightpulseai.com,http://localhost:3000,http://localhost:8069"

# Zoho SMTP
gh secret set SMTP_FROM --body "no-reply@insightpulseai.com"
gh secret set SMTP_USER --body "business@insightpulseai.com"
gh secret set SMTP_PASS --body "<zoho_app_password>"
```

---

## Success Criteria

- ✅ Scripts created and executable
- ✅ Edge Function health check implemented
- ✅ CI/CD workflow configured
- ✅ Documentation complete
- ✅ `.env.platform.local` marked dev-only
- ⏳ Edge Secrets deployed (awaiting user action)
- ⏳ Auth configuration applied (awaiting user action)
- ⏳ Magic Link tested (awaiting user action)
- ⏳ Email OTP tested (awaiting user action)
- ⏳ Zoho password rotated (awaiting user action)
- ⏳ GitHub Actions secrets added (awaiting user action)

---

## Rollback Plan

### Rollback Edge Secrets

```bash
# Save current secrets
supabase secrets list > secrets_backup_$(date +%Y%m%d-%H%M).txt

# Remove all secrets
supabase secrets unset OPENAI_API_KEY ANTHROPIC_API_KEY OCR_BASE_URL OCR_API_KEY N8N_BASE_URL SUPERSET_BASE_URL MCP_BASE_URL

# Restore from backup (manual)
```

### Rollback Auth Configuration

```bash
# Save current config
curl -fsS "https://api.supabase.com/v1/projects/${SUPABASE_PROJECT_REF}/config/auth" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  > auth_config_backup_$(date +%Y%m%d-%H%M).json

# Restore from backup
curl -fsS -X PATCH "https://api.supabase.com/v1/projects/${SUPABASE_PROJECT_REF}/config/auth" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d @auth_config_backup_20260210-1300.json
```

### Rollback Git Changes

```bash
# Revert commit
git revert <commit_sha>
git push origin main

# Or reset (destructive)
git reset --hard HEAD~1
git push --force origin main
```

---

## Next Steps

1. **Deploy**: Run `./scripts/supabase/apply_all.sh .env.platform.local`
2. **Verify**: Test secret-smoke, magic link, email OTP
3. **Rotate**: Change Zoho password + update GitHub secrets
4. **Monitor**: Check Supabase Logs for auth email delivery
5. **Document**: Update team runbook with new procedures

---

## References

- Plan: `/Users/tbwa/.claude/projects/-Users-tbwa-Documents-GitHub-Insightpulseai-odoo/2a564683-bee3-4fef-bb55-4c43e65bcd68.jsonl`
- Scripts: `scripts/supabase/`
- Docs: `scripts/supabase/README.md`
- Workflow: `.github/workflows/supabase-secrets-deploy.yml`
