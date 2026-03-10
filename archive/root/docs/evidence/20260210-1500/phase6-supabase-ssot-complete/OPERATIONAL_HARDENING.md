# Supabase SSOT - Operational Hardening Checklist

**Status**: ⏳ **PENDING USER ACTION**
**Date**: 2026-02-10 15:00 UTC

## Overview

Core Supabase SSOT migration is complete. Remaining tasks are operational hardening for production deployment:
1. **CI Secrets Provisioning** - Push secrets to GitHub Actions for automated deployments
2. **Zoho Password Rotation** - Rotate compromised SMTP app password

---

## Task 1: Provision GitHub Actions Secrets ⏳

**Why**: CI/CD workflow needs encrypted secrets to deploy Edge Secrets and Auth config automatically.

**Prerequisites**:
- `SUPABASE_ACCESS_TOKEN` - Supabase Management API token (PAT) with project access
- `.env.platform.local` - Local dev environment file with all secrets

**Commands**:
```bash
cd ~/Documents/GitHub/Insightpulseai/odoo

# Load local env
set -a
source .env.platform.local
set +a

# Required: Set Management API token
export SUPABASE_ACCESS_TOKEN="<YOUR_SUPABASE_PAT>"

# Push all secrets to GitHub Actions
./scripts/supabase/gh_actions_secrets_apply.sh Insightpulseai/odoo .env.platform.local
```

**Expected Output**:
```
📦 Applying GitHub Actions Secrets to Insightpulseai/odoo
====================================================

→ Loading secrets from: .env.platform.local
→ Validating required secrets...
  ✓ Found: SUPABASE_PROJECT_REF
  ✓ Found: SUPABASE_ACCESS_TOKEN
  ✓ Found: OPENAI_API_KEY
  ✓ Found: ANTHROPIC_API_KEY
  ✓ Found: AUTH_JWT_ISSUER

→ Deriving optional secrets...
  ✓ SMTP_FROM (from target)
  ✓ SMTP_HOST (from source)
  ✓ SMTP_PORT (from source)
  ✓ SMTP_USER (from source)
  ✓ SMTP_PASS (from source)
  ✓ AUTH_SITE_URL (from source)

→ Pushing secrets to GitHub Actions...
  ✓ SUPABASE_PROJECT_REF
  ✓ SUPABASE_ACCESS_TOKEN
  ✓ OPENAI_API_KEY
  ✓ ANTHROPIC_API_KEY
  ✓ AUTH_JWT_ISSUER
  ✓ SMTP_FROM
  ✓ SMTP_HOST
  ✓ SMTP_PORT
  ✓ SMTP_USER
  ✓ SMTP_PASS
  ✓ AUTH_SITE_URL
  ✓ AUTH_ADDITIONAL_REDIRECT_URLS

✅ GitHub Actions secrets applied successfully!

Total secrets: 12
Repository: Insightpulseai/odoo
```

**Verification**:
```bash
# List GitHub Actions secrets
gh secret list -R Insightpulseai/odoo

# Trigger CI workflow (manual dispatch)
gh workflow run supabase-secrets-deploy.yml -R Insightpulseai/odoo

# Check workflow run status
gh run list -R Insightpulseai/odoo --limit 10
```

---

## Task 2: Rotate Zoho SMTP Password ⚠️ CRITICAL

**Why**: Current password `5Kww9uyvJcb7` was exposed in chat logs and must be rotated.

**Prerequisites**:
1. Generate new Zoho app-specific password in [Zoho Admin Console](https://accounts.zoho.com/home#security/app-passwords)
2. Have `gh` CLI authenticated for GitHub Actions secret updates

**One-Shot Rotation Script** (Automated):
```bash
cd ~/Documents/GitHub/Insightpulseai/odoo

# Generate new password in Zoho first, then run:
./scripts/supabase/rotate_zoho_password.sh "<NEW_ZOHO_APP_PASSWORD>"
```

**What This Script Does**:
1. ✅ Backs up `.env.platform.local` (timestamped backup)
2. ✅ Updates `ZOHO_SMTP_PASS` in `.env.platform.local`
3. ✅ Pushes `SMTP_PASS` to GitHub Actions secrets
4. ✅ Re-applies Supabase Auth SMTP configuration
5. ✅ Verifies Edge Secrets health (should be unaffected)
6. ✅ Tests Magic Link flow (waits 60s for rate limit)
7. ✅ Tests Email OTP flow

**Expected Output**:
```
🔐 Rotating Zoho SMTP Password
====================================================

→ Step 1/5: Updating .env.platform.local...
  ✓ Backup created: .env.platform.local.bak.20260210-150000
  ✓ Updated ZOHO_SMTP_PASS in .env.platform.local

→ Step 2/5: Updating GitHub Actions secret...
  ✓ SMTP_PASS secret updated in Insightpulseai/odoo

→ Step 3/5: Re-applying Supabase Auth SMTP configuration...
  ✓ Supabase Auth SMTP config updated

→ Step 4/5: Verifying Edge Secrets health...
  ✅ Secret smoke test PASSED

→ Step 5/5: Testing Auth flows...
  Testing Magic Link...
  ✅ Magic Link sent successfully! (HTTP 200)

  ⏳ Waiting 60s for rate limit reset...

  Testing Email OTP...
  ✅ Email OTP sent successfully! (HTTP 200)

====================================================
✅ Zoho Password Rotation Complete!

Summary:
  ✓ .env.platform.local updated
  ✓ GitHub Actions SMTP_PASS secret updated
  ✓ Supabase Auth SMTP config re-applied
  ✓ Edge Secrets health verified
  ✓ Auth flows smoke tested

Next steps:
  1. Check business@insightpulseai.com inbox for test emails
  2. Verify Magic Link and OTP emails received successfully
  3. Delete backup: rm .env.platform.local.bak.*
```

**Manual Rotation** (Alternative):
If you prefer manual control:
```bash
cd ~/Documents/GitHub/Insightpulseai/odoo

# 1. Update .env.platform.local
perl -i -pe 's/^ZOHO_SMTP_PASS=.*/ZOHO_SMTP_PASS=<NEW_PASSWORD>/' .env.platform.local

# 2. Reload env
set -a
source .env.platform.local
set +a

# 3. Update GitHub Actions secret
gh secret set SMTP_PASS -R Insightpulseai/odoo --body "<NEW_PASSWORD>"

# 4. Re-apply Supabase Auth config
./scripts/supabase/configure_auth_smtp_and_urls.sh

# 5. Test
./scripts/supabase/invoke_secret_smoke.sh
sleep 60
./scripts/supabase/test_magic_link_curl.sh
sleep 60
./scripts/supabase/test_email_otp_curl.sh
```

---

## Task 3: Verify Git History Clean ✅ (Optional)

**Why**: Ensure compromised password never committed to git.

**Commands**:
```bash
cd ~/Documents/GitHub/Insightpulseai/odoo

# Search for exposed Zoho password
git log --all -S'5Kww9uyvJcb7'

# Search for exposed JWT secret
git log --all -S'Zk3D3Zh+XZBjEw0v2bqhoyWU2KCO9VzTHuEhh7hNxuM='
```

**Expected**: No results (already verified clean in `docs/evidence/20260210-0709/mail_and_auth_complete.md`)

---

## Post-Hardening Verification

After completing Tasks 1 and 2, run comprehensive verification:

```bash
cd ~/Documents/GitHub/Insightpulseai/odoo
set -a; source .env.platform.local; set +a

# 1. Edge Secrets health
./scripts/supabase/invoke_secret_smoke.sh
# Expected: {"ok": true, "present": 7, "missing": 0}

# 2. Auth config verification
./scripts/supabase/verify_auth_config.sh
# Expected: ✅ All Auth config present

# 3. Auth health endpoint
curl -sS "${SUPABASE_URL}/auth/v1/health" -H "apikey: ${SUPABASE_ANON_KEY}" | jq .
# Expected: {"name": "GoTrue", "version": "...", "description": "GoTrue is a user..."}

# 4. Magic Link flow
./scripts/supabase/test_magic_link_curl.sh
# Expected: HTTP 200, email sent

# 5. Email OTP flow (wait 60s for rate limit)
sleep 60
./scripts/supabase/test_email_otp_curl.sh
# Expected: HTTP 200 or HTTP 429 (rate limited)

# 6. Check email inbox
# Expected: Emails received at business@insightpulseai.com
```

---

## CI Workflow Testing

After GitHub Actions secrets provisioned:

```bash
cd ~/Documents/GitHub/Insightpulseai/odoo

# List workflows
gh workflow list -R Insightpulseai/odoo | grep supabase

# Trigger Supabase secrets deploy workflow
gh workflow run supabase-secrets-deploy.yml -R Insightpulseai/odoo

# Check run status
gh run list -R Insightpulseai/odoo --limit 10

# View logs if needed
gh run view <RUN_ID> -R Insightpulseai/odoo --log
```

---

## Rollback Procedures

### Rollback Zoho Password

If new password doesn't work:
```bash
cd ~/Documents/GitHub/Insightpulseai/odoo

# Restore backup
cp .env.platform.local.bak.<TIMESTAMP> .env.platform.local

# Re-apply old password
set -a; source .env.platform.local; set +a
./scripts/supabase/configure_auth_smtp_and_urls.sh
gh secret set SMTP_PASS -R Insightpulseai/odoo --body "$ZOHO_SMTP_PASS"
```

### Rollback GitHub Actions Secrets

```bash
# Delete all secrets
gh secret list -R Insightpulseai/odoo | awk '{print $1}' | xargs -I {} gh secret delete {} -R Insightpulseai/odoo

# Re-apply from backup
./scripts/supabase/gh_actions_secrets_apply.sh Insightpulseai/odoo .env.platform.local.bak.<TIMESTAMP>
```

---

## Security Notes

1. **SUPABASE_ACCESS_TOKEN**:
   - Never push to Edge Secrets (only GitHub Actions)
   - High privilege token - rotate if compromised
   - Stored in GitHub Actions secrets only

2. **Zoho Password**:
   - Generate app-specific password, not main account password
   - Rotate quarterly for compliance
   - Old password becomes invalid after rotation

3. **API Key Rotation**:
   - Anon/Service Role keys rotated automatically by Supabase
   - Use `fetch_project_api_keys.sh` to retrieve current keys
   - Update `.env.platform.local` if keys change

4. **GitHub Actions Secrets**:
   - Encrypted at rest by GitHub
   - Only accessible by workflows in same repo
   - Audit secret access via workflow logs

---

## Timeline

- **Task 1**: ~5 minutes (CI secrets provisioning)
- **Task 2**: ~10 minutes (password rotation + verification)
- **Task 3**: ~1 minute (git history check)

**Total**: ~15-20 minutes for complete operational hardening.

---

## Success Criteria

- ✅ All GitHub Actions secrets provisioned (12 total)
- ✅ Zoho password rotated and verified working
- ✅ Magic Link emails received successfully
- ✅ Email OTP codes received successfully
- ✅ Edge Secrets health check passing (7/7)
- ✅ Auth config verification passing
- ✅ CI workflow can trigger successfully
- ✅ Git history clean (no exposed secrets)

---

**Status**: Ready for user execution. All scripts created and tested.
