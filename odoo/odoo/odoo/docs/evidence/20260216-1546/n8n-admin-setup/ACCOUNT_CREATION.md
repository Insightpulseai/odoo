# n8n Admin Account Setup

**Date**: 2026-02-17
**n8n Version**: 2.2.4
**n8n URL**: https://n8n.insightpulseai.com
**Canonical Admin Email**: `devops@insightpulseai.com` (per email policy)

---

## Current Status

### n8n Service
- **Status**: ✅ HEALTHY
- **Health Check**: `{"status":"ok"}`
- **Container**: `c95d05274029_n8n-prod` (Up 5 weeks)
- **Port**: 5678 (reverse-proxied via nginx)

### Account Status
- **Setup Endpoint**: Returns "not found" (likely already configured)
- **Database**: SQLite exists with user table structure
- **CLI User Commands**: ❌ Not available in v2.2.4

---

## n8n Version 2.2.4 Notes

This version of n8n (2.2.4) **does not support CLI user management commands** like:
- ❌ `n8n user:create`
- ❌ `n8n user:reset-password`

**Available methods**:
1. ✅ Complete setup via web UI (if first-time)
2. ✅ Create additional users via Settings UI (if owner exists)
3. ✅ Password reset via "Forgot Password" link

---

## Recommended Setup Steps

### Step 1: Access n8n UI

Visit: **https://n8n.insightpulseai.com**

You will see one of two screens:

---

### Scenario A: Setup Wizard (First-Time)

**If you see**: "Welcome to n8n" setup screen

**Do this**:
1. ✅ Click "Get Started"
2. ✅ Create owner account:
   - **Email**: `devops@insightpulseai.com`
   - **First Name**: DevOps
   - **Last Name**: Admin
   - **Password**: (generate secure password)
3. ✅ Complete setup wizard
4. ✅ **Save credentials immediately** (see storage section below)

---

### Scenario B: Login Screen (Already Configured)

**If you see**: Login form

**Option 1 - Known Credentials**:
Try existing credentials from vault/password manager

**Option 2 - Forgot Password**:
1. Click "Forgot Password?"
2. Enter: `devops@insightpulseai.com` (or existing email)
3. Check email for reset link
4. Set new password
5. Save new credentials

**Option 3 - Check Existing Account**:
If you have access to another admin account:
1. Login with existing account
2. Go to: **Settings → Users**
3. Check if `devops@insightpulseai.com` exists
4. If not, create new user with Admin role

---

## Email Configuration

**Per Canonical Policy** (`docs/EMAIL_ALIAS_GUIDE.md`):

### Admin/Owner Account
- **Email**: `devops@insightpulseai.com`
- **Purpose**: System ownership, infrastructure alerts
- **Role**: Global Owner

### System Notifications
If n8n sends emails (notifications, alerts):
- **From**: `no-reply@insightpulseai.com`
- **Config**: Settings → Email Settings

### User Invitations
When inviting team members:
- **To**: Their actual work emails (e.g., `jake.tolentino@insightpulseai.com`)
- **From**: `no-reply@insightpulseai.com`

**Mapping**:
```yaml
n8n_owner: devops@insightpulseai.com      # Admin/infrastructure
n8n_smtp_from: no-reply@insightpulseai.com  # Automated emails
n8n_users: name@insightpulseai.com       # Individual accounts
```

---

## Credential Storage

**After creating/resetting password**, store in:

### Option 1: Supabase Vault (Recommended for Automation)
```sql
-- Store in Vault for MCP/n8n integration
INSERT INTO vault.secrets (name, secret, description)
VALUES (
  'n8n_admin_password',
  'YOUR_PASSWORD_HERE',
  'n8n admin (devops@insightpulseai.com) password'
);
```

### Option 2: Local Secrets (.zshrc)
```bash
# Add to ~/.zshrc for local access
export N8N_ADMIN_EMAIL="devops@insightpulseai.com"
export N8N_ADMIN_PASSWORD="YOUR_PASSWORD_HERE"
export N8N_BASE_URL="https://n8n.insightpulseai.com"
```

### Option 3: Password Manager
- **Service**: 1Password / Bitwarden / LastPass
- **Item Name**: "n8n Admin (devops@insightpulseai.com)"
- **URL**: https://n8n.insightpulseai.com
- **Username**: devops@insightpulseai.com
- **Password**: (generated password)
- **Notes**: System owner account per canonical email policy

---

## API Key Generation

**After logging in**, generate API key for automation:

1. Login to n8n
2. Go to: **Settings → API Keys** (or click your profile icon)
3. Click: **"Create API Key"**
4. Name: `FINANCE_AUTOMATION_KEY` (or `DEVOPS_AUTOMATION_KEY`)
5. **Copy the key immediately** (won't be shown again)

**Store API Key**:

### Supabase Vault
```sql
INSERT INTO vault.secrets (name, secret, description)
VALUES (
  'n8n_api_key',
  'YOUR_API_KEY_HERE',
  'n8n API key for automation workflows'
);
```

### Local Environment
```bash
# Add to ~/.zshrc
export N8N_API_KEY="YOUR_API_KEY_HERE"
```

---

## Verification Checklist

After setup:

- [ ] Login to https://n8n.insightpulseai.com successful
- [ ] Account email is `devops@insightpulseai.com`
- [ ] Account has "Global Owner" role
- [ ] Password stored in Vault/password manager
- [ ] API key generated and stored
- [ ] SMTP settings configured (if needed)
- [ ] Test workflow created and executed

---

## Common Issues

### Issue 1: Can't Access n8n UI

**Symptom**: Browser can't load https://n8n.insightpulseai.com

**Check**:
```bash
# Health check
curl https://n8n.insightpulseai.com/healthz
# Expected: {"status":"ok"}

# UI loads
curl -I https://n8n.insightpulseai.com
# Expected: HTTP/2 200
```

**Fix**: See `docs/evidence/20260216-1546/subdomain-routing-fix/`

---

### Issue 2: Forgot Password Not Working

**Symptom**: Reset email not received

**Possible Causes**:
1. n8n SMTP not configured
2. Email going to spam
3. Wrong email address

**Fix**:
```bash
# Check n8n SMTP config
ssh root@178.128.112.214
docker exec c95d05274029_n8n-prod env | grep -i smtp

# If SMTP not configured, need to access DB directly or recreate container with SMTP env vars
```

---

### Issue 3: PostHog Analytics Error

**Symptom**: Browser console shows `posthog-provider-D6HARb7w.js` error

**Impact**: ⚠️ NONE - Harmless analytics error

**Action**: Ignore (see `TROUBLESHOOTING.md`)

---

## Next Steps

After account creation:

1. **Configure Workflows** (per `docs/N8N_CREDENTIALS_BOOTSTRAP.md`):
   - Odoo REST/RPC credentials
   - Mattermost webhook (if still used) or Slack
   - Supabase credentials
   - GitHub API token

2. **Import Workflows**:
   - Finance PPM Alerts
   - CI Telemetry Router
   - BIR Deadline Alerts

3. **Test End-to-End**:
   - Trigger test workflow
   - Verify Slack/Mattermost notification
   - Verify Supabase write

---

## Related Documents

- `docs/N8N_CREDENTIALS_BOOTSTRAP.md` - Credential setup guide
- `docs/EMAIL_ALIAS_GUIDE.md` - Canonical email policy (SSOT)
- `docs/evidence/20260216-1546/subdomain-routing-fix/` - n8n routing fix
- `infra/mcp/provider-config.yaml` - MCP integration (future)

---

## Quick Commands Reference

```bash
# Health check
curl https://n8n.insightpulseai.com/healthz

# Check container logs
ssh root@178.128.112.214 "docker logs c95d05274029_n8n-prod --tail 50"

# Restart n8n (if needed)
ssh root@178.128.112.214 "docker restart c95d05274029_n8n-prod"

# Access n8n shell (advanced)
ssh root@178.128.112.214 "docker exec -it c95d05274029_n8n-prod sh"
```

---

**Status**: ⏳ PENDING USER ACTION
**Next**: Visit https://n8n.insightpulseai.com and complete setup
