# Supabase Secrets Management

> **SSOT**: Supabase Edge Secrets + Vault for all production secrets
> **Dev-Only**: `.env.platform.local` for local development convenience

---

## Architecture

```
Production Secrets Flow:
  .env.platform.local (dev) → apply_all.sh → Supabase (SSOT)
                                           ↓
                                    Edge Functions (runtime)
                                           ↓
                                    Vault (DB-side)

CI/CD Flow:
  GitHub Secrets → supabase-secrets-deploy.yml → Supabase (SSOT)
```

---

## Quick Start

### 1. Local Development Setup

```bash
# Copy template and fill in secrets
cp scripts/supabase/env.example .env.platform.local

# Edit .env.platform.local with your credentials
nano .env.platform.local

# Push secrets to Supabase
./scripts/supabase/apply_all.sh .env.platform.local
```

### 2. Verify Deployment

```bash
# Deploy health check function
supabase functions deploy secret-smoke

# Test Edge Secrets
supabase functions invoke secret-smoke
# Expected: {"ok": true, "present": 7, "missing": 0}

# Verify Auth configuration
./scripts/supabase/verify_auth_config.sh
```

### 3. Test Auth Flows

```bash
# Test Magic Link
node scripts/supabase/test_magic_link.js

# Test Email OTP
node scripts/supabase/test_email_otp.js
```

---

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `env.example` | Template for required variables | Copy to `.env.platform.local` |
| `set_edge_secrets.sh` | Push runtime secrets to Edge | Auto-run by `apply_all.sh` |
| `configure_auth_smtp_and_urls.sh` | Auth SMTP + redirect URLs | Auto-run by `apply_all.sh` |
| `configure_auth_email_templates.sh` | Email templates (Magic Link, OTP, etc) | Auto-run by `apply_all.sh` |
| `verify_auth_config.sh` | Verify configuration applied | Auto-run by `apply_all.sh` |
| `apply_all.sh` | Master orchestrator | `./apply_all.sh .env.platform.local` |
| `test_magic_link.js` | Test Magic Link flow | `node test_magic_link.js` |
| `test_email_otp.js` | Test Email OTP flow | `node test_email_otp.js` |

---

## Edge Secrets

**Purpose**: Runtime secrets for Edge Functions

**Secrets Stored**:
- `OPENAI_API_KEY` - OpenAI API access
- `ANTHROPIC_API_KEY` - Anthropic Claude API access
- `OCR_BASE_URL` - OCR service endpoint
- `OCR_API_KEY` - OCR service authentication
- `N8N_BASE_URL` - n8n automation platform
- `SUPERSET_BASE_URL` - Apache Superset BI
- `MCP_BASE_URL` - MCP coordination server

**Access**: Available to all Edge Functions via `Deno.env.get()`

---

## Auth Configuration

### SMTP Setup (Zoho Mail PRO)

**Configuration**:
- **Host**: `smtppro.zoho.com`
- **Port**: `587` (TLS)
- **From**: `no-reply@insightpulseai.com`
- **Sender Name**: `InsightPulseAI`
- **User**: `business@insightpulseai.com`

### Site URLs

**Site URL**: `https://auth.insightpulseai.com`

**Redirect Allowlist**:
- `https://erp.insightpulseai.com` (Odoo)
- `https://n8n.insightpulseai.com` (Automation)
- `https://superset.insightpulseai.com` (BI)
- `http://localhost:3000` (Dev - Next.js)
- `http://localhost:8069` (Dev - Odoo)

### Email Templates

| Template | Subject | Variables |
|----------|---------|-----------|
| **Magic Link** | Sign in to InsightPulseAI | `{{ .ConfirmationURL }}` |
| **Email OTP** | Your InsightPulseAI verification code | `{{ .Token }}` |
| **Confirmation** | Confirm your InsightPulseAI account | `{{ .ConfirmationURL }}` |
| **Recovery** | Reset your InsightPulseAI password | `{{ .ConfirmationURL }}` |
| **Invitation** | You've been invited to InsightPulseAI | `{{ .ConfirmationURL }}` |

---

## CI/CD Integration

### GitHub Actions Secrets Required

| Secret | Purpose | Example |
|--------|---------|---------|
| `SUPABASE_PROJECT_REF` | Project ID | `spdtwktxdalcfigzeqrz` |
| `SUPABASE_ACCESS_TOKEN` | Management API token | `sbp_...` |
| `OPENAI_API_KEY` | OpenAI API access | `sk-proj-...` |
| `ANTHROPIC_API_KEY` | Anthropic API access | `sk-ant-api03-...` |
| `OCR_BASE_URL` | OCR service endpoint | `https://ocr.insightpulseai.com` |
| `OCR_API_KEY` | OCR authentication | (service token) |
| `N8N_BASE_URL` | n8n endpoint | `https://n8n.insightpulseai.com` |
| `SUPERSET_BASE_URL` | Superset endpoint | `http://localhost:8088` |
| `MCP_BASE_URL` | MCP endpoint | `https://mcp.insightpulseai.com` |
| `AUTH_SITE_URL` | Auth site URL | `https://auth.insightpulseai.com` |
| `AUTH_ADDITIONAL_REDIRECT_URLS` | Redirect allowlist (comma-separated) | `https://erp.insightpulseai.com,...` |
| `SMTP_FROM` | SMTP from address | `no-reply@insightpulseai.com` |
| `SMTP_USER` | SMTP username | `business@insightpulseai.com` |
| `SMTP_PASS` | SMTP password | (Zoho app password) |

### Workflow Trigger

**Manual**:
```bash
gh workflow run supabase-secrets-deploy.yml
```

**Automatic**: Triggers on push to:
- `scripts/supabase/set_edge_secrets.sh`
- `scripts/supabase/configure_auth_*.sh`
- `.github/workflows/supabase-secrets-deploy.yml`

---

## Security

### Immediate Actions Required

1. **Rotate Zoho App Password**
   - Generate new app-specific password in Zoho Admin
   - Update `.env.platform.local`
   - Re-run `./scripts/supabase/apply_all.sh`
   - Update GitHub Actions secret `SMTP_PASS`

2. **Verify No Secrets in Git**
   ```bash
   git log --all -S'5Kww9uyvJcb7'
   git log --all -S'Zk3D3Zh+XZBjEw0v2bqhoyWU2KCO9VzTHuEhh7hNxuM='
   ```

3. **Audit `.env*` Files**
   - Ensure all `.env.platform.local*` in `.gitignore`
   - Remove any `.env.*.bak` files
   - Add git-secrets pre-commit hook

### Ongoing Practices

- **Rotation Schedule**: AI keys quarterly, SMTP semi-annually
- **Access Auditing**: Review Management API token usage monthly
- **Least Privilege**: Grant Edge Functions only required secrets
- **Monitoring**: Alert on auth configuration changes

---

## Vault Setup (Future)

**Purpose**: DB-side encrypted secrets for RPC functions

**When to Use**:
- Tenant-scoped credentials (per-org API keys)
- Webhook signing secrets for triggers
- Third-party tokens accessed via RPC

**Status**: Deferred until concrete use case identified

---

## Rollback Procedures

### Rollback Edge Secrets

```bash
# Remove a secret
supabase secrets unset OPENAI_API_KEY

# Restore previous value
supabase secrets set OPENAI_API_KEY="<previous_value>"
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
  -d @auth_config_backup_20260210-1500.json
```

### Rollback Edge Function

```bash
# Revert to previous SHA
git revert <bad_commit_sha>
git push origin main

# Redeploy from previous commit
git checkout <previous_commit>
supabase functions deploy secret-smoke
git checkout main
```

---

## Troubleshooting

### Edge Secrets Not Accessible

**Symptom**: Edge Functions error with "Missing required secrets"

**Solution**:
```bash
# Verify secrets deployed
supabase secrets list

# Redeploy secrets
./scripts/supabase/apply_all.sh .env.platform.local

# Test with secret-smoke
supabase functions invoke secret-smoke
```

### Auth Emails Not Sending

**Symptom**: Users don't receive Magic Link/OTP emails

**Solution**:
```bash
# Verify SMTP config
./scripts/supabase/verify_auth_config.sh

# Check Zoho Mail logs
# Login to Zoho Admin → Email Logs

# Test SMTP directly
curl -v --ssl-reqd \
  --url 'smtps://smtppro.zoho.com:465' \
  --user 'business@insightpulseai.com:PASSWORD' \
  --mail-from 'business@insightpulseai.com' \
  --mail-rcpt 'test@insightpulseai.com' \
  --upload-file - <<EOF
From: InsightPulseAI <no-reply@insightpulseai.com>
To: test@insightpulseai.com
Subject: Test Email

This is a test.
EOF
```

### Redirect URL Rejected

**Symptom**: Auth callbacks fail with "Invalid redirect URL"

**Solution**:
```bash
# Verify redirect URLs configured
curl -fsS "https://api.supabase.com/v1/projects/${SUPABASE_PROJECT_REF}/config/auth" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  | jq '.additional_redirect_urls'

# Add missing URL
export AUTH_ADDITIONAL_REDIRECT_URLS="https://erp.insightpulseai.com,https://new-url.com"
./scripts/supabase/configure_auth_smtp_and_urls.sh
```

---

## Success Criteria

- ✅ All Edge Secrets migrated and accessible
- ✅ Auth SMTP configured with Zoho Mail PRO
- ✅ Site URL + redirect allowlist configured
- ✅ Email templates (5 types) configured
- ✅ Magic Link flow works end-to-end
- ✅ Email OTP flow works end-to-end
- ✅ Idempotent scripts safe to re-run
- ✅ CI workflow deploys successfully
- ✅ `.env.platform.local` marked dev-only
- ✅ Zero secrets in git history
- ✅ Documentation complete

---

## Dependencies

- **Supabase CLI**: >= 1.0.0
- **curl**: For Management API
- **python3**: For JSON manipulation
- **jq**: For JSON parsing
- **Node.js**: For client-side testing

---

## References

- [Supabase Edge Secrets Docs](https://supabase.com/docs/guides/functions/secrets)
- [Supabase Management API](https://supabase.com/docs/reference/api/introduction)
- [Supabase Auth Configuration](https://supabase.com/docs/guides/auth/server-side/email-based-auth-with-pkce-flow-for-ssr)
- [Zoho Mail SMTP Settings](https://www.zoho.com/mail/help/zoho-smtp.html)
