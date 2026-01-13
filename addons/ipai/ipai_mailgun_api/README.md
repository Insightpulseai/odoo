# IPAI Mailgun API

HTTP API email integration for Mailgun to bypass SMTP port blocking.

## Problem

DigitalOcean blocks outbound SMTP ports 25/587/465 by default as an anti-spam policy. This prevents standard SMTP email sending from working on DigitalOcean droplets.

## Solution

This module replaces SMTP-based email sending with Mailgun's HTTP API, which operates over HTTPS (port 443) and is not subject to port blocking.

## Features

- ✅ HTTP API email sending (bypasses port blocking)
- ✅ Automatic fallback to SMTP if API not configured
- ✅ Configurable via system parameters
- ✅ Better monitoring and logging than SMTP
- ✅ Compatible with all Odoo email workflows
- ✅ Supports text and HTML emails
- ✅ CC/BCC support

## Installation

1. Install the module:
   ```bash
   # Via Odoo UI: Apps > Search "IPAI Mailgun API" > Install
   # OR via command line:
   odoo -d odoo_core -i ipai_mailgun_api --stop-after-init
   ```

2. Install Python requests library (if not already installed):
   ```bash
   pip3 install requests
   # OR in Docker:
   docker exec odoo-prod pip3 install requests
   ```

## Configuration

### 1. Get Mailgun API Key

1. Login to Mailgun: https://app.mailgun.com/
2. Navigate to **Sending > Domain Settings > mg.insightpulseai.net**
3. Click **API Keys** tab
4. Copy the **Private API Key** (starts with `key-`)

### 2. Configure in Odoo

**Option A: Via UI** (Recommended)

1. Go to **Settings > Technical > Parameters > System Parameters**
2. Find or create these parameters:
   - **Key**: `mailgun.api_key` | **Value**: `key-xxxxxxxx` (your API key)
   - **Key**: `mailgun.domain` | **Value**: `mg.insightpulseai.net`
   - **Key**: `mailgun.use_api` | **Value**: `True`

**Option B: Via Environment Variables** (Production)

Set in `/opt/odoo-ce/repo/deploy/.env`:

```bash
MAILGUN_API_KEY=key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MAILGUN_DOMAIN=mg.insightpulseai.net
```

Then add to `deploy/odoo.conf`:

```ini
[options]
; Mailgun API configuration
mailgun_api_key = ${MAILGUN_API_KEY}
mailgun_domain = ${MAILGUN_DOMAIN}
```

### 3. Remove Old SMTP Configuration (Optional)

Since SMTP is blocked, you can remove the old SMTP mail server:

1. Go to **Settings > Technical > Email > Outgoing Mail Servers**
2. Delete or archive the SMTP server for `smtp.mailgun.org`

## Testing

### Test via Python Script

```bash
ssh root@178.128.112.214
cd /opt/odoo-ce/repo

# Set API key
export MAILGUN_API_KEY=key-xxxxxxxx

# Run test
python3 scripts/send_via_mailgun_api.py \
  business@insightpulseai.com \
  "Mailgun API Test" \
  "This email was sent via Mailgun HTTP API"

# Expected output:
# ✅ Email sent successfully
#    Message ID: <xxxxxxxx.xxxxxxxx@mg.insightpulseai.net>
#    Status: Queued. Thank you.
```

### Test via Odoo UI

1. Go to **Settings > Technical > Email > Emails**
2. Click **Create** to compose a test email
3. Fill in:
   - **To**: `business@insightpulseai.com`
   - **Subject**: `Mailgun API Test`
   - **Body**: `Test email sent from Odoo via Mailgun HTTP API`
4. Click **Send Now**
5. Check logs: `docker logs odoo-prod | grep -i mailgun`

### Test Finance PPM Notifications

```bash
# Trigger a BIR deadline alert (if Finance PPM module installed)
ssh root@178.128.112.214

# Via Odoo CLI
docker exec odoo-prod odoo shell -d odoo_core << 'EOF'
env = odoo.api.Environment(cr, SUPERUSER_ID, {})
bir_schedule = env['ipai.finance.bir_schedule'].search([('status', '=', 'in_progress')], limit=1)
if bir_schedule:
    bir_schedule._send_deadline_alert()
    print(f"✅ Sent alert for {bir_schedule.form_type}")
else:
    print("❌ No in_progress BIR forms found")
EOF
```

## Troubleshooting

### Email Not Sending

**Check Mailgun API key is configured:**

```bash
ssh root@178.128.112.214
docker exec odoo-prod odoo shell -d odoo_core << 'EOF'
env = odoo.api.Environment(cr, SUPERUSER_ID, {})
api_key = env['ir.config_parameter'].sudo().get_param('mailgun.api_key')
print(f"API Key configured: {bool(api_key)}")
print(f"API Key prefix: {api_key[:10] if api_key else 'NOT SET'}")
EOF
```

**Check Odoo logs:**

```bash
docker logs odoo-prod --tail 50 | grep -i mailgun
```

**Test API key directly:**

```bash
export MAILGUN_API_KEY=key-xxxxxxxx
python3 scripts/send_via_mailgun_api.py test@example.com "Test" "Body"
```

### Module Not Loading

**Verify module installed:**

```bash
docker exec odoo-prod odoo shell -d odoo_core << 'EOF'
env = odoo.api.Environment(cr, SUPERUSER_ID, {})
module = env['ir.module.module'].search([('name', '=', 'ipai_mailgun_api')])
print(f"Module state: {module.state}")
EOF
```

**Reinstall if needed:**

```bash
docker exec odoo-prod odoo -d odoo_core -u ipai_mailgun_api --stop-after-init
docker restart odoo-prod
```

### API Rate Limits

Mailgun free tier limits:
- **5,000 emails/month** (free tier)
- **10 messages/second** rate limit

If you hit limits, check Mailgun dashboard: https://app.mailgun.com/

## Advantages Over SMTP

| Feature | SMTP | HTTP API |
|---------|------|----------|
| Port blocking | ❌ Blocked by DigitalOcean | ✅ Uses HTTPS (443) |
| Monitoring | ⚠️ Limited | ✅ Full dashboard + webhooks |
| Error messages | ⚠️ Cryptic codes | ✅ Clear JSON responses |
| Batch sending | ❌ One at a time | ✅ Batch API available |
| Templates | ❌ No | ✅ Yes |
| Webhooks | ❌ No | ✅ Yes |
| Debugging | ⚠️ Difficult | ✅ Easy |

## References

- **Mailgun API Documentation**: https://documentation.mailgun.com/docs/mailgun/api-reference/openapi-final/tag/Messages/
- **Mailgun Quickstart**: https://documentation.mailgun.com/docs/mailgun/quickstart-guide/
- **Root Cause Documentation**: `docs/MAILGUN_SMTP_PORT_BLOCKED.md`
- **DNS Verification**: `docs/DNS_SETTINGS.md`

## Support

For issues or questions:
1. Check Odoo logs: `docker logs odoo-prod | grep -i mailgun`
2. Check Mailgun dashboard: https://app.mailgun.com/mg/sending/domains/mg.insightpulseai.net
3. Review documentation: `docs/MAILGUN_SMTP_PORT_BLOCKED.md`

## License

AGPL-3

## Author

InsightPulse AI - https://insightpulseai.net
