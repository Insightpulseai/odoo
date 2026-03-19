# n8n Admin Setup Reference

**Purpose**: Reference guide for n8n admin account and initial configuration
**Status**: REFERENCE (not a completion claim)
**Timezone**: Asia/Manila (UTC+08:00)

---

## Overview

n8n requires first-time UI-based setup to create the initial owner/admin account. This is a **manual step** that cannot be automated via API.

**Verified Infrastructure**:
- ✅ Container: ipai-n8n (running, healthy)
- ✅ Database: Supabase PostgreSQL (migrations complete)
- ✅ SMTP: Zoho Mail configured
- ✅ Health: `{"status":"ok"}` at https://n8n.insightpulseai.com

**Manual Step Required**: First-time admin account creation (see IMPLEMENTATION_SUMMARY.md)

---

## Account Creation (UI-Only)

### Email Policy Compliance

**MUST use**: `devops@insightpulseai.com`

**Rationale**:
- Per `infra/identity/admin-email-policy.yaml` (SSOT)
- Rule E001: All infrastructure platforms must use devops@ as admin
- CI enforcement: `.github/workflows/email-policy-check.yml`

**Forbidden**:
- Personal emails (@gmail, @yahoo)
- Functional aliases (business@, support@, info@)
- System email alias (no-reply@) - only for outbound system emails

### Account Details

**Required Fields**:
- Email: `devops@insightpulseai.com`
- First Name: `DevOps`
- Last Name: `Admin`
- Password: Strong password (8+ characters, mixed case, numbers, symbols)

**Password Storage**:
```sql
-- Execute in Supabase SQL editor after account creation
INSERT INTO vault.secrets (name, secret, description, created_at)
VALUES (
  'n8n_admin_password',
  '[GENERATED_PASSWORD_HERE]',
  'n8n admin (devops@) password for automation platform',
  NOW()
);

-- Verify stored
SELECT name, description, created_at
FROM vault.secrets
WHERE name = 'n8n_admin_password';
```

---

## SMTP Configuration (Verified)

**Current Setup**:
```yaml
Provider: Zoho Mail
Host: smtp.zoho.com
Port: 587
User: no-reply@insightpulseai.com
From: no-reply@insightpulseai.com
TLS: Enabled (STARTTLS)
```

**Evidence**:
```bash
docker exec ipai-n8n env | grep -E '(EMAIL|SMTP)'
# N8N_EMAIL_MODE=smtp
# N8N_SMTP_HOST=smtp.zoho.com
# N8N_SMTP_PORT=587
# N8N_SMTP_USER=no-reply@insightpulseai.com
# N8N_SMTP_SENDER=no-reply@insightpulseai.com
```

**Functionality**:
- Password reset emails
- User invitation emails
- Workflow notification emails

**Test** (after admin account creation):
1. Click "Forgot Password" on login page
2. Enter: devops@insightpulseai.com
3. Verify email received with reset link
4. Confirm email sent from: no-reply@insightpulseai.com

---

## API Key Generation

**Purpose**: Programmatic access for automation workflows

**When**: After admin account creation

**Steps** (UI-required):
1. Login: https://n8n.insightpulseai.com
2. Navigate: Profile → Settings → API Keys
3. Create: Click "Create API Key"
4. Name: `automation_key` or `ci_cd_key`
5. Copy immediately (not shown again)

**Storage**:
```sql
INSERT INTO vault.secrets (name, secret, description)
VALUES (
  'n8n_api_key',
  '[API_KEY_HERE]',
  'n8n API key for automation workflows and CI/CD integration'
);
```

**Usage**:
```bash
# Test API access
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  https://n8n.insightpulseai.com/api/v1/workflows

# Expected: {"data": [...]} or {"data": []} if no workflows yet
```

---

## Security Hardening (Post-Setup)

### Two-Factor Authentication (Optional)

**Recommendation**: Enable for production admin accounts

**Steps** (UI):
1. Settings → Security → Two-Factor Authentication
2. Scan QR code with authenticator app
3. Verify with OTP code
4. Store backup codes in Vault

### Session Settings

**Current Defaults**:
- JWT secret: Auto-generated on container creation
- Encryption key: Set via N8N_ENCRYPTION_KEY env var
- Session timeout: Default (24 hours)

**Verification**:
```bash
docker exec ipai-n8n env | grep -E '(JWT|ENCRYPTION)'
# N8N_ENCRYPTION_KEY=[PRESENT]
```

### Webhook Security

**Current Setup**:
```yaml
Webhook URL: https://n8n.insightpulseai.com/
Protocol: HTTPS
Authentication: Token-based (per workflow)
```

**Best Practice**: Use webhook authentication in workflows that accept external triggers

---

## Verification Checklist

After admin account creation, verify:

- [ ] Login successful with devops@insightpulseai.com
- [ ] Password stored in Supabase Vault
- [ ] Email notifications work (test password reset)
- [ ] API key generated and stored
- [ ] 2FA enabled (if required for production)
- [ ] Webhook URL configured correctly

**Verification Script**: `sandbox/dev/scripts/verify-n8n-setup.sh`

---

## Troubleshooting

### Issue: Cannot Access n8n UI

**Symptom**: Browser cannot load https://n8n.insightpulseai.com

**Checks**:
```bash
# Health endpoint
curl -I https://n8n.insightpulseai.com/healthz
# Expected: HTTP/2 200 + {"status":"ok"}

# Container status
ssh root@178.128.112.214 "docker ps | grep ipai-n8n"
# Expected: Container "Up (healthy)"

# nginx routing
ssh root@178.128.112.214 "nginx -t"
# Expected: test is successful
```

### Issue: Password Reset Email Not Received

**Symptom**: Reset email not arriving in devops@ inbox

**Checks**:
```bash
# SMTP configured
docker exec ipai-n8n env | grep -i smtp
# Expected: All SMTP variables present

# Container logs
docker logs ipai-n8n --tail 100 | grep -i smtp
# Look for SMTP connection errors
```

**Possible Causes**:
1. Email in spam folder (check Zoho Mail spam)
2. Zoho app password incorrect (verify in ~/.zshrc)
3. SMTP rate limiting (wait 5 minutes, retry)
4. Wrong recipient email (must be exact: devops@insightpulseai.com)

### Issue: API Key Not Working

**Symptom**: API calls return 401 Unauthorized

**Checks**:
```bash
# Test with API key
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  https://n8n.insightpulseai.com/api/v1/workflows
# Expected: 200 response (not 401)
```

**Solutions**:
- Regenerate API key in n8n UI
- Verify no extra spaces in key
- Check key stored correctly in Vault
- Confirm correct header format: `X-N8N-API-KEY`

---

## Related Documentation

- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md` (primary reference)
- **Odoo Integration**: `ODOO_INTEGRATION_REFERENCE.md`
- **AI Integration**: `AI_INTEGRATION_REFERENCE.md`
- **Email Policy SSOT**: `infra/identity/admin-email-policy.yaml`
- **n8n Official Docs**: https://docs.n8n.io/hosting/installation/docker/

---

**Note**: This is a reference document, not a claim of completion. See `IMPLEMENTATION_SUMMARY.md` for current status and manual steps required.
