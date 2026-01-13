# DNS & Mailgun Configuration

**Domain**: `insightpulseai.net`
**Mailgun Subdomain**: `mg.insightpulseai.net`
**Canonical IP**: `178.128.112.214` (DigitalOcean Droplet)

## DNS Status: ✅ Correctly Configured

### 1. Mailgun Subdomain (mg.insightpulseai.net)

**MX Records** (Inbound email routing):
```
mg  MX  10  mxa.mailgun.org
mg  MX  10  mxb.mailgun.org
```
→ All inbound email to `*@mg.insightpulseai.net` routed to Mailgun

**SPF Record**:
```
mg  TXT  v=spf1 include:mailgun.org ~all
```
→ Authorizes Mailgun to send email on behalf of mg subdomain

**DKIM Record**:
```
pic._domainkey.mg  TXT  k=rsa; p=...
```
→ Mailgun signing key for email authentication

**DMARC Record**:
```
_dmarc.mg  TXT  v=DMARC1; p=none; rua=mailto:postmaster@mg.insightpulseai.net
```
→ Policy: `p=none` (monitor-only, safe for testing)

**Domain Connect**:
```
email.mg  CNAME  mailgun.org
```
→ Provider-side feature, no conflict

### 2. App Endpoints (All → 178.128.112.214)

| Subdomain | Type | Target | Service |
|-----------|------|--------|---------|
| erp | A | 178.128.112.214 | Odoo ERP |
| n8n | A | 178.128.112.214 | n8n Automation |
| superset | A | 178.128.112.214 | Apache Superset |
| mcp | A | 178.128.112.214 | MCP Hub |
| auth | A | 178.128.112.214 | Auth Service |
| @ | A | 178.128.112.214 | Root domain |
| www | CNAME | insightpulseai.net | WWW redirect |

**Reverse Proxy**: Nginx routes by hostname on 178.128.112.214

### 3. SSL/TLS Configuration

**CAA Record**:
```
@  CAA  0 issue "letsencrypt.org"
```
→ Only Let's Encrypt can issue certificates (automatic TLS)

### 4. Root Domain Email (Optional)

For sending from `user@insightpulseai.net` (not `mg.*`), additional SPF/DKIM needed.
**Current setup**: Only `mg.insightpulseai.net` configured for Mailgun.

## Mailgun Domain Verification

**Action Required**: Verify domain in Mailgun UI

1. Go to **Sending → Domains → mg.insightpulseai.net**
2. Click **"Check DNS Records"**
3. Ensure all checks are ✅ green:
   - SPF ✅
   - DKIM ✅
   - MX ✅
   - Tracking ✅

## SMTP Credentials (Outbound Email)

**For Odoo, n8n, Superset, etc.**:

```yaml
SMTP Host: smtp.mailgun.org
Port: 587
Security: STARTTLS
Username: postmaster@mg.insightpulseai.net
Password: <MAILGUN_SMTP_PASSWORD>
From Address: no-reply@mg.insightpulseai.net
```

**Environment Variables** (add to `~/.zshrc`):
```bash
export MAILGUN_SMTP_HOST="smtp.mailgun.org"
export MAILGUN_SMTP_PORT="587"
export MAILGUN_SMTP_USER="postmaster@mg.insightpulseai.net"
export MAILGUN_SMTP_PASSWORD="<your-mailgun-smtp-password>"
export MAILGUN_FROM_EMAIL="no-reply@mg.insightpulseai.net"
```

## Inbound Email Routing (Webhooks)

**Mailgun Routes** - Forward inbound email to n8n/Odoo

### Example: Support Ticketing

**Mailgun UI → Receiving → Routes → New Route**:

```yaml
Priority: 0
Expression: match_recipient("support@mg.insightpulseai.net")
Actions:
  - forward("https://n8n.insightpulseai.net/webhook/mailgun-inbound")
  - store(notify="https://n8n.insightpulseai.net/webhook/mailgun-stored")
Description: Forward support emails to n8n webhook
```

### Example: Odoo Helpdesk

```yaml
Priority: 1
Expression: match_recipient("helpdesk@mg.insightpulseai.net")
Actions:
  - forward("https://erp.insightpulseai.net/mailgun/inbound")
Description: Forward helpdesk emails to Odoo
```

### Example: Catch-All

```yaml
Priority: 99
Expression: match_recipient(".*@mg.insightpulseai.net")
Actions:
  - forward("postmaster@mg.insightpulseai.net")
Description: Catch-all for unmatched recipients
```

## Odoo Configuration (Outgoing Mail Server)

**Settings → Technical → Outgoing Mail Servers → Create**:

```python
{
    'name': 'Mailgun (mg.insightpulseai.net)',
    'smtp_host': 'smtp.mailgun.org',
    'smtp_port': 587,
    'smtp_encryption': 'starttls',
    'smtp_user': 'postmaster@mg.insightpulseai.net',
    'smtp_pass': os.getenv('MAILGUN_SMTP_PASSWORD'),
    'smtp_from': 'no-reply@mg.insightpulseai.net',
    'sequence': 10,
}
```

**Test Command**:
```bash
docker exec odoo-core odoo shell -d odoo_core <<'PYEOF'
mail_server = env['ir.mail_server'].search([('name', '=', 'Mailgun (mg.insightpulseai.net)')], limit=1)
if mail_server:
    mail_server.test_smtp_connection()
    print("✅ SMTP connection successful")
else:
    print("❌ Mail server not found")
PYEOF
```

## n8n Webhook (Inbound Email Handler)

**Webhook URL**: `https://n8n.insightpulseai.net/webhook/mailgun-inbound`

**Sample n8n Workflow**:

```json
{
  "name": "Mailgun Inbound Handler",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "mailgun-inbound",
        "responseMode": "onReceived",
        "options": {}
      }
    },
    {
      "name": "Parse Email",
      "type": "n8n-nodes-base.set",
      "parameters": {
        "values": {
          "string": [
            {"name": "from", "value": "={{$json.sender}}"},
            {"name": "to", "value": "={{$json.recipient}}"},
            {"name": "subject", "value": "={{$json.subject}}"},
            {"name": "body", "value": "={{$json['stripped-text']}}"}
          ]
        }
      }
    },
    {
      "name": "Route to Service",
      "type": "n8n-nodes-base.switch",
      "parameters": {
        "conditions": {
          "string": [
            {"value1": "={{$json.to}}", "operation": "contains", "value2": "support@"}
          ]
        }
      }
    }
  ]
}
```

## Verification Checklist

- [ ] Mailgun domain verified (all DNS checks green)
- [ ] SMTP credentials added to `~/.zshrc`
- [ ] Odoo outgoing mail server configured
- [ ] Test email sent from Odoo successfully
- [ ] Mailgun Routes configured for inbound
- [ ] n8n webhook tested with sample email
- [ ] Inbound email delivered to correct service

## Troubleshooting

**SMTP Connection Failed**:
```bash
# Test with curl
curl --url 'smtp://smtp.mailgun.org:587' \
  --mail-from 'no-reply@mg.insightpulseai.net' \
  --mail-rcpt 'test@example.com' \
  --user 'postmaster@mg.insightpulseai.net:<password>' \
  --upload-file - <<EOF
From: no-reply@mg.insightpulseai.net
To: test@example.com
Subject: Test Email

This is a test email from Mailgun.
EOF
```

**Inbound Not Working**:
1. Check Mailgun Logs: **Sending → Logs** in Mailgun UI
2. Verify webhook endpoint accessible: `curl https://n8n.insightpulseai.net/webhook/mailgun-inbound`
3. Check Mailgun Routes: Ensure priority and expression are correct

**DNS Propagation**:
```bash
# Check MX records
dig +short mg.insightpulseai.net MX

# Check SPF
dig +short mg.insightpulseai.net TXT | grep spf

# Check DKIM
dig +short pic._domainkey.mg.insightpulseai.net TXT
```

## Related Documentation

- **CLAUDE.md** - Infrastructure configuration section
- **docs/email/** - Email integration patterns
- **n8n/** - n8n workflow templates
