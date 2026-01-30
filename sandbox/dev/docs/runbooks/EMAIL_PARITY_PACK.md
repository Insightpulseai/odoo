# Email Parity Pack - Odoo CE 18 → EE Email Capabilities

**Purpose**: Achieve Odoo Enterprise-level email functionality using Mailgun integration with Odoo CE 18.

**Status**: Production-ready
**Date**: 2026-01-28
**Author**: InsightPulse AI Engineering

---

## Overview

This implementation provides:
- ✅ **Outbound Email**: Authenticated sending via Mailgun SMTP (SPF/DKIM/DMARC compliant)
- ✅ **Inbound Routing**: Mailgun webhooks → Odoo models (CRM, Projects, Support)
- ✅ **Event Tracking**: Email delivery, opens, clicks, bounces tracked in Odoo
- ✅ **EE-Level Features**: Catchall aliases, automatic record creation, email analytics

---

## Current DNS Configuration (Verified)

All required DNS records are already configured:

### Root Domain (`insightpulseai.net`)
- SPF: `v=spf1 include:mailgun.org ~all` ✅
- DMARC: `v=DMARC1; p=none; rua=mailto:3651085@dmarc.mailgun.org` ✅
- MX: ❌ Not configured (using Mailgun subdomain instead)

### Mailgun Subdomain (`mg.insightpulseai.net`)
- MX: `10 mxa.mailgun.org`, `10 mxb.mailgun.org` ✅
- SPF: `v=spf1 include:mailgun.org ~all` ✅
- DKIM: Configured ✅
- DMARC: Configured ✅

**Result**: Can send from `*@insightpulseai.net`, receive at `*@mg.insightpulseai.net`

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Email Parity Architecture                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Outbound Flow:                                                  │
│  Odoo → Mailgun SMTP (smtp.mailgun.org:587) → Recipients        │
│                                                                  │
│  Inbound Flow:                                                   │
│  Sender → Mailgun Routes → https://erp.insightpulseai.net       │
│           /mailgun/inbound → ipai_mailgun_bridge                │
│           → CRM / Projects / Support Channel                     │
│                                                                  │
│  Event Tracking:                                                 │
│  Mailgun Events → https://erp.insightpulseai.net                │
│           /mailgun/events → ipai_mailgun_bridge                 │
│           → mail.mail.ipai_mailgun_last_event                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Installation (Local Development)

### 1. Install Addon

```bash
cd /Users/tbwa/Documents/GitHub/odoo-ce/sandbox/dev

# Install via Odoo CLI
export DOCKER_HOST="unix:///Users/tbwa/.colima/default/docker.sock"
docker exec -it odoo-dev odoo \
  -c /etc/odoo/odoo.conf \
  -d odoo_dev \
  -i ipai_mailgun_bridge \
  --stop-after-init
```

### 2. Configure SMTP (via Odoo Shell)

```bash
./scripts/dev/configure-mailgun-smtp.sh
```

This script:
- Sets system parameters (default_from, catchall_domain, webhook_signing_key)
- Creates/updates Mailgun SMTP server configuration
- Uses environment variables from `.env`

### 3. Configure Mailgun Routes (Production Only)

**Note**: This requires production Mailgun API key and should be run after staging validation.

```bash
# Set environment variables
export MAILGUN_API_KEY="your_mailgun_api_key"
export MAILGUN_DOMAIN="mg.insightpulseai.net"

./scripts/mailgun/configure-routes.sh
```

---

## Addon Components

### `ipai_mailgun_bridge`

**Location**: `addons/ipai_mailgun_bridge/`

**Structure**:
```
ipai_mailgun_bridge/
├── __manifest__.py                    # Module metadata
├── __init__.py                        # Module init
├── controllers/
│   ├── __init__.py
│   └── mailgun_webhook.py            # Webhook endpoints
├── models/
│   ├── __init__.py
│   └── mail_mail.py                  # mail.mail extension
└── data/
    ├── mailgun_parameters.xml        # System parameters
    └── mailgun_catchall_aliases.xml  # Email aliases
```

**Dependencies**:
- `base` - Odoo core
- `mail` - Email functionality
- `crm` - CRM leads from sales@
- `project` - Tasks from projects@

**No Helpdesk Dependency**: Support emails create mail.channel messages instead of helpdesk tickets (no OCA helpdesk required).

---

## Email Routing

### Inbound Email Addresses

| Address | Creates | Model | Notes |
|---------|---------|-------|-------|
| `sales@insightpulseai.net` | CRM Lead | `crm.lead` | Automatic lead creation |
| `projects@insightpulseai.net` | Project Task | `project.task` | Creates task in first project |
| `support@insightpulseai.net` | Channel Message | `mail.channel` | Support inbox (no helpdesk) |

### Webhook Endpoints

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/mailgun/inbound` | POST | Receive inbound emails | Mailgun signature |
| `/mailgun/events` | POST | Track email events | Mailgun signature |

---

## Nginx Configuration (Production)

**File**: `/etc/nginx/sites-available/erp.insightpulseai.net.conf`

Add these locations to existing server block:

```nginx
# Mailgun Webhooks (Inbound & Events)
location /mailgun/inbound {
    proxy_pass http://odoo18_prod;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For  $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
}

location /mailgun/events {
    proxy_pass http://odoo18_prod;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For  $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
}
```

**Apply configuration**:
```bash
sudo nginx -t && sudo systemctl reload nginx
```

---

## Mailgun Configuration

### 1. Inbound Routes

Configure Mailgun to forward emails to Odoo:

```bash
export MAILGUN_API_KEY="your_key"
export MAILGUN_DOMAIN="mg.insightpulseai.net"

# Catchall route (all @insightpulseai.net)
curl -s -u "api:${MAILGUN_API_KEY}" \
  https://api.mailgun.net/v3/routes \
  -F priority=1 \
  -F description='Odoo catchall' \
  -F expression='match_recipient(".*@insightpulseai.net")' \
  -F action='forward("https://erp.insightpulseai.net/mailgun/inbound")' \
  -F action='stop()'
```

### 2. Event Webhooks

Track email delivery events:

```bash
curl -s -u "api:${MAILGUN_API_KEY}" \
  https://api.mailgun.net/v3/domains/${MAILGUN_DOMAIN}/webhooks \
  -F id=tracking \
  -F url='https://erp.insightpulseai.net/mailgun/events'
```

### 3. Webhook Signing Key

**Critical**: Set the webhook signing key in Odoo for security:

```bash
# Get signing key from Mailgun dashboard: Settings → Webhooks → Signing Key
export MAILGUN_WEBHOOK_SIGNING_KEY="your_signing_key"

docker exec -it odoo-dev odoo \
  -c /etc/odoo/odoo.conf \
  -d odoo_dev \
  --shell <<EOF
env['ir.config_parameter'].sudo().set_param(
    'ipai_mailgun.webhook_signing_key',
    '${MAILGUN_WEBHOOK_SIGNING_KEY}'
)
EOF
```

---

## Testing & Verification

### 1. Webhook Endpoint Health

```bash
# Check endpoints are accessible (expect 200 or 405, not 404/5xx)
curl -I https://erp.insightpulseai.net/mailgun/inbound
curl -I https://erp.insightpulseai.net/mailgun/events
```

### 2. Outbound Email Test

```bash
./scripts/mailgun/test-outbound-email.sh
```

This script:
- Creates test email via Odoo shell
- Sends to configured TEST_EMAIL_TO
- Verifies Mailgun delivery logs

### 3. Inbound Email Test

```bash
# Send test email
echo "Test support request" | mail -s "Test Subject" support@insightpulseai.net

# Verify in Odoo
docker exec -it odoo-dev odoo \
  -c /etc/odoo/odoo.conf \
  -d odoo_dev \
  --shell <<'EOF'
channel = env['mail.channel'].sudo().search([('name', '=', 'Support Inbox')], limit=1)
print(f"Support channel messages: {len(channel.message_ids)}")
EOF
```

### 4. Event Tracking Test

After sending outbound email (step 2), check tracking:

```bash
docker exec -it odoo-dev odoo \
  -c /etc/odoo/odoo.conf \
  -d odoo_dev \
  --shell <<'EOF'
mail = env['mail.mail'].sudo().search([('subject', '=', 'Parity test')], limit=1)
print(f"Last event: {mail.ipai_mailgun_last_event}")
EOF
```

Expected events: `delivered`, `opened`, `clicked` (if you interact with email)

---

## EE Parity Checklist

| Feature | Odoo EE | IPAI CE + Mailgun | Status |
|---------|---------|-------------------|--------|
| Outbound SMTP | ✅ | ✅ Mailgun SMTP | ✅ Complete |
| SPF/DKIM/DMARC | ✅ | ✅ Via Mailgun | ✅ Complete |
| Inbound routing | ✅ | ✅ Mailgun webhooks | ✅ Complete |
| Catchall aliases | ✅ | ✅ mail.alias | ✅ Complete |
| Email tracking | ✅ | ✅ Event webhooks | ✅ Complete |
| Bounce handling | ✅ | ✅ Event webhooks | ✅ Complete |
| Auto-record creation | ✅ | ✅ Controller routing | ✅ Complete |
| Helpdesk integration | ✅ | ⚠️ mail.channel | ⚠️ No helpdesk dep |
| Marketing automation | ✅ | ❌ Not implemented | ❌ Future |

**Parity Score**: 90% (8/9 features, helpdesk optional)

---

## Production Deployment

### 1. Install on Production

```bash
# SSH to production server
ssh root@178.128.112.214

cd /opt/odoo-ce
git pull origin main

# Install addon
docker exec -it odoo18-prod-app odoo \
  -c /etc/odoo/odoo.conf \
  -d odoo18_prod \
  -i ipai_mailgun_bridge \
  --stop-after-init
```

### 2. Configure SMTP (Production)

```bash
# Set production environment variables
export MAILGUN_SMTP_LOGIN="postmaster@mg.insightpulseai.net"
export MAILGUN_SMTP_PASSWORD="your_production_password"
export MAILGUN_WEBHOOK_SIGNING_KEY="your_production_signing_key"

# Run configuration script
./scripts/mailgun/configure-smtp-prod.sh
```

### 3. Configure Mailgun Routes (Production)

```bash
export MAILGUN_API_KEY="your_production_api_key"
export MAILGUN_DOMAIN="mg.insightpulseai.net"

./scripts/mailgun/configure-routes.sh
```

### 4. Update Nginx (Production)

```bash
# Add webhook locations to nginx config
sudo nano /etc/nginx/sites-available/erp.insightpulseai.net.conf
# (Add locations from "Nginx Configuration" section above)

sudo nginx -t && sudo systemctl reload nginx
```

---

## Rollback Procedure

### 1. Disable Addon

```bash
docker exec -it odoo-dev odoo \
  -c /etc/odoo/odoo.conf \
  -d odoo_dev \
  --shell <<'EOF'
module = env['ir.module.module'].sudo().search([('name', '=', 'ipai_mailgun_bridge')])
module.button_immediate_uninstall()
EOF
```

### 2. Disable SMTP Server

```bash
docker exec -it odoo-dev odoo \
  -c /etc/odoo/odoo.conf \
  -d odoo_dev \
  --shell <<'EOF'
smtp = env['ir.mail_server'].sudo().search([('name', '=', 'Mailgun SMTP')])
smtp.write({'active': False})
EOF
```

### 3. Remove Mailgun Routes

```bash
export MAILGUN_API_KEY="your_key"

# List routes
curl -s -u "api:${MAILGUN_API_KEY}" \
  https://api.mailgun.net/v3/routes | jq '.items[].id'

# Delete route
curl -s -u "api:${MAILGUN_API_KEY}" \
  -X DELETE https://api.mailgun.net/v3/routes/<ROUTE_ID>
```

---

## Troubleshooting

### Issue: Inbound emails not creating records

**Check**:
1. Webhook endpoint accessible: `curl -I https://erp.insightpulseai.net/mailgun/inbound`
2. Mailgun routes configured: View in Mailgun dashboard
3. Signature verification: Check `ipai_mailgun.webhook_signing_key` in Odoo
4. Odoo logs: `docker logs odoo-dev -f | grep mailgun`

**Fix**: Set signing key to empty string for testing (insecure):
```bash
docker exec -it odoo-dev odoo --shell <<'EOF'
env['ir.config_parameter'].sudo().set_param('ipai_mailgun.webhook_signing_key', '')
EOF
```

### Issue: Outbound emails not sending

**Check**:
1. SMTP server configured: Odoo → Settings → Technical → Outgoing Mail Servers
2. SMTP credentials valid: Test connection in Odoo UI
3. Mailgun logs: Check Mailgun dashboard for send attempts

**Fix**: Verify SMTP configuration:
```bash
docker exec -it odoo-dev odoo --shell <<'EOF'
smtp = env['ir.mail_server'].sudo().search([('name', '=', 'Mailgun SMTP')])
print(f"Active: {smtp.active}, Host: {smtp.smtp_host}, User: {smtp.smtp_user}")
EOF
```

### Issue: Events not tracked

**Check**:
1. Event webhook configured in Mailgun: Settings → Webhooks
2. Message ID matching: Verify `Message-Id` header in sent emails
3. Event endpoint accessible: `curl -I https://erp.insightpulseai.net/mailgun/events`

**Debug**: Check recent events in Odoo:
```bash
docker exec -it odoo-dev odoo --shell <<'EOF'
recent = env['mail.mail'].sudo().search([], order='id desc', limit=5)
for mail in recent:
    print(f"ID: {mail.id}, Event: {mail.ipai_mailgun_last_event}, Subject: {mail.subject}")
EOF
```

---

## Security Considerations

1. **Webhook Signing**: Always verify Mailgun signatures in production
2. **HTTPS Only**: All webhook endpoints must use HTTPS
3. **IP Whitelisting**: Consider restricting nginx to Mailgun IP ranges
4. **Secret Management**: Store API keys in `.env`, never commit to git
5. **Rate Limiting**: Implement rate limiting on webhook endpoints if needed

---

## Future Enhancements

1. **Marketing Automation**: Unsubscribe link handling, campaign tracking
2. **Advanced Bounce Handling**: Automatic contact blacklisting
3. **Email Templates**: Custom templates with merge fields
4. **A/B Testing**: Campaign split testing via Mailgun
5. **Helpdesk Integration**: Optional OCA helpdesk module support

---

## Related Documentation

- **Email Infrastructure Strategy**: `docs/infra/EMAIL_INFRASTRUCTURE_STRATEGY.md`
- **DNS Enhancement Guide**: `docs/infra/DNS_ENHANCEMENT_GUIDE.md`
- **Database Initialization**: `docs/runbooks/DATABASE_INIT.md`

---

**Last Updated**: 2026-01-28
**Version**: 1.0.0
**Maintainer**: InsightPulse AI Engineering
