# Email & OAuth Configuration Guide

**Version**: 1.0
**Date**: 2025-01-05
**Stack**: Odoo 18 CE + Gmail SMTP + Google OAuth SSO

---

## Overview

This guide covers complete configuration of:
1. **Gmail SMTP** - Outgoing email using App Password
2. **Google OAuth SSO** - Sign in with Google functionality

---

## Prerequisites

### 1. Gmail Account Requirements

**For SMTP (Email Sending)**:
- Gmail account with 2FA enabled
- App Password generated (16 characters, no spaces)
- Generate at: https://myaccount.google.com/apppasswords

**Steps to Generate App Password**:
1. Go to Google Account settings
2. Security → 2-Step Verification (must be enabled)
3. Scroll to "App passwords"
4. Select app: "Mail"
5. Select device: "Other (Custom name)" → Enter "Odoo ERP"
6. Click "Generate"
7. Copy 16-character password (remove spaces)

### 2. Google Cloud Project Requirements

**For OAuth SSO (Sign in with Google)**:
- Google Cloud Project created
- OAuth 2.0 credentials configured
- Authorized redirect URI: `https://erp.insightpulseai.com/auth_oauth/signin`

**Current Configuration**:
```json
{
  "client_id": "1024356860971-k71aep6lperde4vaeiai4f41ehmsfqhl.apps.googleusercontent.com",
  "project_id": "cba-ai",
  "client_secret": "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",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

**Verify Configuration**:
1. Go to: https://console.cloud.google.com/apis/credentials
2. Select project: "cba-ai"
3. Edit OAuth 2.0 Client ID
4. Verify "Authorized redirect URIs" includes:
   - `https://erp.insightpulseai.com/auth_oauth/signin`
5. If not present, add it and wait 5-10 minutes for propagation

---

## Quick Deployment

### Option 1: Complete Automated Setup

Deploy all fixes (OwlError + OAuth + Email + SSO) in one command:

```bash
# SSH into production server
ssh root@159.223.75.148

# Navigate to repo
cd /root/odoo-ce

# Pull latest changes
git pull origin main

# Run complete deployment script
./scripts/deploy_complete_fix.sh your.email@gmail.com "your16charapppass"
```

**Expected Output**:
```
==================================================
DEPLOYMENT SUMMARY
==================================================

Configuration Applied:
  ✓ OwlError fixed: pay_invoices_online field removed
  ✓ OAuth loop fixed: HTTPS enforced in nginx + database
  ✓ Gmail SMTP: your.email@gmail.com configured
  ✓ Google OAuth SSO: Sign in with Google enabled

✅ DEPLOYMENT COMPLETED SUCCESSFULLY
```

### Option 2: Manual Step-by-Step Setup

If you prefer granular control or troubleshooting:

#### Step 1: Core Hotfix (OwlError + OAuth Loop)
```bash
./scripts/hotfix_production.sh prod
```

#### Step 2: Gmail SMTP Configuration
```bash
./scripts/configure_gmail_smtp.sh your.email@gmail.com "your16charapppass" prod
```

#### Step 3: Google OAuth SSO Configuration
```bash
./scripts/configure_google_oauth.sh prod
```

#### Step 4: Validate All Changes
```bash
./scripts/validate_production.sh prod
```

---

## Configuration Details

### Gmail SMTP Settings

**Database Table**: `ir.mail_server`

**Configuration**:
```python
{
    'name': 'Gmail SMTP',
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 465,
    'smtp_encryption': 'ssl',  # SSL is more reliable than STARTTLS for Gmail
    'smtp_user': 'your.email@gmail.com',
    'smtp_pass': 'your16charapppass',
    'sequence': 1,  # Highest priority
    'active': True
}
```

**System Parameters** (`ir.config_parameter`):
```python
{
    'mail.default.from': 'your.email@gmail.com',
    'mail.catchall.domain': 'gmail.com',
    'mail.catchall.alias': 'your.email@gmail.com'
}
```

**Why SSL (465) instead of STARTTLS (587)?**
- SSL (port 465) establishes encrypted connection from the start
- STARTTLS (port 587) starts unencrypted and upgrades to TLS
- Odoo 18 CE + Gmail works more reliably with SSL
- Fewer connection timeout issues in production

### Google OAuth SSO Settings

**Database Table**: `auth.oauth.provider`

**Configuration**:
```python
{
    'name': 'Google',
    'client_id': '1024356860971-k71aep6lperde4vaeiai4f41ehmsfqhl.apps.googleusercontent.com',
    'secret': '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',
    'auth_endpoint': 'https://accounts.google.com/o/oauth2/auth',
    'scope': 'openid email profile',
    'validation_endpoint': 'https://www.googleapis.com/oauth2/v3/userinfo',
    'enabled': True,
    'css_class': 'fa fa-google',
    'body': 'Sign in with Google'
}
```

**System Parameters** (`ir.config_parameter`):
```python
{
    'web.base.url': 'https://erp.insightpulseai.com',
    'web.base.url.freeze': 'True'
}
```

**OAuth Flow**:
1. User clicks "Sign in with Google" button
2. Browser redirects to: `https://accounts.google.com/o/oauth2/auth?...`
3. User selects Google account and grants permissions
4. Google redirects back to: `https://erp.insightpulseai.com/auth_oauth/signin?code=...`
5. Odoo exchanges code for access token
6. Odoo fetches user info from: `https://www.googleapis.com/oauth2/v3/userinfo`
7. User logged in or account created if first time

---

## Testing & Validation

### Test 1: Gmail SMTP Connection

**UI Method**:
1. Login to Odoo: `https://erp.insightpulseai.com`
2. Navigate to: Settings → Technical → Email → Outgoing Mail Servers
3. Click "Gmail SMTP" server record
4. Click "Test Connection" button
5. **Expected**: Popup shows "Connection Test Successful!"

**CLI Method**:
```bash
docker exec odoo-erp-prod python3 <<EOF
import odoo
from odoo import api, SUPERUSER_ID

config = odoo.tools.config
config['db_name'] = 'prod'
odoo.service.server.load_server_wide_modules()
registry = odoo.registry('prod')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    server = env['ir.mail_server'].search([('smtp_host', '=', 'smtp.gmail.com')], limit=1)

    if server:
        try:
            smtp = server.connect()
            smtp.quit()
            print("✓ SMTP connection successful")
        except Exception as e:
            print(f"❌ SMTP connection failed: {e}")
    else:
        print("❌ Gmail SMTP server not found")
EOF
```

### Test 2: Send Test Email

**UI Method**:
1. Settings → Technical → Email → Emails
2. Click "Create"
3. Fill in:
   - **Email To**: your.email@gmail.com
   - **Subject**: Test Email from Odoo
   - **Body**: This is a test email.
4. Click "Send Now"
5. **Expected**: Email appears in recipient inbox within 1-2 minutes

**CLI Method**:
```bash
docker exec odoo-erp-prod python3 <<EOF
import odoo
from odoo import api, SUPERUSER_ID

config = odoo.tools.config
config['db_name'] = 'prod'
odoo.service.server.load_server_wide_modules()
registry = odoo.registry('prod')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Send test email
    mail = env['mail.mail'].create({
        'email_to': 'your.email@gmail.com',
        'subject': 'Test Email from Odoo CLI',
        'body_html': '<p>This is a test email sent via CLI.</p>'
    })
    mail.send()

    print(f"✓ Test email queued (ID: {mail.id})")
    print(f"  State: {mail.state}")
    print(f"  To: {mail.email_to}")
EOF
```

### Test 3: Google OAuth SSO Login

**Browser Test**:
1. Open Chrome Incognito window
2. Navigate to: `https://erp.insightpulseai.com`
3. **Expected**: Login page shows "Sign in with Google" button
4. Click "Sign in with Google"
5. **Expected**: Redirect to Google account selection
6. Select your Google account
7. **Expected**: Redirect back to Odoo and logged in

**Common Issues**:

**Issue 1**: No "Sign in with Google" button
- **Cause**: Browser cache, auth_oauth module not installed
- **Fix**: Clear browser cache (Ctrl+Shift+R), verify module installation

**Issue 2**: `redirect_uri_mismatch` error
- **Cause**: Google Cloud Console redirect URI not configured
- **Fix**: Add `https://erp.insightpulseai.com/auth_oauth/signin` to Authorized redirect URIs

**Issue 3**: Infinite redirect loop (http:// ↔ https://)
- **Cause**: nginx X-Forwarded-Proto not set to `https`
- **Fix**: Run `./scripts/hotfix_production.sh` to fix nginx configuration

**Issue 4**: `invalid_client` error
- **Cause**: Client ID or Client Secret mismatch
- **Fix**: Verify credentials in database match Google Cloud Console

### Test 4: Verify Database Configuration

```bash
# Check Gmail SMTP server
docker exec odoo-erp-prod psql -U odoo -d prod -c "
  SELECT name, smtp_host, smtp_port, smtp_user, active
  FROM ir_mail_server
  WHERE active=true
  ORDER BY sequence;
"

# Expected output:
#     name     |   smtp_host    | smtp_port |      smtp_user       | active
# -------------+----------------+-----------+----------------------+--------
#  Gmail SMTP  | smtp.gmail.com |       465 | your.email@gmail.com | t

# Check Google OAuth provider
docker exec odoo-erp-prod psql -U odoo -d prod -c "
  SELECT name, client_id, enabled
  FROM auth_oauth_provider
  WHERE enabled=true;
"

# Expected output:
#   name  |                      client_id                      | enabled
# --------+-----------------------------------------------------+---------
#  Google | 1024356860971-k71aep6lperde4vaeiai4f41ehmsfqhl... | t
```

---

## Troubleshooting

### Gmail SMTP Issues

#### Problem: "Connection Test Failed" or timeout
**Diagnosis**:
```bash
docker logs odoo-erp-prod --tail 50 | grep -i smtp
```

**Common Causes**:
1. **App Password incorrect**
   - Verify 16 characters, no spaces
   - Regenerate if expired: https://myaccount.google.com/apppasswords

2. **2FA not enabled**
   - Enable at: https://myaccount.google.com/security

3. **"Less secure app" blocking**
   - This setting was deprecated by Google
   - Use App Passwords instead

4. **Firewall blocking port 465**
   - Test: `telnet smtp.gmail.com 465`
   - Expected: Connection established

5. **Gmail account suspended**
   - Check: https://myaccount.google.com/notifications

**Fix Commands**:
```bash
# Regenerate Gmail SMTP configuration
./scripts/configure_gmail_smtp.sh your.email@gmail.com "new16charapppass" prod

# Verify SMTP connection
docker exec odoo-erp-prod python3 -c "
import smtplib
smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
smtp.login('your.email@gmail.com', 'your16charapppass')
smtp.quit()
print('✓ Direct SMTP connection successful')
"
```

#### Problem: Emails stuck in "Outgoing" state
**Diagnosis**:
```bash
docker exec odoo-erp-prod psql -U odoo -d prod -c "
  SELECT id, subject, state, failure_reason
  FROM mail_mail
  WHERE state != 'sent'
  ORDER BY id DESC
  LIMIT 10;
"
```

**Common Causes**:
1. **Mail cron job not running**
   - Check: Settings → Technical → Automation → Scheduled Actions
   - Find "Mail: Email Queue Manager"
   - Verify "Active" is checked

2. **SMTP server disabled**
   - Check: Settings → Technical → Email → Outgoing Mail Servers
   - Verify "Gmail SMTP" is active

**Fix Commands**:
```bash
# Force send queued emails
docker exec odoo-erp-prod odoo shell -d prod -c "
env['mail.mail'].search([('state', '=', 'outgoing')]).send()
"

# Enable mail queue cron
docker exec odoo-erp-prod psql -U odoo -d prod -c "
  UPDATE ir_cron
  SET active = true
  WHERE model = 'mail.mail'
    AND function = '_process_email_queue';
"
```

### Google OAuth SSO Issues

#### Problem: `redirect_uri_mismatch`
**Error Message**:
```
Error 400: redirect_uri_mismatch
The redirect URI in the request, https://erp.insightpulseai.com/auth_oauth/signin,
does not match the ones authorized for the OAuth client.
```

**Fix**:
1. Go to: https://console.cloud.google.com/apis/credentials
2. Select project "cba-ai"
3. Edit OAuth 2.0 Client ID
4. Under "Authorized redirect URIs", add:
   ```
   https://erp.insightpulseai.com/auth_oauth/signin
   ```
5. Click "Save"
6. Wait 5-10 minutes for propagation
7. Retry login

#### Problem: Infinite OAuth redirect loop
**Symptoms**:
- Browser keeps redirecting between Odoo and Google
- URL alternates between http:// and https://

**Root Cause**: nginx not sending `X-Forwarded-Proto: https` header

**Fix**:
```bash
# Run core hotfix script (includes nginx fix)
./scripts/hotfix_production.sh prod

# Verify nginx header
docker exec nginx nginx -T | grep "X-Forwarded-Proto"
# Expected: proxy_set_header X-Forwarded-Proto https;
```

#### Problem: OAuth login creates new user instead of linking
**Symptoms**:
- Existing user with same email gets duplicated
- Two accounts with same email address

**Cause**: Odoo doesn't auto-link OAuth to existing email

**Fix** (manual):
```bash
# Link OAuth provider to existing user
docker exec odoo-erp-prod psql -U odoo -d prod -c "
  UPDATE res_users
  SET oauth_provider_id = (SELECT id FROM auth_oauth_provider WHERE name='Google'),
      oauth_uid = 'user_google_id'  -- Replace with actual Google ID
  WHERE login = 'user.email@gmail.com';
"
```

**Prevention**: Use OAuth for all logins, disable password login

---

## Security Best Practices

### 1. App Password Management
- ✅ **DO**: Store in environment variables or Odoo database (encrypted)
- ✅ **DO**: Rotate every 90 days
- ✅ **DO**: Revoke unused App Passwords
- ❌ **DON'T**: Hardcode in config files
- ❌ **DON'T**: Share App Passwords between services
- ❌ **DON'T**: Commit to git repositories

### 2. OAuth Client Secret Management
- ✅ **DO**: Store only in Odoo database (encrypted)
- ✅ **DO**: Restrict Google Cloud Console access
- ✅ **DO**: Monitor OAuth usage in Google Cloud Console
- ❌ **DON'T**: Expose in public repositories
- ❌ **DON'T**: Share between projects
- ❌ **DON'T**: Log in plaintext

### 3. Email Security
- ✅ **DO**: Use SPF, DKIM, DMARC for domain
- ✅ **DO**: Monitor email delivery rates
- ✅ **DO**: Implement rate limiting
- ❌ **DON'T**: Send from personal Gmail for production
- ❌ **DON'T**: Disable SSL/TLS
- ❌ **DON'T**: Ignore bounce notifications

### 4. OAuth Security
- ✅ **DO**: Use `state` parameter for CSRF protection
- ✅ **DO**: Validate redirect URIs strictly
- ✅ **DO**: Implement token refresh logic
- ❌ **DON'T**: Allow wildcard redirect URIs
- ❌ **DON'T**: Store access tokens in cookies
- ❌ **DON'T**: Disable HTTPS for OAuth endpoints

---

## Rollback Procedures

### Rollback Gmail SMTP Configuration
```bash
# Disable Gmail SMTP server
docker exec odoo-erp-prod psql -U odoo -d prod -c "
  UPDATE ir_mail_server
  SET active = false
  WHERE smtp_host = 'smtp.gmail.com';
"

# Restart Odoo
docker restart odoo-erp-prod
```

### Rollback Google OAuth SSO Configuration
```bash
# Disable Google OAuth provider
docker exec odoo-erp-prod psql -U odoo -d prod -c "
  UPDATE auth_oauth_provider
  SET enabled = false
  WHERE name = 'Google';
"

# Restart Odoo
docker restart odoo-erp-prod
```

### Complete Rollback (All Changes)
```bash
# Restore database from backup
docker exec -i postgres psql -U odoo -d postgres < /backups/prod_$(date +%Y%m%d).sql

# Restart Odoo
docker restart odoo-erp-prod
```

---

## Monitoring & Maintenance

### Email Monitoring
```bash
# Check email queue status
docker exec odoo-erp-prod psql -U odoo -d prod -c "
  SELECT state, COUNT(*)
  FROM mail_mail
  WHERE create_date > NOW() - INTERVAL '24 hours'
  GROUP BY state;
"

# Check SMTP errors
docker logs odoo-erp-prod --tail 100 | grep -i "smtp"
```

### OAuth Monitoring
```bash
# Check OAuth login activity
docker exec odoo-erp-prod psql -U odoo -d prod -c "
  SELECT DATE(create_date), COUNT(*)
  FROM res_users_log
  WHERE login_type = 'oauth'
  GROUP BY DATE(create_date)
  ORDER BY DATE(create_date) DESC
  LIMIT 7;
"

# Check failed OAuth attempts
docker logs odoo-erp-prod --tail 100 | grep -i "oauth"
```

---

## Related Documentation

- **Production Hotfix**: `docs/PRODUCTION_HOTFIX.md`
- **Success Criteria**: `docs/SUCCESS_CRITERIA.md`
- **Deployment Checklist**: `DEPLOYMENT_CHECKLIST.md`

---

**Last Updated**: 2025-01-05
**Maintained By**: DevOps Engineer (jgtolentino)
**Next Review**: After successful production deployment
