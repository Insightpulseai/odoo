# Odoo CE 18.0 SMTP Setup with Mailgun

**Purpose**: Configure Odoo to send transactional emails via Mailgun's SMTP service

**Prerequisites**:
- Mailgun domain `mg.insightpulseai.com` verified (all DNS records ✅)
- Mailgun SMTP credentials from dashboard
- Admin access to Odoo CE 18.0

---

## Mailgun SMTP Credentials (Canonical)

| Field | Value | Notes |
|-------|-------|-------|
| **SMTP Server** | `smtp.mailgun.org` | US region endpoint |
| **Port** | `587` | TLS (recommended) |
| **Port Alternative** | `465` | SSL (also supported) |
| **Username** | `postmaster@mg.insightpulseai.com` | Mailgun-generated default |
| **Password** | `{MAILGUN_SMTP_PASSWORD}` | From Mailgun dashboard "Domain Settings" → "SMTP Credentials" |
| **TLS** | ✅ Required | Must enable TLS/STARTTLS |

**Retrieve SMTP Password**:
1. Go to Mailgun dashboard: https://app.mailgun.com/mg/dashboard
2. Navigate to "Sending" → "Domains" → `mg.insightpulseai.com`
3. Click "Domain Settings" → "SMTP Credentials"
4. Copy password for `postmaster@mg.insightpulseai.com`

---

## Odoo SMTP Configuration (UI)

### Step 1: Navigate to Outgoing Mail Servers

**Path**: Settings → Technical → Email → Outgoing Mail Servers

**URL**: `https://erp.insightpulseai.com/web#menu_id=183&cids=1&action=182`

### Step 2: Create New SMTP Server

Click **"Create"** button and fill in the form:

| Field | Value | Required |
|-------|-------|----------|
| **Description** | `Mailgun Production (mg.insightpulseai.com)` | ✅ |
| **SMTP Server** | `smtp.mailgun.org` | ✅ |
| **SMTP Port** | `587` | ✅ |
| **Connection Security** | `TLS (STARTTLS)` | ✅ |
| **Username** | `postmaster@mg.insightpulseai.com` | ✅ |
| **Password** | `{MAILGUN_SMTP_PASSWORD}` | ✅ |
| **Priority** | `10` | ✅ (default) |

**Screenshot Reference**: See screenshot provided by user for exact UI layout

### Step 3: Save and Test Connection

1. Click **"Save"** button
2. Click **"Test Connection"** button
3. **Expected Result**: "Connection Test Succeeded! Everything seems properly set up!"
4. **If Failed**: See Troubleshooting section below

---

## Odoo System Parameters (Set "From" Domain)

### Step 1: Navigate to System Parameters

**Path**: Settings → Technical → Parameters → System Parameters

**URL**: `https://erp.insightpulseai.com/web#menu_id=183&cids=1&action=174`

### Step 2: Update/Create Parameter

**Search for existing**: `mail.catchall.domain`

**If exists**: Edit existing parameter
**If not exists**: Click "Create"

| Field | Value |
|-------|-------|
| **Key** | `mail.catchall.domain` |
| **Value** | `mg.insightpulseai.com` |

**Purpose**: Forces all outgoing emails to use `@mg.insightpulseai.com` as sender domain

### Step 3: Update Default From Email (Optional)

**Parameter**: `mail.default.from`
**Value**: `noreply@mg.insightpulseai.com`

**Purpose**: Default sender address when no specific user email is provided

---

## Verification Procedure

### Test 1: SMTP Connection Test (Built-in)

1. Go to **Settings → Technical → Email → Outgoing Mail Servers**
2. Open the Mailgun server record
3. Click **"Test Connection"**
4. **Expected**: "Connection Test Succeeded!"

### Test 2: Send Test Email from Odoo

1. Go to **Settings → Technical → Email → Emails**
2. Click **"Create"**
3. Fill in test email:
   - **To**: Your personal email (Gmail, Outlook, etc.)
   - **Subject**: `Odoo Mailgun Test - $(date +%Y-%m-%d)`
   - **Body**: `This is a test email from Odoo CE 18.0 via Mailgun SMTP.`
4. Click **"Send Now"**
5. Check recipient inbox within 1-2 minutes

**Expected**:
- Email delivers successfully
- Sender shows: `noreply@mg.insightpulseai.com` (or configured default)
- Email passes spam filters (check Gmail "View original" → SPF/DKIM PASS)

### Test 3: Trigger Transactional Email

**Example**: Create expense and submit for approval

1. Go to **Expenses → My Expenses → Create**
2. Fill in expense details
3. Click **"Submit to Manager"**
4. **Expected**: Manager receives email notification at their configured email

### Test 4: Check Mailgun Logs

1. Go to Mailgun dashboard: https://app.mailgun.com/mg/logs
2. **Expected**: See accepted + delivered events for test emails
3. Check "Delivered" status (green checkmark)
4. Review any failures or bounces

---

## Advanced Configuration

### Multiple SMTP Servers (Priority Fallback)

**Use Case**: Configure backup SMTP server for failover

1. Create second outgoing mail server (e.g., SendGrid, AWS SES)
2. Set **Priority** = `20` (higher number = lower priority)
3. Odoo will try primary (priority 10) first, fallback to secondary (priority 20) on failure

### Custom Sender Addresses per User

**Path**: Settings → Users & Companies → Users → [Select User] → Preferences

| Field | Value |
|-------|-------|
| **Email** | `firstname.lastname@mg.insightpulseai.com` |

**Effect**: Outgoing emails from that user will use their custom sender address

**Requirement**: Sender address must be within `mg.insightpulseai.com` domain

### Email Notification Preferences

**Path**: Settings → Users & Companies → Users → [Select User] → Preferences

| Field | Value | Effect |
|-------|-------|--------|
| **Notification** | `Handle by Emails` | Receive Odoo notifications via email |
| **Notification** | `Handle in Odoo` | In-app notifications only |

---

## Troubleshooting

### SMTP Connection Test Fails

**Symptom**: "Connection Test Failed" with error message

**Common Errors**:

1. **`Connection refused` or `Connection timeout`**
   - **Fix**: Check firewall rules (port 587 must be open outbound)
   - **Fix**: Verify SMTP server is `smtp.mailgun.org` (not `api.mailgun.net`)

2. **`Authentication failed`**
   - **Fix**: Verify SMTP username is `postmaster@mg.insightpulseai.com`
   - **Fix**: Re-copy SMTP password from Mailgun dashboard
   - **Fix**: Ensure no leading/trailing spaces in credentials

3. **`TLS/SSL error`**
   - **Fix**: Ensure "Connection Security" is set to `TLS (STARTTLS)`
   - **Fix**: Update Python `certifi` package: `pip install --upgrade certifi`

### Emails Not Sending

**Symptom**: Odoo queues emails but they never send

**Diagnosis**:
```bash
# Check Odoo mail queue
ssh root@178.128.112.214 "docker exec odoo-prod odoo shell -d odoo" <<'PYTHON'
# Count pending emails
env['mail.mail'].search_count([('state', '=', 'outgoing')])
# Should return 0 if queue is processing

# Check failed emails
env['mail.mail'].search([('state', '=', 'exception')]).mapped('failure_reason')
PYTHON
```

**Fixes**:
1. Restart Odoo: `docker restart odoo-prod`
2. Check cron jobs: **Settings → Technical → Automation → Scheduled Actions** → Search "Mail" → Ensure enabled
3. Force send queued emails:
   ```bash
   ssh root@178.128.112.214 "docker exec odoo-prod odoo shell -d odoo" <<'PYTHON'
   env['mail.mail'].search([('state', '=', 'outgoing')]).send()
   PYTHON
   ```

### Emails Go to Spam

**Symptom**: Emails deliver but land in spam folder

**Root Causes**:
1. SPF/DKIM not configured (verify DNS records)
2. Missing DMARC policy
3. Low sender reputation (new domain)
4. Generic content triggers spam filters

**Solutions**:
1. Verify DNS: `./scripts/mailgun/verify_domain.sh` → all ✅
2. Add DMARC record:
   ```
   _dmarc.mg.insightpulseai.com TXT "v=DMARC1; p=none; rua=mailto:dmarc@insightpulseai.com"
   ```
3. Test email authentication: https://www.mail-tester.com
4. Warm up sender reputation (send gradually, monitor engagement)

### Wrong Sender Domain

**Symptom**: Emails send from `@erp.insightpulseai.com` instead of `@mg.insightpulseai.com`

**Fix**: Set system parameter `mail.catchall.domain` = `mg.insightpulseai.com`

**Verification**:
1. Send test email
2. Check "From" header in recipient's "View original" option
3. Should show: `From: noreply@mg.insightpulseai.com`

---

## Production Checklist

Before marking SMTP setup as complete:

1. ✅ SMTP connection test passes
2. ✅ Test email delivers to external inbox (Gmail/Outlook)
3. ✅ Test email passes SPF/DKIM checks (mail-tester.com score ≥8/10)
4. ✅ System parameter `mail.catchall.domain` = `mg.insightpulseai.com`
5. ✅ Mailgun logs show "delivered" status
6. ✅ Transactional email triggers work (expense approval, etc.)
7. ✅ No emails stuck in Odoo outgoing queue
8. ✅ Cron jobs for mail processing are enabled

---

## Security Considerations

### API Key vs SMTP Password

| Method | Use Case | Security |
|--------|----------|----------|
| **SMTP Password** | Odoo transactional emails | ✅ Recommended (TLS encrypted) |
| **API Key** | n8n workflows, programmatic sending | ⚠️ More powerful (requires careful handling) |

**Rule**: Use SMTP for Odoo, reserve API for n8n/scripts

### Credentials Storage

**Odoo Database**: SMTP password stored encrypted in `ir_mail_server` table
**Environment Variables**: API keys stored in `~/.zshrc` only
**Never Commit**: No credentials in version control

---

**Last Updated**: 2026-01-14
**Applies To**: Production Odoo CE 18.0 (`erp.insightpulseai.com`)
**Mailgun Domain**: `mg.insightpulseai.com`
**SMTP Server**: `smtp.mailgun.org:587` (TLS)
