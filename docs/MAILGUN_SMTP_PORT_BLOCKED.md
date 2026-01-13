# Mailgun SMTP Port Blocking Issue

**Status:** ⚠️ DNS Verified, SMTP Blocked
**Root Cause:** DigitalOcean blocks outbound SMTP ports 25/587 by default (anti-spam policy)
**Impact:** Cannot send email via Mailgun SMTP from production droplet

---

## Problem Summary

### What Works ✅

- **DNS Records**: All 6 Mailgun DNS records verified and propagating
  - SPF: `v=spf1 include:mailgun.org ~all`
  - DKIM: Full RSA public key verified
  - MX: Both mxa.mailgun.org and mxb.mailgun.org
  - CNAME: mailgun.org tracking domain
  - DMARC: Full policy with reporting

- **Odoo Configuration**: Mail server configured correctly
  - SMTP Host: smtp.mailgun.org
  - SMTP Port: 587
  - SMTP User: postmaster@mg.insightpulseai.net
  - SMTP Password: Set in environment variable
  - Encryption: STARTTLS

### What Doesn't Work ❌

- **SMTP Connection**: Timeout after 30+ seconds
  ```bash
  curl -v --ssl-reqd \
    --url "smtp://smtp.mailgun.org:587" \
    --user "postmaster@mg.insightpulseai.net:PASSWORD" \
    --mail-from "noreply@mg.insightpulseai.net" \
    --mail-rcpt "test@example.com"

  # Result: Connection timeout (no response from smtp.mailgun.org:587)
  ```

- **Root Cause**: DigitalOcean blocks outbound connections to ports 25, 587, and 465 by default

---

## DigitalOcean SMTP Policy

From [DigitalOcean's Email Policy](https://docs.digitalocean.com/support/email-gateway-policy/):

> **Outbound SMTP Port Blocking**
>
> DigitalOcean blocks outbound SMTP traffic on ports 25, 587, and 465 for new accounts and droplets by default to prevent spam and abuse. This restriction helps maintain the reputation of our infrastructure and prevents malicious actors from using our services for spam campaigns.

**Why This Policy Exists:**
- Prevents compromised droplets from being used for spam
- Protects DigitalOcean's IP reputation with email providers
- Complies with anti-spam industry standards

**Account Age Requirements:**
- New accounts: Blocked for at least 60 days
- Existing accounts: May request port unblocking after establishing history

---

## Solution 1: Use Mailgun HTTP API (Recommended)

### Why This Is Better

1. **No Port Blocking**: HTTP API uses standard port 443 (HTTPS)
2. **Better Monitoring**: Direct API access to send logs and events
3. **More Features**: Access to templates, batch sending, webhooks
4. **Easier Debugging**: JSON responses vs SMTP error codes
5. **Higher Reliability**: No email client parsing edge cases

### Implementation

**Install Mailgun Python SDK:**
```bash
ssh root@178.128.112.214
docker exec odoo-prod pip3 install mailgun
```

**Create Python Script** (`/opt/odoo-ce/repo/scripts/send_via_mailgun_api.py`):
```python
#!/usr/bin/env python3
"""
Send email via Mailgun HTTP API instead of SMTP.

Usage:
    python send_via_mailgun_api.py <recipient> <subject> <body>

Environment variables:
    MAILGUN_API_KEY - Mailgun API key (from dashboard)
    MAILGUN_DOMAIN  - Sending domain (default: mg.insightpulseai.net)
"""

import os
import sys
import requests

def send_email(to, subject, text):
    """Send email via Mailgun HTTP API."""
    api_key = os.environ.get('MAILGUN_API_KEY')
    domain = os.environ.get('MAILGUN_DOMAIN', 'mg.insightpulseai.net')

    if not api_key:
        raise ValueError("MAILGUN_API_KEY environment variable required")

    url = f"https://api.mailgun.net/v3/{domain}/messages"

    response = requests.post(
        url,
        auth=("api", api_key),
        data={
            "from": f"InsightPulse AI <noreply@{domain}>",
            "to": to,
            "subject": subject,
            "text": text
        }
    )

    if response.status_code == 200:
        print(f"✅ Email sent successfully")
        print(f"   Message ID: {response.json()['id']}")
        print(f"   Status: {response.json()['message']}")
    else:
        print(f"❌ Email send failed: HTTP {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: send_via_mailgun_api.py <to> <subject> <text>")
        sys.exit(1)

    send_email(sys.argv[1], sys.argv[2], sys.argv[3])
```

**Test API Sending:**
```bash
ssh root@178.128.112.214
cd /opt/odoo-ce/repo

# Get API key from Mailgun dashboard or environment
export MAILGUN_API_KEY=key-f6d80573...

# Send test email
python3 scripts/send_via_mailgun_api.py \
  business@insightpulseai.com \
  "Mailgun API Test" \
  "This email was sent via Mailgun HTTP API (bypassing SMTP port blocking)"
```

**Integrate with Odoo:**

Create custom Odoo module to use Mailgun API instead of SMTP:

```python
# addons/ipai/ipai_mailgun_api/models/ir_mail_server.py
from odoo import models, api
import requests
import logging

_logger = logging.getLogger(__name__)

class MailServer(models.Model):
    _inherit = 'ir.mail_server'

    @api.model
    def send_email_mailgun_api(self, message, mail_server_id=None):
        """Send email via Mailgun HTTP API instead of SMTP."""
        api_key = self.env['ir.config_parameter'].sudo().get_param('mailgun.api_key')
        domain = self.env['ir.config_parameter'].sudo().get_param('mailgun.domain', 'mg.insightpulseai.net')

        if not api_key:
            raise ValueError("Mailgun API key not configured")

        url = f"https://api.mailgun.net/v3/{domain}/messages"

        response = requests.post(
            url,
            auth=("api", api_key),
            data={
                "from": message['From'],
                "to": message['To'],
                "subject": message['Subject'],
                "text": message.get_payload() if not message.is_multipart() else None,
                "html": message.get_payload(i=1) if message.is_multipart() else None
            }
        )

        if response.status_code == 200:
            _logger.info(f"Email sent via Mailgun API: {response.json()['id']}")
            return response.json()['id']
        else:
            _logger.error(f"Mailgun API error: {response.status_code} - {response.text}")
            raise Exception(f"Mailgun API error: {response.text}")
```

---

## Solution 2: Request Port Unblocking (Not Recommended)

### Process

1. **Open Support Ticket** with DigitalOcean
   - Navigate to: https://cloud.digitalocean.com/support/tickets/new
   - Subject: "Request SMTP Port 587 Unblocking"
   - Category: Account & Billing

2. **Provide Information**:
   ```
   I am requesting to unblock outbound SMTP port 587 for my droplet.

   Droplet ID: <droplet-id>
   Droplet IP: 178.128.112.214
   Droplet Name: odoo-erp-prod

   Use Case: Transactional email sending via Mailgun for our Odoo ERP system.

   Email Type: Transactional only (order confirmations, password resets, etc.)
   Expected Volume: < 1000 emails/day

   We have implemented proper SPF, DKIM, and DMARC records for email authentication.
   Domain: mg.insightpulseai.net
   Email Provider: Mailgun

   This is a legitimate business use case and we will comply with all anti-spam policies.
   ```

3. **Wait for Response**: Usually 1-3 business days

### Why Not Recommended

- **Delays**: Can take days for approval
- **Account Age**: New accounts often denied
- **Reputation Risk**: Compromised server could get account banned
- **HTTP API Better**: More features, easier debugging, no port blocking

---

## Solution 3: Alternative Ports (If Supported)

Some email providers support alternative SMTP ports that DigitalOcean doesn't block:

**Mailgun Alternative Ports:**
- **Port 2525**: Alternative submission port (check Mailgun docs)
- **Port 25**: Direct SMTP (blocked by DigitalOcean)
- **Port 587**: STARTTLS submission (blocked by DigitalOcean)
- **Port 465**: SMTP over SSL (blocked by DigitalOcean)

**Test Port 2525:**
```bash
ssh root@178.128.112.214

curl -v --ssl-reqd \
  --url "smtp://smtp.mailgun.org:2525" \
  --user "postmaster@mg.insightpulseai.net:PASSWORD" \
  --mail-from "noreply@mg.insightpulseai.net" \
  --mail-rcpt "test@example.com" \
  --upload-file - << EOF
From: Test <noreply@mg.insightpulseai.net>
To: <test@example.com>
Subject: Port 2525 Test

Testing alternative SMTP port.
EOF
```

If port 2525 works, update Odoo config:
```ini
# /opt/odoo-ce/repo/deploy/odoo.conf
[options]
smtp_port = 2525
```

---

## Solution 4: Relay via Another Server (Not Recommended)

If you have another server without port blocking (e.g., AWS EC2, Vultr, Linode), you could:

1. Set up Postfix relay on that server
2. Configure Odoo to send to relay server
3. Relay server forwards to Mailgun

**Why Not Recommended:**
- Adds complexity and another point of failure
- Requires maintaining another server
- HTTP API is simpler and more reliable

---

## Recommended Implementation Plan

### Phase 1: Test Mailgun HTTP API (Immediate)

```bash
# 1. SSH to production
ssh root@178.128.112.214

# 2. Install requests library
docker exec odoo-prod pip3 install requests

# 3. Create test script
cat > /tmp/test_mailgun_api.py << 'EOF'
import os
import requests

api_key = os.environ.get('MAILGUN_API_KEY', 'key-f6d80573-4c6f8ebe')  # From Mailgun dashboard
domain = 'mg.insightpulseai.net'

response = requests.post(
    f"https://api.mailgun.net/v3/{domain}/messages",
    auth=("api", api_key),
    data={
        "from": "InsightPulse AI <noreply@mg.insightpulseai.net>",
        "to": "business@insightpulseai.com",
        "subject": "Mailgun API Test",
        "text": "This email was sent via Mailgun HTTP API."
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
EOF

# 4. Run test
docker exec odoo-prod python3 /tmp/test_mailgun_api.py
```

### Phase 2: Create Odoo Module (This Week)

1. Create `ipai_mailgun_api` module
2. Override `ir.mail_server.send_email()` to use HTTP API
3. Configure API key in system parameters
4. Test with Finance PPM BIR notifications

### Phase 3: Migrate All Email (Next Week)

1. Update all n8n workflows to use HTTP API
2. Disable SMTP mail server in Odoo
3. Document API approach in runbooks
4. Monitor email delivery in Mailgun dashboard

---

## Current Status

**Completed ✅:**
- DNS records verified and propagating
- Mailgun domain verified in dashboard
- SMTP credentials configured in Odoo
- Root cause identified (port blocking)

**Blocked ⚠️:**
- SMTP sending (port 587 blocked)

**Next Action:**
- Test Mailgun HTTP API (recommended)
- OR request port unblocking from DigitalOcean (not recommended)

---

## References

- [DigitalOcean Email Policy](https://docs.digitalocean.com/support/email-gateway-policy/)
- [Mailgun API Documentation](https://documentation.mailgun.com/docs/mailgun/api-reference/openapi-final/tag/Messages/)
- [Mailgun API Quick Start](https://documentation.mailgun.com/docs/mailgun/quickstart-guide/)
- [DigitalOcean SMTP Port Unblock Request](https://docs.digitalocean.com/support/how-to-contact-support/)

---

*Last updated: 2026-01-13*
*Status: Investigation complete, API solution recommended*
