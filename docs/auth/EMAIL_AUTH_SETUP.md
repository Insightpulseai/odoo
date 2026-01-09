# Email Authentication Setup Guide

Complete guide for configuring email authentication with Mailgun, Supabase Auth, and Odoo.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Email Flow Architecture                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Supabase Auth (Magic Links) ──────> Mailgun SMTP          │
│       │                                    │                 │
│       │                                    │                 │
│       ├──> Custom Access Token Hook        │                 │
│       │    (JWT Claims: tenant_id, role)   │                 │
│       │                                    │                 │
│       └──> Redirect URLs (configured)      │                 │
│            • http://localhost:3000/*       │                 │
│            • https://superset.insightpulseai.net/*          │
│            • https://erp.insightpulseai.net/*               │
│                                            │                 │
│  Odoo (Transactional Email) ──────────────┘                 │
│       • Approval notifications                              │
│       • Task assignments                                    │
│       • System alerts                                       │
│                                                              │
│  n8n (Workflow Email) ──────────> Mailgun SMTP             │
│       • BIR deadline alerts                                 │
│       • Month-end close reminders                           │
│       • Multi-agency notifications                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## DNS Configuration for Mailgun

**Domain:** `mg.insightpulseai.net`
**DNS Provider:** Entri (uses relative host names)

### Required DNS Records (Entri Format)

| Host | Type | Priority | TTL | Data |
|------|------|----------|-----|------|
| `mg` | MX | 10 | 3600 | `mxa.mailgun.org` |
| `mg` | MX | 10 | 3600 | `mxb.mailgun.org` |
| `mg` | TXT | - | 3600 | `v=spf1 include:mailgun.org ~all` |
| `pic._domainkey.mg` | TXT | - | 3600 | `v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDcYB3DG10ylI4z6PWaiwyiByMrjwr9kfgJK8ccsZYT4guxi8+Emyf/nUs7IqR/LTZwwymeTZDaS/vQ6pjDhIaF2J9M9XsdgP+nv3wx99BqQ7dA+aa5sNwJKI3WRhr1YMK6IJQJIWSLERPBr74eMBAVa/Zmrfui1BOCgUFvQN9GBQIDAQAB` |
| `email.mg` | CNAME | - | 3600 | `mailgun.org` |
| `_dmarc.mg` | TXT | - | 3600 | `v=DMARC1; p=quarantine; rua=mailto:postmaster@mg.insightpulseai.net; pct=100; fo=1` |

### Record Details

#### MX Records (Inbound Mail Routing)
**Purpose:** Route incoming email to Mailgun servers

```dns
Host: mg
Type: MX
Priority: 10
Data: mxa.mailgun.org

Host: mg
Type: MX
Priority: 10
Data: mxb.mailgun.org
```

**Note:** Both MX records have priority 10 for round-robin load balancing.

#### SPF Record (Sender Policy Framework)
**Purpose:** Authorize Mailgun to send email on behalf of `mg.insightpulseai.net`

```dns
Host: mg
Type: TXT
Data: v=spf1 include:mailgun.org ~all
```

**Verification:**
```bash
dig +short TXT mg.insightpulseai.net
# Expected: "v=spf1 include:mailgun.org ~all"
```

#### DKIM Record (DomainKeys Identified Mail)
**Purpose:** Cryptographic signature proving email authenticity

```dns
Host: pic._domainkey.mg
Type: TXT
Data: v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDcYB3DG10ylI4z6PWaiwyiByMrjwr9kfgJK8ccsZYT4guxi8+Emyf/nUs7IqR/LTZwwymeTZDaS/vQ6pjDhIaF2J9M9XsdgP+nv3wx99BqQ7dA+aa5sNwJKI3WRhr1YMK6IJQJIWSLERPBr74eMBAVa/Zmrfui1BOCgUFvQN9GBQIDAQAB
```

**Key Components:**
- `v=DKIM1` - DKIM version
- `k=rsa` - RSA key type
- `p=...` - Public key (base64 encoded)

**Verification:**
```bash
dig +short TXT pic._domainkey.mg.insightpulseai.net
# Expected: "v=DKIM1; k=rsa; p=MIGf..."
```

**Critical:** The `v=DKIM1;` prefix is **required**. Older configurations may have only `k=rsa; p=...` which will fail validation.

#### Tracking CNAME (Click/Open Tracking)
**Purpose:** Enable email click and open tracking

```dns
Host: email.mg
Type: CNAME
Data: mailgun.org
```

**Verification:**
```bash
dig +short CNAME email.mg.insightpulseai.net
# Expected: mailgun.org.
```

#### DMARC Record (Email Authentication Policy)
**Purpose:** Instruct receiving servers how to handle authentication failures

```dns
Host: _dmarc.mg
Type: TXT
Data: v=DMARC1; p=quarantine; rua=mailto:postmaster@mg.insightpulseai.net; pct=100; fo=1
```

**Policy Breakdown:**
- `v=DMARC1` - DMARC version
- `p=quarantine` - Quarantine emails that fail authentication (safer than `reject` during initial setup)
- `rua=mailto:postmaster@mg.insightpulseai.net` - Send aggregate reports here
- `pct=100` - Apply policy to 100% of messages
- `fo=1` - Generate forensic reports on any authentication failure

**Verification:**
```bash
dig +short TXT _dmarc.mg.insightpulseai.net
# Expected: "v=DMARC1; p=quarantine; rua=mailto:postmaster@mg.insightpulseai.net; pct=100; fo=1"
```

**Policy Progression:**
1. **Initial (Testing):** `p=none` - Monitor only, no enforcement
2. **Intermediate:** `p=quarantine` - Send failing emails to spam
3. **Production:** `p=reject` - Reject failing emails entirely

### DNS Propagation Verification

**Complete Verification Script:**
```bash
#!/bin/bash
DOMAIN="mg.insightpulseai.net"

echo "=== MX Records ==="
dig +short MX $DOMAIN

echo -e "\n=== SPF Record ==="
dig +short TXT $DOMAIN

echo -e "\n=== DKIM Record ==="
dig +short TXT pic._domainkey.$DOMAIN

echo -e "\n=== Tracking CNAME ==="
dig +short CNAME email.$DOMAIN

echo -e "\n=== DMARC Record ==="
dig +short TXT _dmarc.$DOMAIN
```

**Expected Output:**
```
=== MX Records ===
10 mxa.mailgun.org.
10 mxb.mailgun.org.

=== SPF Record ===
"v=spf1 include:mailgun.org ~all"

=== DKIM Record ===
"v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDcYB3DG10ylI4z6PWaiwyiByMrjwr9kfgJK8ccsZYT4guxi8+Emyf/nUs7IqR/LTZwwymeTZDaS/vQ6pjDhIaF2J9M9XsdgP+nv3wx99BqQ7dA+aa5sNwJKI3WRhr1YMK6IJQJIWSLERPBr74eMBAVa/Zmrfui1BOCgUFvQN9GBQIDAQAB"

=== Tracking CNAME ===
mailgun.org.

=== DMARC Record ===
"v=DMARC1; p=quarantine; rua=mailto:postmaster@mg.insightpulseai.net; pct=100; fo=1"
```

---

## Supabase Auth Configuration

### SMTP Settings (Mailgun)

**Navigate to:** Supabase Dashboard → Project Settings → Auth → Email Auth

**Settings:**
```
Enable Email Provider: ✓ Enabled
SMTP Host: smtp.mailgun.org
SMTP Port: 2525
SMTP User: postmaster@mg.insightpulseai.net
SMTP Password: [Mailgun SMTP password from dashboard]
Sender Email: noreply@mg.insightpulseai.net
Sender Name: InsightPulse AI
```

**Why Port 2525?**
DigitalOcean blocks standard SMTP ports (25, 465, 587) but allows 2525 as an alternative submission port.

### Redirect URL Configuration

**Navigate to:** Supabase Dashboard → Authentication → URL Configuration

**Site URL:**
```
https://superset.insightpulseai.net
```

**Redirect URLs (whitelist):**
```
http://localhost:3000/*
https://superset.insightpulseai.net/*
https://erp.insightpulseai.net/*
https://auth.insightpulseai.net/*
```

**Wildcards Explained:**
- `/*` matches any path and query parameters
- Required for magic link redirects (e.g., `/login/?next=/superset/welcome/`)

### Custom Access Token Hook

**Navigate to:** Supabase Dashboard → Authentication → Hooks

**Hook Type:** Custom Access Token
**Status:** ✓ Enabled
**Function:** `public.custom_access_token_hook`

**Verification (SQL):**
```sql
-- Check hook function exists
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
  AND routine_name = 'custom_access_token_hook';

-- Expected: 1 row with routine_type = 'FUNCTION'

-- Test hook with sample user
SELECT public.custom_access_token_hook(
  jsonb_build_object(
    'user_id', 'f0304ff6-60bd-439e-be9c-ea36c29a3464',
    'claims', '{}'::jsonb
  )
);

-- Expected: JSON with tenant_id, role, tenant_slug, display_name
```

### Email Templates (Optional Customization)

**Default Templates:**
- Magic Link: `Confirm your email address`
- Invite: `You have been invited`
- Recovery: `Reset your password`

**Template Variables:**
- `{{ .ConfirmationURL }}` - Magic link URL
- `{{ .SiteURL }}` - Configured site URL
- `{{ .Token }}` - One-time token
- `{{ .TokenHash }}` - Hashed token

**Customization Location:** Supabase Dashboard → Authentication → Email Templates

---

## Odoo SMTP Configuration

### Environment Variables

**File:** `/Users/tbwa/odoo-ce/.env.local` (or deployed environment)

```bash
# Mailgun SMTP Configuration
MAIL_HOST=smtp.mailgun.org
MAIL_PORT=2525
MAIL_USER=postmaster@mg.insightpulseai.net
MAIL_PASSWORD=your_mailgun_smtp_password_here
MAIL_ENCRYPTION=none  # Port 2525 uses STARTTLS automatically
MAIL_DEFAULT_FROM=noreply@mg.insightpulseai.net
MAIL_CATCHALL_DOMAIN=mg.insightpulseai.net
MAIL_FORCE_SMTP_FROM=true

# Odoo Base URL (for email links)
ODOO_BASE_URL=https://erp.insightpulseai.net
```

### Odoo Configuration Script

**Script:** `scripts/configure_mailgun_smtp.py`

```python
#!/usr/bin/env python3
"""Configure Mailgun SMTP for Odoo"""
import os
from odoo import api, SUPERUSER_ID

MAIL_HOST = os.getenv('MAIL_HOST', 'smtp.mailgun.org')
MAIL_PORT = int(os.getenv('MAIL_PORT', '2525'))
MAIL_USER = os.getenv('MAIL_USER', 'postmaster@mg.insightpulseai.net')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_FROM = os.getenv('MAIL_DEFAULT_FROM', 'noreply@mg.insightpulseai.net')

if not MAIL_PASSWORD:
    raise ValueError("MAIL_PASSWORD environment variable is required")

with api.Environment.manage():
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Create/update mail server
    MailServer = env['ir.mail_server']
    server = MailServer.search([('name', '=', 'Mailgun')], limit=1)

    values = {
        'name': 'Mailgun',
        'smtp_host': MAIL_HOST,
        'smtp_port': MAIL_PORT,
        'smtp_user': MAIL_USER,
        'smtp_pass': MAIL_PASSWORD,
        'smtp_encryption': 'none',  # STARTTLS on port 2525
        'from_filter': MAIL_DEFAULT_FROM,
        'sequence': 10,
        'active': True,
    }

    if server:
        server.write(values)
        print(f"✓ Updated Mailgun SMTP server: {server.id}")
    else:
        server = MailServer.create(values)
        print(f"✓ Created Mailgun SMTP server: {server.id}")

    # Set system parameters
    env['ir.config_parameter'].set_param('mail.catchall.domain', MAIL_DEFAULT_FROM)
    env['ir.config_parameter'].set_param('mail.default.from', MAIL_DEFAULT_FROM)

    # Test connection
    try:
        server.test_smtp_connection()
        print("✓ SMTP connection test successful")
    except Exception as e:
        print(f"✗ SMTP connection test failed: {e}")

    env.cr.commit()
```

**Execution:**
```bash
docker exec -i odoo-core odoo shell -d odoo_core < scripts/configure_mailgun_smtp.py
```

### Set Odoo Base URL (Idempotent)

**Script:** `scripts/set_odoo_base_url.py`

```python
#!/usr/bin/env python3
"""Set Odoo base URL for correct email link generation"""
import os
from odoo import api, SUPERUSER_ID

BASE_URL = os.getenv('ODOO_BASE_URL', 'https://erp.insightpulseai.net')

with api.Environment.manage():
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Get or create web.base.url parameter
    param = env['ir.config_parameter'].get_param('web.base.url')

    if param != BASE_URL:
        env['ir.config_parameter'].set_param('web.base.url', BASE_URL)
        print(f"✓ Updated web.base.url: {BASE_URL}")
    else:
        print(f"✓ web.base.url already correct: {BASE_URL}")

    # Ensure web.base.url.freeze is set (prevents override)
    freeze = env['ir.config_parameter'].get_param('web.base.url.freeze', 'False')
    if freeze != 'True':
        env['ir.config_parameter'].set_param('web.base.url.freeze', 'True')
        print("✓ Froze web.base.url to prevent override")
    else:
        print("✓ web.base.url already frozen")

    env.cr.commit()
```

**Verification:**
```sql
SELECT key, value
FROM ir_config_parameter
WHERE key IN ('web.base.url', 'web.base.url.freeze', 'mail.default.from');
```

---

## n8n Email Configuration

**n8n uses Mailgun API, not SMTP** (more reliable for workflow automation)

### Environment Variables

```bash
MAILGUN_API_KEY=your_mailgun_api_key_here
MAILGUN_DOMAIN=mg.insightpulseai.net
MAILGUN_API_BASE_URL=https://api.mailgun.net/v3
```

### n8n Workflow Email Node Configuration

```json
{
  "parameters": {
    "resource": "email",
    "operation": "send",
    "fromEmail": "noreply@mg.insightpulseai.net",
    "toEmail": "={{ $json.recipient_email }}",
    "subject": "={{ $json.subject }}",
    "text": "={{ $json.body_text }}",
    "html": "={{ $json.body_html }}",
    "options": {
      "tags": ["n8n", "workflow", "automation"]
    }
  },
  "type": "n8n-nodes-base.mailgun",
  "typeVersion": 1.1
}
```

---

## Email Deliverability Best Practices

### Sender Reputation

1. **Warm-up Period:** Gradually increase sending volume over 2-4 weeks
2. **Monitor Bounce Rate:** Keep below 5%
3. **Monitor Complaint Rate:** Keep below 0.1%
4. **List Hygiene:** Remove bounced/unsubscribed addresses immediately

### Email Content

1. **SPF/DKIM Alignment:** Always send from `@mg.insightpulseai.net`
2. **Include Unsubscribe Link:** Required for transactional emails
3. **Text + HTML Versions:** Provide both for compatibility
4. **Avoid Spam Triggers:** No ALL CAPS, excessive exclamation marks, misleading subjects

### Monitoring

**Mailgun Dashboard Metrics:**
- Delivered: Should be >95%
- Opens: Varies by email type
- Clicks: Varies by email type
- Bounces: Should be <5%
- Complaints: Should be <0.1%

**DMARC Reports:**
- Configure `rua=mailto:postmaster@mg.insightpulseai.net`
- Review daily for authentication failures
- Investigate any SPF/DKIM failures immediately

---

## Troubleshooting

### Common Issues

**1. "550 5.7.1 Unauthenticated email from domain not accepted"**

**Cause:** SPF record missing or incorrect
**Fix:** Verify SPF record with `dig +short TXT mg.insightpulseai.net`

**2. "DKIM signature verification failed"**

**Cause:** DKIM record missing `v=DKIM1;` prefix
**Fix:** Update TXT record to include full value: `v=DKIM1; k=rsa; p=...`

**3. "Message rejected due to DMARC policy"**

**Cause:** DMARC policy too strict (`p=reject`) before SPF/DKIM aligned
**Fix:** Start with `p=none`, then `p=quarantine`, finally `p=reject`

**4. Supabase magic link shows "FUNCTION_INVOCATION_FAILED"**

**Cause:** Redirect URL not in whitelist
**Fix:** Add URL to Supabase Dashboard → Authentication → URL Configuration

**5. Odoo emails not sending**

**Cause:** SMTP credentials incorrect or port blocked
**Fix:**
- Verify `MAIL_PASSWORD` is correct Mailgun SMTP password (not API key)
- Use port 2525 (not 25, 465, 587)
- Test with `scripts/configure_mailgun_smtp.py`

### Verification Checklist

**DNS Configuration:**
- [ ] MX records resolve to `mxa.mailgun.org` and `mxb.mailgun.org`
- [ ] SPF record contains `v=spf1 include:mailgun.org ~all`
- [ ] DKIM record contains full value with `v=DKIM1;` prefix
- [ ] Tracking CNAME resolves to `mailgun.org`
- [ ] DMARC record exists at `_dmarc.mg.insightpulseai.net`

**Supabase Auth:**
- [ ] SMTP configured with port 2525
- [ ] Redirect URLs include all required domains
- [ ] Custom Access Token Hook enabled
- [ ] Test magic link sends successfully

**Odoo Configuration:**
- [ ] `ir.mail_server` record exists for Mailgun
- [ ] `web.base.url` set to `https://erp.insightpulseai.net`
- [ ] `web.base.url.freeze` is `True`
- [ ] Test email sends successfully

**n8n Configuration:**
- [ ] Mailgun API key configured
- [ ] Test workflow email sends successfully

---

## Security Considerations

### Secrets Management

**Never commit these to git:**
- `MAIL_PASSWORD` (Mailgun SMTP password)
- `MAILGUN_API_KEY` (Mailgun API key)
- `SUPABASE_SERVICE_ROLE_KEY` (Supabase admin key)

**Secure storage:**
- Local: `.env.local` (gitignored)
- Production: DigitalOcean App Platform environment variables
- CI/CD: GitHub Secrets

### Access Control

**Mailgun Dashboard:**
- Enable 2FA
- Use separate SMTP credentials per service (Odoo, Supabase, n8n)
- Rotate credentials quarterly

**Supabase Dashboard:**
- Enable 2FA
- Use service role key only in server-side code
- Never expose in frontend/browser

**Odoo:**
- Restrict `ir.mail_server` access to admin users only
- Enable audit logging for email sends
- Monitor for suspicious email patterns

---

## References

- [Mailgun Documentation](https://documentation.mailgun.com/)
- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [Odoo Email Configuration](https://www.odoo.com/documentation/18.0/applications/general/email_communication.html)
- [DMARC.org](https://dmarc.org/)
- [SPF Record Syntax](http://www.open-spf.org/SPF_Record_Syntax/)
- [DKIM Core](https://datatracker.ietf.org/doc/html/rfc6376)

---

**Last Updated:** 2026-01-09
**Maintainer:** DevOps Team
**Related Docs:** `AUTH_MODEL.md`, `MAGIC_LINK_500_ERROR.md`
