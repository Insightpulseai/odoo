# Email Setup with Zoho Mail (Canonical Guide)

**Canonical Email System for Odoo 19** | Updated: 2026-02-12

This guide documents the **settings-as-code** approach for configuring Zoho Mail SMTP with Odoo 19.

---

## Overview

**Zoho Mail SMTP** is the canonical email delivery system for InsightPulse AI's Odoo 19 deployment.

**Key Benefits**:
- ✅ Enterprise-grade email delivery with 99.9% uptime
- ✅ Professional sender reputation management
- ✅ Comprehensive email tracking and analytics
- ✅ App-specific password support for enhanced security
- ✅ Full SPF/DKIM/DMARC compliance
- ✅ Compatible with Microsoft 365/Outlook recipients (one-way notifications)

**External Mail Compatibility**:
- Microsoft 365 / Outlook supported as **recipient-only** mail systems
- Calendar invites (ICS), alerts, and notifications delivered via Zoho SMTP
- One-way notification only (no Microsoft Graph API, no Entra ID tenant integration)
- No callbacks or tenant-level access required

---

## Prerequisites

1. **Zoho Mail Account**: Active account for `insightpulseai.com` domain
2. **Domain Ownership**: Verified domain in Zoho Mail admin
3. **DNS Access**: Ability to add TXT records to `insightpulseai.com`
4. **Odoo 19**: Running instance with admin access
5. **Environment Variables**: Secure storage for credentials

---

## Part 1: Zoho Mail Configuration

### 1.1 Create App-Specific Password

**Why App Passwords?**
- More secure than account password
- Can be revoked independently
- Per-application access control
- Protects primary account if compromised

**Creation Steps** (Settings-as-Code):
```bash
# Generate app password via Zoho Mail API (or manually via portal)
# Store in secure vault/environment variable
export ZOHO_SMTP_APP_PASSWORD="your-16-character-app-password"
```

**Manual Creation** (if API unavailable):
1. Log into Zoho Mail: https://mail.zoho.com
2. Navigate: Settings → Security → App Passwords
3. Generate new password for "Odoo 19 Production"
4. Save password immediately (shown only once)

### 1.2 SMTP Server Details

```bash
# Zoho Mail SMTP Configuration
ZOHO_SMTP_SERVER="smtp.zoho.com"
ZOHO_SMTP_PORT="587"
ZOHO_SMTP_SECURITY="STARTTLS"
ZOHO_SMTP_USER="no-reply@insightpulseai.com"
ZOHO_SMTP_FROM="no-reply@insightpulseai.com"
```

**Port Options**:
- **587** (STARTTLS): Recommended for production
- **465** (SSL/TLS): Alternative if port 587 blocked
- **25** (Plain): Not recommended (no encryption)

---

## Part 2: DNS Configuration

### 2.1 SPF Record

**Purpose**: Authorize Zoho Mail to send email for `insightpulseai.com`

```bash
# Add TXT record to insightpulseai.com
# Host: @ (root domain)
# Type: TXT
# Value:
v=spf1 include:zohomail.com -all
```

**Verification**:
```bash
dig +short TXT insightpulseai.com | grep "v=spf1"
# Expected: "v=spf1 include:zohomail.com -all"
```

### 2.2 DKIM Record

**Purpose**: Cryptographic email authentication

**Retrieve DKIM from Zoho**:
1. Zoho Mail Admin → Domains → insightpulseai.com → DKIM
2. Copy DKIM selector and public key

```bash
# Add TXT record
# Host: [zoho-selector]._domainkey.insightpulseai.com
# Type: TXT
# Value: (Zoho-provided DKIM public key)
# Example:
# v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC...
```

**Verification**:
```bash
dig +short TXT [zoho-selector]._domainkey.insightpulseai.com
# Should return DKIM public key
```

### 2.3 DMARC Record

**Purpose**: Email authentication policy enforcement

```bash
# Add TXT record
# Host: _dmarc.insightpulseai.com
# Type: TXT
# Value:
v=DMARC1; p=quarantine; rua=mailto:postmaster@insightpulseai.com; ruf=mailto:postmaster@insightpulseai.com; fo=1
```

**Policy Progression**:
1. **Initial**: `p=none` (monitoring only)
2. **Testing**: `p=quarantine` (suspicious to spam)
3. **Production**: `p=reject` (strict enforcement)

**Verification**:
```bash
dig +short TXT _dmarc.insightpulseai.com
# Expected: "v=DMARC1; p=quarantine; ..."
```

### 2.4 DNS Verification Script

```bash
#!/bin/bash
# verify-email-dns.sh

echo "=== Email DNS Configuration Verification ==="

# SPF
echo -e "\n[SPF Record]"
spf=$(dig +short TXT insightpulseai.com | grep "v=spf1")
if [[ $spf == *"zohomail.com"* ]]; then
  echo "✅ SPF: $spf"
else
  echo "❌ SPF: Missing or incorrect"
fi

# DKIM (replace [selector] with actual Zoho selector)
echo -e "\n[DKIM Record]"
dkim=$(dig +short TXT [zoho-selector]._domainkey.insightpulseai.com)
if [[ $dkim == *"v=DKIM1"* ]]; then
  echo "✅ DKIM: Configured"
else
  echo "❌ DKIM: Missing or incorrect"
fi

# DMARC
echo -e "\n[DMARC Record]"
dmarc=$(dig +short TXT _dmarc.insightpulseai.com)
if [[ $dmarc == *"v=DMARC1"* ]]; then
  echo "✅ DMARC: $dmarc"
else
  echo "❌ DMARC: Missing or incorrect"
fi

echo -e "\n=== Verification Complete ==="
```

---

## Part 3: Odoo 19 Configuration (Settings-as-Code)

### 3.1 Environment Variables

**Production** (`.env.production`):
```bash
# Zoho Mail SMTP Configuration
ZOHO_SMTP_SERVER=smtp.zoho.com
ZOHO_SMTP_PORT=587
ZOHO_SMTP_USER=no-reply@insightpulseai.com
ZOHO_SMTP_APP_PASSWORD=your-16-character-app-password
ZOHO_SMTP_FROM=no-reply@insightpulseai.com
ZOHO_SMTP_SECURITY=starttls
```

**Development** (`.env.development`):
```bash
# Development SMTP (can use same Zoho account or test account)
ZOHO_SMTP_SERVER=smtp.zoho.com
ZOHO_SMTP_PORT=587
ZOHO_SMTP_USER=dev@insightpulseai.com
ZOHO_SMTP_APP_PASSWORD=dev-app-password
ZOHO_SMTP_FROM=dev@insightpulseai.com
ZOHO_SMTP_SECURITY=starttls
```

**Security Rules**:
- ✅ Never commit `.env*` files to git (already in `.gitignore`)
- ✅ Use app passwords, not account password
- ✅ Rotate passwords quarterly
- ✅ Use different credentials for dev/staging/prod

### 3.2 Odoo Configuration File

**File**: `odoo19/odoo.conf`

```ini
[options]
# Email Configuration (Zoho Mail)
smtp_server = ${ZOHO_SMTP_SERVER}
smtp_port = ${ZOHO_SMTP_PORT}
smtp_ssl = False
smtp_ssl_certificate_filename = False
smtp_ssl_private_key_filename = False
smtp_user = ${ZOHO_SMTP_USER}
smtp_password = ${ZOHO_SMTP_APP_PASSWORD}
email_from = ${ZOHO_SMTP_FROM}

# Email Settings
email_from_formatted = InsightPulse AI <no-reply@insightpulseai.com>
mail_catchall_alias = postmaster@insightpulseai.com
```

**Variable Interpolation**:
- Odoo supports environment variable substitution with `${VAR_NAME}` syntax
- Alternatively, use Python config or shell script to generate config

### 3.3 Deployment Script

**File**: `scripts/deploy/configure-email.sh`

```bash
#!/bin/bash
set -euo pipefail

ODOO_CONF="/path/to/odoo19/odoo.conf"
ENV_FILE="${1:-.env.production}"

# Load environment variables
if [[ -f "$ENV_FILE" ]]; then
  export $(grep -v '^#' "$ENV_FILE" | xargs)
else
  echo "❌ Environment file not found: $ENV_FILE"
  exit 1
fi

# Update Odoo configuration
cat > "$ODOO_CONF" <<EOF
[options]
# Email Configuration (Zoho Mail)
smtp_server = $ZOHO_SMTP_SERVER
smtp_port = $ZOHO_SMTP_PORT
smtp_ssl = False
smtp_user = $ZOHO_SMTP_USER
smtp_password = $ZOHO_SMTP_APP_PASSWORD
email_from = $ZOHO_SMTP_FROM
email_from_formatted = InsightPulse AI <$ZOHO_SMTP_FROM>

# (other Odoo options...)
EOF

echo "✅ Email configuration updated: $ODOO_CONF"
echo "🔄 Restart Odoo to apply changes"
```

**Usage**:
```bash
# Production
bash scripts/deploy/configure-email.sh .env.production

# Development
bash scripts/deploy/configure-email.sh .env.development
```

---

## Part 4: Verification & Testing

### 4.1 SMTP Connection Test

**File**: `scripts/verify/test-smtp.py`

```python
#!/usr/bin/env python3
"""Test Zoho Mail SMTP connection"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load from environment
SMTP_SERVER = os.getenv("ZOHO_SMTP_SERVER", "smtp.zoho.com")
SMTP_PORT = int(os.getenv("ZOHO_SMTP_PORT", "587"))
SMTP_USER = os.getenv("ZOHO_SMTP_USER")
SMTP_PASSWORD = os.getenv("ZOHO_SMTP_APP_PASSWORD")
SMTP_FROM = os.getenv("ZOHO_SMTP_FROM")

def test_smtp_connection():
    """Test SMTP connection and send test email"""
    try:
        print(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")

        # Create SMTP connection
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1)  # Enable debug output
        server.ehlo()
        server.starttls()
        server.ehlo()

        print(f"Authenticating as {SMTP_USER}...")
        server.login(SMTP_USER, SMTP_PASSWORD)

        print("✅ SMTP connection successful!")

        # Send test email
        msg = MIMEMultipart()
        msg['From'] = SMTP_FROM
        msg['To'] = SMTP_USER  # Send to self
        msg['Subject'] = "Zoho Mail SMTP Test - Odoo 19"

        body = """
        This is a test email from Odoo 19 using Zoho Mail SMTP.

        If you receive this, email configuration is working correctly.

        Configuration:
        - SMTP Server: {server}
        - SMTP Port: {port}
        - From: {from_addr}

        Timestamp: {timestamp}
        """.format(
            server=SMTP_SERVER,
            port=SMTP_PORT,
            from_addr=SMTP_FROM,
            timestamp=datetime.now().isoformat()
        )

        msg.attach(MIMEText(body, 'plain'))

        server.send_message(msg)
        print(f"✅ Test email sent to {SMTP_USER}")

        server.quit()
        return True

    except Exception as e:
        print(f"❌ SMTP test failed: {e}")
        return False

if __name__ == "__main__":
    from datetime import datetime

    # Check required environment variables
    required_vars = ["ZOHO_SMTP_USER", "ZOHO_SMTP_APP_PASSWORD", "ZOHO_SMTP_FROM"]
    missing = [v for v in required_vars if not os.getenv(v)]

    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        exit(1)

    success = test_smtp_connection()
    exit(0 if success else 1)
```

**Usage**:
```bash
# Load environment and test
source .env.production
python3 scripts/verify/test-smtp.py
```

### 4.2 Odoo Email Test

**Via Odoo Shell**:
```bash
# Start Odoo shell
cd odoo19
./odoo-bin shell -c odoo.conf

# In Python shell:
>>> from odoo import api, SUPERUSER_ID
>>> env = api.Environment(cr, SUPERUSER_ID, {})
>>>
>>> # Send test email
>>> mail_server = env['ir.mail_server'].sudo().search([], limit=1)
>>> mail_server.test_smtp_connection()
>>>
>>> # Create and send email
>>> mail = env['mail.mail'].sudo().create({
...     'email_from': 'no-reply@insightpulseai.com',
...     'email_to': 'admin@insightpulseai.com',
...     'subject': 'Odoo 19 Email Test',
...     'body_html': '<p>Test email from Odoo 19 via Zoho Mail SMTP</p>',
... })
>>> mail.send()
>>>
>>> print("✅ Email sent successfully" if mail.state == 'sent' else f"❌ Email failed: {mail.failure_reason}")
```

### 4.3 Automated Verification

**File**: `scripts/verify/verify-email-config.sh`

```bash
#!/bin/bash
set -euo pipefail

echo "=== Odoo 19 Email Configuration Verification ==="

# 1. DNS checks
echo -e "\n[1/5] DNS Configuration..."
bash scripts/verify/verify-email-dns.sh

# 2. Environment variables
echo -e "\n[2/5] Environment Variables..."
required_vars=("ZOHO_SMTP_SERVER" "ZOHO_SMTP_PORT" "ZOHO_SMTP_USER" "ZOHO_SMTP_APP_PASSWORD" "ZOHO_SMTP_FROM")
for var in "${required_vars[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo "❌ $var: Not set"
  else
    echo "✅ $var: Set"
  fi
done

# 3. Odoo config
echo -e "\n[3/5] Odoo Configuration..."
if grep -q "smtp_server = smtp.zoho.com" odoo19/odoo.conf; then
  echo "✅ Odoo config: Zoho SMTP configured"
else
  echo "❌ Odoo config: Missing or incorrect"
fi

# 4. SMTP connection
echo -e "\n[4/5] SMTP Connection..."
python3 scripts/verify/test-smtp.py

# 5. Odoo email test (requires running instance)
echo -e "\n[5/5] Odoo Email Test..."
echo "ℹ️  Manual verification required: Send test email via Odoo UI"

echo -e "\n=== Verification Complete ==="
```

---

## Part 5: Troubleshooting

### Common Issues

#### Issue: "Authentication Failed" Error

**Symptoms**:
```
smtplib.SMTPAuthenticationError: (535, b'Authentication Failed')
```

**Solutions**:
1. Verify app password (not account password)
2. Check username is full email address (`no-reply@insightpulseai.com`)
3. Ensure Zoho account is active and not locked
4. Check 2FA settings in Zoho

**Verification**:
```bash
# Test credentials manually
curl -v --url 'smtp://smtp.zoho.com:587' \
  --mail-from 'no-reply@insightpulseai.com' \
  --mail-rcpt 'admin@insightpulseai.com' \
  --user 'no-reply@insightpulseai.com:app-password' \
  --upload-file - <<EOF
From: no-reply@insightpulseai.com
To: admin@insightpulseai.com
Subject: SMTP Test

Test message
EOF
```

#### Issue: Emails Going to Spam

**Symptoms**:
- Emails delivered but marked as spam
- Low sender reputation score

**Solutions**:
1. Verify SPF record includes Zoho
2. Ensure DKIM is properly configured
3. Set DMARC policy to `p=quarantine` or `p=reject`
4. Check sender reputation: https://www.mail-tester.com
5. Warm up sending (gradual volume increase)

**Verification**:
```bash
# Check SPF alignment
dig +short TXT insightpulseai.com | grep zohomail

# Check DKIM signature in sent email headers
# Look for "DKIM-Signature:" header in email source
```

#### Issue: Connection Timeout

**Symptoms**:
```
TimeoutError: [Errno 60] Operation timed out
```

**Solutions**:
1. Check firewall allows outbound port 587
2. Verify network connectivity to `smtp.zoho.com`
3. Try alternative port (465 for SSL/TLS)
4. Check if ISP blocks SMTP ports

**Verification**:
```bash
# Test network connectivity
nc -zv smtp.zoho.com 587

# Test with telnet
telnet smtp.zoho.com 587

# Expected: "220 smtp.zoho.com ESMTP ready"
```

#### Issue: "Relay Access Denied"

**Symptoms**:
```
smtplib.SMTPRecipientsRefused: Relay access denied
```

**Solutions**:
1. Verify sender domain matches Zoho account domain
2. Check `email_from` uses authorized domain
3. Ensure authentication is enabled (not anonymous relay)

#### Issue: Large Attachments Fail

**Symptoms**:
- Emails with attachments > 10MB fail to send

**Solutions**:
1. Zoho limit: 25MB per email (including headers/encoding)
2. Odoo effective limit: ~20MB (after base64 encoding)
3. Use link-based sharing for large files
4. Configure Odoo attachment storage (S3, etc.)

**Configuration**:
```ini
# In odoo.conf
limit_memory_hard = 2684354560  # 2.5GB
limit_memory_soft = 2147483648  # 2GB
limit_request = 8192            # Request size limit
```

---

## Part 6: Monitoring & Maintenance

### Email Delivery Monitoring

**Script**: `scripts/monitor/email-health.sh`

```bash
#!/bin/bash

# Check Odoo mail queue
echo "=== Mail Queue Status ==="
psql -d odoo -c "
SELECT
  state,
  COUNT(*) as count,
  MAX(create_date) as latest
FROM mail_mail
WHERE create_date > NOW() - INTERVAL '24 hours'
GROUP BY state;
"

# Check for failed emails
echo -e "\n=== Recent Failures ==="
psql -d odoo -c "
SELECT
  email_to,
  subject,
  failure_reason,
  create_date
FROM mail_mail
WHERE state = 'exception'
  AND create_date > NOW() - INTERVAL '7 days'
ORDER BY create_date DESC
LIMIT 10;
"
```

### Sender Reputation Check

**Monthly Tasks**:
```bash
# 1. Check SPF/DKIM/DMARC compliance
bash scripts/verify/verify-email-dns.sh

# 2. Review Zoho delivery reports
# Login to Zoho Mail → Reports → Email Delivery

# 3. Check blacklist status
curl -s "https://mxtoolbox.com/api/v1/Blacklist/insightpulseai.com"

# 4. Rotate app passwords (quarterly)
# Generate new app password in Zoho
# Update .env.production
# Restart Odoo
```

### Performance Optimization

**Odoo Mail Settings**:
```python
# Configure mail batch processing
# Settings → Technical → System Parameters

# ir.cron.mail_gateway
# Frequency: Every 5 minutes (default: 1 minute for high volume)

# mail.bounce.alias
# Set bounce handling email
```

**Database Cleanup**:
```sql
-- Archive old sent emails (keep 90 days)
DELETE FROM mail_mail
WHERE state = 'sent'
  AND create_date < NOW() - INTERVAL '90 days';

-- Vacuum table
VACUUM ANALYZE mail_mail;
```

---

## Part 7: Security Best Practices

### Password Management

1. **App Passwords Only**: Never use account password for SMTP
2. **Rotation Policy**: Quarterly password rotation
3. **Secure Storage**: Use environment variables, never hardcode
4. **Least Privilege**: Separate credentials for dev/staging/prod

### Monitoring & Alerts

**Email Security Alerts**:
```bash
# Monitor for authentication failures
tail -f /var/log/odoo/odoo-server.log | grep -i "smtp.*authentication"

# Alert on DMARC policy violations
# Review Zoho DMARC reports weekly
```

### Compliance

**GDPR Considerations**:
- Email logs contain personal data
- Implement retention policy (90-day default)
- Provide data export mechanisms
- Honor unsubscribe requests

**CAN-SPAM Compliance**:
- Include physical address in emails
- Clear unsubscribe mechanism
- Process unsubscribe within 10 business days
- Honor opt-out preferences

---

## Part 8: Migration from Mailgun (Deprecated)

**Historical Context**: Mailgun was deprecated in February 2026 in favor of Zoho Mail.

**Migration Checklist**:
- ✅ DNS records updated (SPF/DKIM/DMARC)
- ✅ Odoo configuration migrated
- ✅ Environment variables updated
- ✅ SMTP credentials rotated
- ✅ Verification tests passed
- ✅ Legacy Mailgun docs moved to `docs/deprecated/mailgun/`

**Rollback Plan** (if needed):
- Mailgun credentials preserved in secure vault (not in repo)
- Legacy configuration documented in `docs/deprecated/mailgun/`
- Rollback requires manual DNS changes (SPF/DKIM)

---

## Summary

**Email Delivery Path**:
```
Odoo 19 → Zoho SMTP (port 587/STARTTLS) → Recipient Inbox
```

**Key Configuration Files**:
- `odoo19/odoo.conf` - Odoo SMTP settings
- `.env.production` - Environment variables (not in git)
- `scripts/deploy/configure-email.sh` - Deployment automation
- `scripts/verify/test-smtp.py` - Connection testing

**Verification Commands**:
```bash
# Full verification suite
bash scripts/verify/verify-email-config.sh

# Individual checks
bash scripts/verify/verify-email-dns.sh
python3 scripts/verify/test-smtp.py
```

**Documentation**:
- This guide: Canonical email setup reference
- Deprecated: `docs/deprecated/mailgun/` (historical reference only)

**Support**:
- Zoho Mail Support: https://www.zoho.com/mail/help/
- SMTP Documentation: https://www.zoho.com/mail/help/smtp.html
- Odoo Email Documentation: https://www.odoo.com/documentation/19.0/administration/maintain/emails.html

---

**Last Updated**: 2026-02-12
**Odoo Version**: 19.0
**Canonical Source**: `docs/guides/email/EMAIL_SETUP_ZOHO.md`
