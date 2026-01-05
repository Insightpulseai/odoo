# Credentials Summary - Secure Reference

**⚠️ CONFIDENTIAL - DO NOT COMMIT TO GIT**

This document summarizes all credentials for Odoo production deployment.

---

## 🔐 Gmail SMTP Credentials

**Account**: jgtolentino@gmail.com
**App Password**: `wcxu fssn evbs mzcy` (spaces optional)
**Clean Format**: `wcxufssnevbsmzcy` (16 chars)

**Storage Location**: `.env.smtp` (git-ignored ✓)

**Usage**:
```bash
GMAIL_USER=jgtolentino@gmail.com
GMAIL_APP_PASSWORD=wcxufssnevbsmzcy
```

**SMTP Configuration**:
- Host: `smtp.gmail.com`
- Port: `465` (SSL)
- Encryption: `ssl` (not starttls)

**Generate New App Password**:
1. Visit: https://myaccount.google.com/apppasswords
2. Create: "Odoo ERP Production"
3. Copy 16-character password
4. Update `.env.smtp` file
5. Redeploy: `./scripts/deploy_with_credentials.sh`

---

## 🔑 Google OAuth SSO Credentials

**✅ Verified in Google Cloud Console** (Jan 5, 2026)

**Project**: cba-ai
**Client Name**: "Odoo Gmail"
**Client Type**: Web application

**Client ID**:
```
1024356860971-k71aep6lperde4vaeiai4f41ehmsfqhl.apps.googleusercontent.com
```

**Client Secret**:
```
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
```

**Authorized Redirect URI** (CRITICAL):
```
https://erp.insightpulseai.net/auth_oauth/signin
```

**OAuth Endpoints**:
- Auth: `https://accounts.google.com/o/oauth2/auth`
- Token: `https://oauth2.googleapis.com/token`
- UserInfo: `https://www.googleapis.com/oauth2/v3/userinfo`

**Scope**:
```
openid email profile
```

**Storage**: Hardcoded in `scripts/configure_google_oauth.sh`

---

## 🌐 Odoo Production URLs

**Base URL**: https://erp.insightpulseai.net
**OAuth Callback**: https://erp.insightpulseai.net/auth_oauth/signin
**Database**: `prod`

**Server**: 159.223.75.148 (odoo-erp-prod Droplet)
**Region**: Singapore (SGP1)

---

## 📂 Credential Storage Locations

### Local Development (Git Repository)
- ✅ `.env.smtp` - Gmail credentials (GIT-IGNORED)
- ✅ `.env.smtp.example` - Template (safe to commit)
- ⚠️ `scripts/configure_google_oauth.sh` - OAuth client ID/secret (hardcoded, okay for private repo)

### Production Server (159.223.75.148)
- `/root/odoo-ce/.env.smtp` - Will be created during deployment
- Odoo database `prod` table `ir.mail_server` - Gmail SMTP settings (encrypted)
- Odoo database `prod` table `auth_oauth_provider` - OAuth settings (encrypted)
- Odoo database `prod` table `ir.config_parameter` - System parameters

---

## 🔒 Security Checklist

- ✅ **Gmail App Password**: Stored in `.env.smtp` (git-ignored)
- ✅ **`.gitignore`**: Updated to exclude `*.env` and `.env.smtp`
- ✅ **Google OAuth**: Redirect URI verified in console
- ✅ **HTTPS Enforced**: nginx `X-Forwarded-Proto = https`
- ✅ **Database Encryption**: Odoo encrypts credentials in PostgreSQL
- ⚠️ **Repository Private**: Ensure GitHub repo is private (contains OAuth secret)

---

## 🚨 Emergency Credential Rotation

### If Gmail App Password Compromised

1. **Revoke old password**:
   - Visit: https://myaccount.google.com/apppasswords
   - Delete "Odoo ERP Production" password

2. **Generate new password**:
   - Create new app password (16 chars)
   - Update `.env.smtp` locally and on server

3. **Redeploy**:
   ```bash
   ssh root@159.223.75.148
   cd /root/odoo-ce
   nano .env.smtp  # Update password
   ./scripts/deploy_with_credentials.sh
   ```

### If Google OAuth Credentials Compromised

1. **Regenerate in Google Cloud Console**:
   - Visit: https://console.cloud.google.com/apis/credentials
   - Delete old "Odoo Gmail" client
   - Create new OAuth 2.0 Client ID
   - Copy new Client ID and Secret

2. **Update deployment script**:
   - Edit `scripts/configure_google_oauth.sh`
   - Replace `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`

3. **Redeploy**:
   ```bash
   ./scripts/deploy_with_credentials.sh
   ```

---

## 📋 Deployment Command Reference

### Standard Deployment (Recommended)
```bash
ssh root@159.223.75.148
cd /root/odoo-ce && git pull origin main
./scripts/deploy_with_credentials.sh
```

### Manual Deployment (Troubleshooting)
```bash
# 1. Core fixes only
./scripts/hotfix_production.sh prod

# 2. Gmail SMTP only
./scripts/configure_gmail_smtp.sh jgtolentino@gmail.com wcxufssnevbsmzcy prod

# 3. OAuth SSO only
./scripts/configure_google_oauth.sh prod

# 4. Validate all
./scripts/validate_production.sh prod
```

### Credential-Free Deployment (Core Fixes Only)
```bash
# If you only need OwlError + OAuth loop fixes (no email/SSO)
./scripts/hotfix_production.sh prod
```

---

## 🔍 Credential Verification Commands

### Check Gmail SMTP in Database
```bash
docker exec odoo-erp-prod psql -U odoo -d prod -c "
  SELECT name, smtp_host, smtp_port, smtp_user, active
  FROM ir_mail_server
  WHERE smtp_host = 'smtp.gmail.com';
"
```

**Expected Output**:
```
    name     |   smtp_host    | smtp_port |      smtp_user       | active
-------------+----------------+-----------+----------------------+--------
 Gmail SMTP  | smtp.gmail.com |       465 | jgtolentino@gmail.com | t
```

### Check OAuth Provider in Database
```bash
docker exec odoo-erp-prod psql -U odoo -d prod -c "
  SELECT name, client_id, enabled
  FROM auth_oauth_provider
  WHERE name = 'Google';
"
```

**Expected Output**:
```
  name  |                      client_id                      | enabled
--------+-----------------------------------------------------+---------
 Google | 1024356860971-k71aep6lperde4vaeiai4f41ehmsfqhl... | t
```

### Test Gmail SMTP Connection
```bash
docker exec odoo-erp-prod python3 <<EOF
import smtplib
try:
    smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp.login('jgtolentino@gmail.com', 'wcxufssnevbsmzcy')
    smtp.quit()
    print('✓ Gmail SMTP connection successful')
except Exception as e:
    print(f'❌ Gmail SMTP connection failed: {e}')
EOF
```

---

## 📚 Related Documentation

- **Deployment Guide**: `DEPLOY_NOW.md`
- **Email & OAuth Setup**: `docs/EMAIL_AND_OAUTH_SETUP.md`
- **Success Criteria**: `docs/SUCCESS_CRITERIA.md`
- **Production Hotfix**: `docs/PRODUCTION_HOTFIX.md`

---

**Last Updated**: 2025-01-05
**Credentials Verified**: ✅ Jan 5, 2026
**Next Review**: After deployment or if credentials expire

---

## ⚠️ IMPORTANT SECURITY NOTES

1. **Never commit `.env.smtp`** to git (already in `.gitignore`)
2. **Keep this document offline** or in encrypted password manager
3. **Rotate credentials every 90 days** for security best practices
4. **Monitor Google account activity**: https://myaccount.google.com/notifications
5. **Keep GitHub repository private** (contains OAuth client secret)

---

**Document Classification**: CONFIDENTIAL
**Access Level**: DevOps Engineers only
**Distribution**: Do not share or commit to version control
