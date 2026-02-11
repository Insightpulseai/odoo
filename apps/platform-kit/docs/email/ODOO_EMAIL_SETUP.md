# Odoo 19.0 Email Configuration with Mailgun

Complete email setup for `insightpulseai.com` using Mailgun for transactional email and Zoho for inbox receiving.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Email Flow Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  OUTBOUND (Odoo → Mailgun → Recipients)                         │
│  ─────────────────────────────────────                          │
│  Odoo ERP                                                        │
│    ↓ SMTP (smtp.mailgun.org:587)                                │
│  Mailgun (mg.insightpulseai.com)                                │
│    ↓ Delivers via Mailgun infrastructure                        │
│  Recipients                                                      │
│                                                                  │
│  INBOUND (Senders → Zoho → Users)                               │
│  ─────────────────────────────────                              │
│  External Senders                                                │
│    ↓ MX records (mx.zoho.com)                                   │
│  Zoho Mail (insightpulseai.com)                                 │
│    ↓ IMAP/POP                                                   │
│  User Inboxes                                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Domain Configuration

| Purpose | Domain | Provider |
|---------|--------|----------|
| **Primary Domain** | `insightpulseai.com` | Canonical |
| **Mailgun Sending** | `mg.insightpulseai.com` | Mailgun subdomain |
| **Inbox Receiving** | `insightpulseai.com` | Zoho Mail |
| **Odoo ERP** | `erp.insightpulseai.com` | DigitalOcean |

## DNS Records

### For Root Domain (`insightpulseai.com`)

#### MX Records (Zoho - Receiving)
```
Type  Host  Priority  Value
MX    @     10        mx.zoho.com
MX    @     20        mx2.zoho.com
MX    @     50        mx3.zoho.com
```

#### SPF Record (Combined)
```
Type  Host  Value
TXT   @     v=spf1 include:zohomail.com include:mailgun.org ~all
```

#### DMARC Record
```
Type  Host     Value
TXT   _dmarc   v=DMARC1; p=quarantine; rua=mailto:dmarc@insightpulseai.com; pct=100
```

### For Mailgun Subdomain (`mg.insightpulseai.com`)

#### SPF Record
```
Type  Host  Value
TXT   mg    v=spf1 include:mailgun.org ~all
```

#### DKIM Records (from Mailgun Dashboard)
```
Type  Host                              Value
TXT   smtp._domainkey.mg                k=rsa; p=<YOUR_DKIM_PUBLIC_KEY>
TXT   krs._domainkey.mg                 k=rsa; p=<YOUR_DKIM_PUBLIC_KEY_2>
```

#### CNAME for Tracking (Optional)
```
Type   Host              Value
CNAME  email.mg          mailgun.org
```

#### MX Records for Mailgun (if receiving webhooks)
```
Type  Host  Priority  Value
MX    mg    10        mxa.mailgun.org
MX    mg    10        mxb.mailgun.org
```

## Mailgun Configuration

### 1. Add Domain in Mailgun

1. Go to [Mailgun Dashboard](https://app.mailgun.com/mg/sending/domains)
2. Click "Add New Domain"
3. Enter: `mg.insightpulseai.com`
4. Select region: US or EU
5. Copy DNS records and add to your DNS provider

### 2. Get SMTP Credentials

From Mailgun Dashboard → Domain Settings → SMTP Credentials:

| Setting | Value |
|---------|-------|
| **SMTP Server** | `smtp.mailgun.org` |
| **Port** | `587` (TLS) or `465` (SSL) |
| **Username** | `postmaster@mg.insightpulseai.com` |
| **Password** | Generated in Mailgun Dashboard |

### 3. Configure Webhooks (Optional)

Set up webhooks for email tracking:

| Event | Webhook URL |
|-------|-------------|
| Delivered | `https://erp.insightpulseai.com/mailgun/webhook/delivered` |
| Opened | `https://erp.insightpulseai.com/mailgun/webhook/opened` |
| Clicked | `https://erp.insightpulseai.com/mailgun/webhook/clicked` |
| Bounced | `https://erp.insightpulseai.com/mailgun/webhook/bounced` |
| Complained | `https://erp.insightpulseai.com/mailgun/webhook/complained` |

## Odoo Configuration

### 1. Enable Custom Email Servers

Navigate to: **Settings → General Settings → Discuss**

Enable: "Use Custom Email Servers"

### 2. Configure Outgoing Mail Server

Navigate to: **Settings → Technical → Outgoing Mail Servers**

Create new record:

| Field | Value |
|-------|-------|
| **Description** | Mailgun - insightpulseai.com |
| **SMTP Server** | `smtp.mailgun.org` |
| **SMTP Port** | `587` |
| **Connection Security** | TLS (STARTTLS) |
| **Username** | `postmaster@mg.insightpulseai.com` |
| **Password** | `<MAILGUN_SMTP_PASSWORD>` |
| **Priority** | `1` |
| **FROM Filtering** | `insightpulseai.com` |

Click "Test Connection" to verify.

### 3. Configure System Parameters

Navigate to: **Settings → Technical → System Parameters**

| Key | Value |
|-----|-------|
| `mail.catchall.domain` | `insightpulseai.com` |
| `mail.catchall.alias` | `catchall` |
| `mail.default.from` | `notifications` |
| `mail.bounce.alias` | `bounce` |
| `web.base.url` | `https://erp.insightpulseai.com` |

### 4. Configure Email Aliases

Navigate to: **Settings → Technical → Email → Aliases**

| Alias | Model | Default Values |
|-------|-------|----------------|
| `sales` | crm.lead | Team: Sales |
| `support` | helpdesk.ticket | Team: Support |
| `jobs` | hr.applicant | Department: HR |
| `invoices` | account.move | Journal: Vendor Bills |

## Environment Variables

Add to your `.env` or environment:

```bash
# Mailgun Configuration
MAILGUN_DOMAIN=mg.insightpulseai.com
MAILGUN_API_KEY=key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MAILGUN_SMTP_LOGIN=postmaster@mg.insightpulseai.com
MAILGUN_SMTP_PASSWORD=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MAILGUN_WEBHOOK_SIGNING_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Odoo Email Settings
ODOO_EMAIL_FROM=notifications@insightpulseai.com
ODOO_CATCHALL_DOMAIN=insightpulseai.com
ODOO_SMTP_HOST=smtp.mailgun.org
ODOO_SMTP_PORT=587
ODOO_SMTP_USER=postmaster@mg.insightpulseai.com
ODOO_SMTP_PASSWORD=${MAILGUN_SMTP_PASSWORD}
ODOO_SMTP_ENCRYPTION=starttls
```

## Odoo Configuration File (odoo.conf)

```ini
[options]
; Email Configuration
smtp_server = smtp.mailgun.org
smtp_port = 587
smtp_ssl = False
smtp_user = postmaster@mg.insightpulseai.com
smtp_password = ${MAILGUN_SMTP_PASSWORD}
email_from = notifications@insightpulseai.com
```

## Verification Steps

### 1. Verify DNS Records

```bash
# Check MX records (Zoho)
dig MX insightpulseai.com +short

# Check SPF record
dig TXT insightpulseai.com +short | grep spf

# Check DMARC record
dig TXT _dmarc.insightpulseai.com +short

# Check Mailgun subdomain SPF
dig TXT mg.insightpulseai.com +short

# Check DKIM
dig TXT smtp._domainkey.mg.insightpulseai.com +short
```

### 2. Test Mailgun API

```bash
curl -s --user "api:${MAILGUN_API_KEY}" \
  https://api.mailgun.net/v3/mg.insightpulseai.com/messages \
  -F from="Test <test@mg.insightpulseai.com>" \
  -F to="your-email@example.com" \
  -F subject="Mailgun Test" \
  -F text="Testing Mailgun configuration"
```

### 3. Test Odoo Email

```python
# In Odoo shell (odoo shell -d <database>)
from odoo import api, SUPERUSER_ID

env = api.Environment(cr, SUPERUSER_ID, {})
template = env.ref('mail.mail_template_data_notification_email_default')

# Send test email
mail = env['mail.mail'].create({
    'subject': 'Odoo Email Test',
    'body_html': '<p>Testing Odoo email via Mailgun</p>',
    'email_to': 'your-email@example.com',
    'email_from': 'notifications@insightpulseai.com',
})
mail.send()
```

### 4. Check Email Logs

In Odoo: **Settings → Technical → Email → Emails**

Filter by state: `exception` to find failed emails.

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Connection refused" | Check port 587 is not blocked by firewall |
| "Authentication failed" | Verify SMTP credentials in Mailgun dashboard |
| "Sender not allowed" | Check FROM Filtering matches your domain |
| "SPF fail" | Ensure SPF record includes `mailgun.org` |
| "DKIM fail" | Verify DKIM records are correctly added |
| "Emails stuck in outbox" | Check Odoo mail queue cron job is running |

### Debug Mode

Enable mail debug logging in `odoo.conf`:

```ini
[options]
log_level = debug
log_handler = :DEBUG,odoo.addons.mail:DEBUG
```

### Check Mail Queue

```sql
-- In PostgreSQL
SELECT id, state, email_to, email_from, failure_reason
FROM mail_mail
WHERE state = 'exception'
ORDER BY id DESC
LIMIT 10;
```

## Security Best Practices

1. **Never commit SMTP passwords** to version control
2. **Use environment variables** for all secrets
3. **Rotate SMTP passwords** regularly
4. **Monitor bounce rates** in Mailgun dashboard
5. **Set up DMARC reporting** to monitor domain abuse
6. **Use webhook signing** to verify Mailgun callbacks

## Related Documentation

- [Odoo 19.0 Email Documentation](https://www.odoo.com/documentation/19.0/applications/general/email_communication.html)
- [Mailgun Documentation](https://documentation.mailgun.com/)
- [Zoho Mail Documentation](https://www.zoho.com/mail/help/)
