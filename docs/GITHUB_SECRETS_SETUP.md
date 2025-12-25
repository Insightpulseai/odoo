# GitHub Secrets Configuration Guide

## Overview

The Finance PPM CI/CD pipeline requires 5 GitHub repository secrets to be configured before deployment.

## Required Secrets

### 1. DROPLET_SSH_KEY
**Purpose**: SSH private key for authenticating to production droplet
**Location**: Production droplet at 159.223.75.148
**How to Obtain**:

```bash
# Generate new SSH key pair (if not already exists)
ssh-keygen -t ed25519 -C "github-actions-finance-ppm" -f ~/.ssh/finance_ppm_deploy

# Copy public key to droplet
ssh-copy-id -i ~/.ssh/finance_ppm_deploy.pub root@159.223.75.148

# Get private key content for GitHub secret
cat ~/.ssh/finance_ppm_deploy
```

**GitHub Secret Value**: Complete private key content (including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`)

### 2. ODOO_ADMIN_PASSWORD
**Purpose**: Odoo admin password for XML-RPC authentication
**Location**: Odoo database `odoo_accounting`
**How to Obtain**:

```bash
# Option 1: From Odoo UI (Settings → Users → admin)
# Option 2: From environment variables
docker exec odoo-accounting printenv ADMIN_PASSWORD

# Option 3: From Odoo shell
docker exec odoo-accounting odoo-bin shell -d odoo_accounting
>>> env['res.users'].browse(1).password
```

**GitHub Secret Value**: Plain text admin password (e.g., `admin123` or secure password)

### 3. N8N_API_KEY
**Purpose**: n8n API key for workflow import
**Location**: n8n instance at https://ipa.insightpulseai.net
**How to Obtain**:

1. Login to n8n: https://ipa.insightpulseai.net
2. Navigate to: Settings → API Keys
3. Create new API key with name "GitHub Actions Finance PPM"
4. Copy the generated API key

**GitHub Secret Value**: n8n API key (e.g., `n8n_api_xxxxxxxxxxxxxxxx`)

### 4. SUPABASE_SERVICE_ROLE_KEY
**Purpose**: Supabase service role key for schema validation
**Location**: Supabase project `xkxyvboeubffxxbebsll`
**How to Obtain**:

1. Login to Supabase: https://supabase.com/dashboard
2. Navigate to project: `xkxyvboeubffxxbebsll`
3. Go to: Settings → API → Project API keys
4. Copy "service_role" key (NOT anon key)

**GitHub Secret Value**: Supabase service role JWT token (starts with `eyJhbGciOi...`)

### 5. MATTERMOST_WEBHOOK_URL
**Purpose**: Mattermost webhook URL for deployment notifications
**Location**: Mattermost instance
**How to Obtain**:

1. Login to Mattermost
2. Navigate to: Integrations → Incoming Webhooks
3. Create new webhook with:
   - Display Name: "Finance PPM Deployment Notifier"
   - Channel: #finance-ppm or #deployments
4. Copy the generated webhook URL

**GitHub Secret Value**: Complete webhook URL (e.g., `https://mattermost.insightpulseai.net/hooks/xxxxxxxxxxxxxx`)

## Setting GitHub Secrets

### Via GitHub Web UI

1. Navigate to repository: https://github.com/[YOUR_ORG]/odoo-ce
2. Go to: Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. For each secret:
   - Name: Use exact names above (e.g., `DROPLET_SSH_KEY`)
   - Value: Paste the secret value
   - Click "Add secret"

### Via GitHub CLI

```bash
# Install GitHub CLI (if not already)
brew install gh  # macOS
# or
sudo apt install gh  # Linux

# Authenticate
gh auth login

# Set secrets (replace values with actual secrets)
gh secret set DROPLET_SSH_KEY < ~/.ssh/finance_ppm_deploy
gh secret set ODOO_ADMIN_PASSWORD --body "your_admin_password"
gh secret set N8N_API_KEY --body "your_n8n_api_key"
gh secret set SUPABASE_SERVICE_ROLE_KEY --body "your_supabase_service_role_key"
gh secret set MATTERMOST_WEBHOOK_URL --body "https://mattermost.insightpulseai.net/hooks/xxx"
```

## Validation

### Test Secret Availability

After setting secrets, verify they are accessible to GitHub Actions:

```bash
# Check secrets are set (values will be masked)
gh secret list
```

Expected output:
```
DROPLET_SSH_KEY            Updated 2025-XX-XX
MATTERMOST_WEBHOOK_URL     Updated 2025-XX-XX
N8N_API_KEY                Updated 2025-XX-XX
ODOO_ADMIN_PASSWORD        Updated 2025-XX-XX
SUPABASE_SERVICE_ROLE_KEY  Updated 2025-XX-XX
```

### Test SSH Connection

```bash
# Test SSH connection using the deploy key
ssh -i ~/.ssh/finance_ppm_deploy root@159.223.75.148 "echo 'SSH connection successful'"
```

### Test Odoo Authentication

```bash
# Test XML-RPC authentication
python3 << EOF
import xmlrpc.client

odoo_url = "http://159.223.75.148:8071"
db = "odoo_accounting"
username = "admin"
password = "YOUR_ADMIN_PASSWORD"

common = xmlrpc.client.ServerProxy(f"{odoo_url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

if uid:
    print(f"✅ Authentication successful (UID: {uid})")
else:
    print("❌ Authentication failed")
EOF
```

### Test n8n API

```bash
# Test n8n API connectivity
curl -sf \
  -H "X-N8N-API-KEY: YOUR_N8N_API_KEY" \
  "https://ipa.insightpulseai.net/api/v1/workflows" | jq '.data | length'
```

### Test Supabase Service Role

```bash
# Test Supabase REST API
curl -sf \
  -H "apikey: YOUR_SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer YOUR_SUPABASE_SERVICE_ROLE_KEY" \
  "https://xkxyvboeubffxxbebsll.supabase.co/rest/v1/finance_ppm.monthly_reports?limit=1" | jq '.'
```

### Test Mattermost Webhook

```bash
# Test Mattermost notification
curl -sf -X POST \
  -H "Content-Type: application/json" \
  -d '{"text": "🧪 Test notification from GitHub secrets setup"}' \
  "YOUR_MATTERMOST_WEBHOOK_URL"
```

## Security Best Practices

1. **Rotate Secrets Regularly**: Change API keys and passwords every 90 days
2. **Limit Scope**: Use dedicated service accounts with minimum required permissions
3. **Audit Access**: Review secret access logs in GitHub Actions runs
4. **Never Log Secrets**: Secrets are automatically masked in GitHub Actions logs
5. **Revoke Unused Keys**: Remove old SSH keys and API keys when no longer needed

## Troubleshooting

### Secret Not Available in Workflow

**Symptom**: Workflow fails with `secret.XXX is not defined`

**Solution**:
1. Verify secret name matches exactly (case-sensitive)
2. Check secret is set at repository level, not organization
3. Ensure workflow has access to secrets (not from forked PR)

### SSH Authentication Failed

**Symptom**: `Permission denied (publickey)` error

**Solution**:
1. Verify public key is in `/root/.ssh/authorized_keys` on droplet
2. Check private key format (should include full PEM headers)
3. Test SSH connection manually before running workflow

### Odoo Authentication Failed

**Symptom**: `Authentication failed` in XML-RPC logs

**Solution**:
1. Verify admin password is correct
2. Check database name is `odoo_accounting`
3. Ensure Odoo is running on port 8071

### n8n API Connection Failed

**Symptom**: `401 Unauthorized` or `403 Forbidden`

**Solution**:
1. Regenerate n8n API key and update secret
2. Check API key has "Workflows: Read & Write" permissions
3. Verify n8n URL is correct: https://ipa.insightpulseai.net

### Supabase Schema Not Found

**Symptom**: `404 Not Found` when querying `finance_ppm.monthly_reports`

**Solution**:
1. Verify schema exists: `SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'finance_ppm';`
2. Check RLS policies are not blocking service role access
3. Ensure table exists: `SELECT table_name FROM information_schema.tables WHERE table_schema = 'finance_ppm';`

### Mattermost Webhook Failed

**Symptom**: `Invalid webhook URL` or `404 Not Found`

**Solution**:
1. Regenerate webhook in Mattermost
2. Ensure webhook URL includes full path: `/hooks/xxxxxxxxxxxxxx`
3. Test webhook manually with curl before setting secret

## Next Steps

After configuring all 5 secrets:

1. Trigger workflow manually: https://github.com/[YOUR_ORG]/odoo-ce/actions/workflows/deploy-finance-ppm.yml
2. Monitor deployment progress in GitHub Actions
3. Verify deployment with verification script on droplet:
   ```bash
   ssh root@159.223.75.148
   /root/odoo-ce/scripts/ci/verify-deployment.sh
   ```
