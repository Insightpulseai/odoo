# Mailgun Integration

> **Generated:** 2026-01-21
> **Purpose:** SMTP and transactional email for Odoo CE (IAP replacement)

---

## Overview

Mailgun replaces Odoo IAP mail services with direct SMTP integration. This provides:

1. **Transactional Email** - Order confirmations, password resets, notifications
2. **Mass Mailing** - Marketing campaigns via `mass_mailing` module
3. **Email Tracking** - Open/click tracking via webhooks
4. **Deliverability** - SPF, DKIM, DMARC authentication

---

## Configuration

### Mailgun Account Setup

1. Create account at https://signup.mailgun.com
2. Verify your domain (e.g., `mg.insightpulseai.net`)
3. Configure DNS records:

```
# SPF Record
TXT  @  "v=spf1 include:mailgun.org ~all"

# DKIM Record
TXT  smtp._domainkey  "k=rsa; p=MIG..."

# DMARC Record
TXT  _dmarc  "v=DMARC1; p=quarantine; rua=mailto:dmarc@insightpulseai.net"

# MX Records (for receiving)
MX  mg  mxa.mailgun.org (priority 10)
MX  mg  mxb.mailgun.org (priority 10)
```

### Environment Variables

```bash
# .env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_SSL=False
SMTP_USER=postmaster@mg.insightpulseai.net
SMTP_PASSWORD=__MAILGUN_SMTP_PASSWORD__
EMAIL_FROM=noreply@insightpulseai.net

# API (for webhooks/tracking)
MAILGUN_API_KEY=key-...
MAILGUN_DOMAIN=mg.insightpulseai.net
MAILGUN_WEBHOOK_SIGNING_KEY=...
```

### odoo.conf

```ini
[options]
smtp_server = smtp.mailgun.org
smtp_port = 587
smtp_ssl = False
smtp_user = postmaster@mg.insightpulseai.net
smtp_password = ${SMTP_PASSWORD}
email_from = noreply@insightpulseai.net
```

---

## Odoo Configuration

### Outgoing Mail Server (ir.mail_server)

```xml
<!-- data/mail_servers.xml -->
<odoo noupdate="1">
    <record id="mailgun_smtp_server" model="ir.mail_server">
        <field name="name">Mailgun SMTP</field>
        <field name="smtp_host">smtp.mailgun.org</field>
        <field name="smtp_port">587</field>
        <field name="smtp_encryption">starttls</field>
        <field name="smtp_user">postmaster@mg.insightpulseai.net</field>
        <field name="smtp_pass">__SMTP_PASSWORD__</field>
        <field name="from_filter">insightpulseai.net</field>
        <field name="sequence">1</field>
    </record>
</odoo>
```

### System Parameters

```xml
<odoo noupdate="1">
    <record id="param_mail_from" model="ir.config_parameter">
        <field name="key">mail.default.from</field>
        <field name="value">noreply@insightpulseai.net</field>
    </record>
    <record id="param_mail_catchall" model="ir.config_parameter">
        <field name="key">mail.catchall.alias</field>
        <field name="value">catchall</field>
    </record>
    <record id="param_mail_bounce" model="ir.config_parameter">
        <field name="key">mail.bounce.alias</field>
        <field name="value">bounce</field>
    </record>
    <record id="param_mail_domain" model="ir.config_parameter">
        <field name="key">mail.catchall.domain</field>
        <field name="value">insightpulseai.net</field>
    </record>
</odoo>
```

---

## Email Tracking (OCA Integration)

### Install OCA mail_tracking

```bash
# Install via pip
pip install odoo-addon-mail_tracking
pip install odoo-addon-mail_tracking_mailgun

# Or via Odoo CLI
odoo-bin -d odoo_core -i mail_tracking,mail_tracking_mailgun --stop-after-init
```

### Webhook Configuration

Configure webhooks in Mailgun dashboard to point to:

```
https://erp.insightpulseai.net/mail/tracking/mailgun/all
```

Events to track:
- `delivered`
- `opened`
- `clicked`
- `unsubscribed`
- `complained`
- `bounced`
- `dropped`

### Webhook Controller

```python
# ipai_mail_integration/controllers/mailgun_webhook.py

import hmac
import hashlib
from odoo import http
from odoo.http import request

class MailgunWebhookController(http.Controller):

    @http.route('/mail/tracking/mailgun/all', type='json', auth='none', csrf=False)
    def mailgun_webhook(self, **post):
        """Handle Mailgun webhook events."""
        # Verify signature
        signing_key = request.env['ir.config_parameter'].sudo().get_param(
            'mailgun.webhook_signing_key', ''
        )

        timestamp = post.get('signature', {}).get('timestamp', '')
        token = post.get('signature', {}).get('token', '')
        signature = post.get('signature', {}).get('signature', '')

        expected = hmac.new(
            signing_key.encode(),
            f'{timestamp}{token}'.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            return {'error': 'Invalid signature'}

        # Process event
        event_data = post.get('event-data', {})
        event_type = event_data.get('event')
        message_id = event_data.get('message', {}).get('headers', {}).get('message-id')

        if message_id:
            mail = request.env['mail.mail'].sudo().search([
                ('message_id', '=', message_id)
            ], limit=1)

            if mail:
                if event_type == 'delivered':
                    mail.write({'state': 'sent'})
                elif event_type in ('bounced', 'dropped'):
                    mail.write({'state': 'exception', 'failure_reason': event_type})

        return {'status': 'ok'}
```

---

## Mass Mailing Configuration

### ipai_mail_integration Settings

```python
# models/res_config_settings.py

ipai_mass_mailing_provider = fields.Selection([
    ('smtp', 'SMTP (Any Provider)'),
    ('mailgun', 'Mailgun API'),
    ('ses', 'AWS SES API'),
    ('sendgrid', 'SendGrid API'),
], string="Mass Mailing Provider",
   config_parameter="ipai_mail.mass_mailing_provider",
   default="smtp")

ipai_mailgun_api_key = fields.Char(
    string="Mailgun API Key",
    config_parameter="ipai_mail.mailgun_api_key",
)
ipai_mailgun_domain = fields.Char(
    string="Mailgun Domain",
    config_parameter="ipai_mail.mailgun_domain",
)
```

### Mailgun API Integration

```python
# models/mail_mailgun.py

import requests
from odoo import models, api

class MailgunMixin(models.AbstractModel):
    _name = 'mail.mailgun.mixin'
    _description = 'Mailgun API Mixin'

    @api.model
    def _mailgun_send(self, to, subject, html, from_email=None):
        """Send email via Mailgun API."""
        ICP = self.env['ir.config_parameter'].sudo()
        api_key = ICP.get_param('ipai_mail.mailgun_api_key')
        domain = ICP.get_param('ipai_mail.mailgun_domain')

        if not api_key or not domain:
            raise ValueError("Mailgun API key and domain required")

        from_email = from_email or ICP.get_param('mail.default.from')

        response = requests.post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            data={
                "from": from_email,
                "to": to if isinstance(to, list) else [to],
                "subject": subject,
                "html": html,
            }
        )
        response.raise_for_status()
        return response.json()

    @api.model
    def _mailgun_validate_email(self, email):
        """Validate email address via Mailgun."""
        ICP = self.env['ir.config_parameter'].sudo()
        api_key = ICP.get_param('ipai_mail.mailgun_api_key')

        response = requests.get(
            "https://api.mailgun.net/v4/address/validate",
            auth=("api", api_key),
            params={"address": email}
        )

        if response.status_code == 200:
            data = response.json()
            return {
                'is_valid': data.get('result') == 'deliverable',
                'risk': data.get('risk'),
                'reason': data.get('reason'),
            }
        return {'is_valid': False, 'reason': 'validation_failed'}
```

---

## Inbound Email (Mailgate)

### Configure Mailgun Routes

In Mailgun dashboard, create route:

```
Match recipient: catchall@insightpulseai.net
Action: forward("https://erp.insightpulseai.net/mail/mailgate")
```

### Mailgate Controller

Already provided in `ipai_enterprise_bridge`:
- `/mail/mailgate` - Standard Odoo mailgate endpoint
- Parses incoming MIME messages
- Routes to appropriate mail.thread models

---

## Validation

```bash
# Test SMTP connection
python3 << 'EOF'
import smtplib
import os

server = smtplib.SMTP(os.environ['SMTP_HOST'], int(os.environ['SMTP_PORT']))
server.starttls()
server.login(os.environ['SMTP_USER'], os.environ['SMTP_PASSWORD'])
print("SMTP connection successful")
server.quit()
EOF

# Test Mailgun API
curl -s --user "api:$MAILGUN_API_KEY" \
    "https://api.mailgun.net/v3/domains/$MAILGUN_DOMAIN"

# Send test email
curl -s --user "api:$MAILGUN_API_KEY" \
    "https://api.mailgun.net/v3/$MAILGUN_DOMAIN/messages" \
    -F from="Test <noreply@$MAILGUN_DOMAIN>" \
    -F to="test@example.com" \
    -F subject="Mailgun Test" \
    -F text="This is a test email from Odoo CE."
```

---

## Deliverability Checklist

- [ ] Domain verified in Mailgun
- [ ] SPF record configured
- [ ] DKIM record configured
- [ ] DMARC record configured
- [ ] Bounce alias configured
- [ ] Catchall alias configured
- [ ] Webhooks configured
- [ ] Test email sent successfully
- [ ] Inbound mail routing tested

---

*See [EE_IAP_TO_OCA_IPAI_MAPPING.md](../EE_IAP_TO_OCA_IPAI_MAPPING.md) for IAP replacement details*
