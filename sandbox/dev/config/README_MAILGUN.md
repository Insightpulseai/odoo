# Mailgun Setup for Local Sandbox

Quick setup guide for Mailgun SMTP in local Odoo sandbox.

## Prerequisites

1. **Mailgun Domain Verified**: `mg.insightpulseai.net`
   - Check: https://app.mailgun.com/app/sending/domains
   - All DNS records should be ✅ green

2. **SMTP Password**: Get from Mailgun UI
   - Go to **Sending → Domain settings → SMTP credentials**
   - Copy password for `postmaster@mg.insightpulseai.net`

## Setup Steps

### 1. Add SMTP Password to Environment

```bash
# Add to ~/.zshrc
echo 'export MAILGUN_SMTP_PASSWORD="your-mailgun-smtp-password-here"' >> ~/.zshrc
source ~/.zshrc
```

### 2. Start Sandbox

```bash
odoo-sandbox
# Or manually:
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
docker compose up -d
```

### 3. Configure Odoo Mail Server

```bash
docker exec -i odoo odoo shell -d odoo_dev_sandbox < sandbox/dev/config/mailgun_setup.py
```

Expected output:
```
✅ Mail server configured: Mailgun (mg.insightpulseai.net)
   SMTP Host: smtp.mailgun.org
   SMTP Port: 587
   SMTP User: postmaster@mg.insightpulseai.net
   From: no-reply@mg.insightpulseai.net

Testing SMTP connection...
✅ SMTP connection test PASSED
```

### 4. Test Email Send

```bash
docker exec -i odoo odoo shell -d odoo_dev_sandbox <<'PYEOF'
# Send test email
mail = env['mail.mail'].create({
    'subject': 'Test Email from Odoo Sandbox',
    'body_html': '<p>This is a test email sent via Mailgun.</p>',
    'email_from': 'no-reply@mg.insightpulseai.net',
    'email_to': 'your-email@example.com',
})
mail.send()
env.cr.commit()
print("✅ Test email sent successfully")
PYEOF
```

## Troubleshooting

### SMTP Connection Failed

**Check 1**: Verify SMTP password is correct
```bash
echo $MAILGUN_SMTP_PASSWORD | wc -c
# Should be ~40 characters
```

**Check 2**: Verify Mailgun domain DNS
```bash
dig +short mg.insightpulseai.net MX
# Should return: mxa.mailgun.org and mxb.mailgun.org
```

**Check 3**: Test SMTP directly
```bash
curl --url 'smtp://smtp.mailgun.org:587' \
  --mail-from 'no-reply@mg.insightpulseai.net' \
  --mail-rcpt 'test@example.com' \
  --user "postmaster@mg.insightpulseai.net:$MAILGUN_SMTP_PASSWORD" \
  --upload-file - <<EOF
From: no-reply@mg.insightpulseai.net
To: test@example.com
Subject: SMTP Test

This is a direct SMTP test.
EOF
```

### Email Not Received

**Check 1**: Mailgun Logs
- Go to: https://app.mailgun.com/app/sending/domains/mg.insightpulseai.net/logs
- Check for delivery status

**Check 2**: Spam Folder
- Mailgun emails may be marked as spam initially
- Add sender to whitelist

**Check 3**: Email Quotas
- Mailgun free tier: 5,000 emails/month
- Check: https://app.mailgun.com/app/account/usage

## Configuration Reference

**Odoo Mail Server Settings**:
- Name: `Mailgun (mg.insightpulseai.net)`
- SMTP Host: `smtp.mailgun.org`
- SMTP Port: `587`
- Security: `STARTTLS`
- Username: `postmaster@mg.insightpulseai.net`
- Password: `$MAILGUN_SMTP_PASSWORD`
- From: `no-reply@mg.insightpulseai.net`

**Environment Variables**:
```bash
MAILGUN_SMTP_HOST=smtp.mailgun.org
MAILGUN_SMTP_PORT=587
MAILGUN_SMTP_USER=postmaster@mg.insightpulseai.net
MAILGUN_SMTP_PASSWORD=<your-password>
MAILGUN_FROM_EMAIL=no-reply@mg.insightpulseai.net
```

## Related Documentation

- **Full DNS/Mailgun Config**: `docs/infrastructure/DNS_MAILGUN_CONFIG.md`
- **n8n Webhook Workflow**: `n8n/workflows/mailgun_inbound_handler.json`
- **Production Setup**: See `docs/email/MAILGUN_PRODUCTION.md`
