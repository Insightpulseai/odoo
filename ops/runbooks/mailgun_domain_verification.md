# Mailgun Domain Verification Runbook

**Purpose:** Configure and verify Mailgun domain for production email delivery from Odoo.

**Prerequisites:**
- Mailgun account with API access
- DNS management access for your domain
- Production Odoo instance configured

---

## 1. Overview

Mailgun requires domain verification to:
- Send email from your domain
- Enable open/click tracking
- Improve deliverability (SPF/DKIM authentication)

**Reference:** [Mailgun Domain Verification Setup Guide](https://help.mailgun.com/hc/en-us/articles/32884702360603-Domain-Verification-Setup-Guide)

---

## 2. Step-by-Step Setup

### Step 1: Add Domain in Mailgun

1. Log in to Mailgun Control Panel
2. Navigate to **Sending** → **Domains**
3. Click **Add New Domain**
4. Enter your domain:
   - **Recommended:** Use a subdomain (e.g., `mail.yourdomain.com`)
   - Subdomains improve deliverability and isolate sending reputation
5. Click **Add Domain**
6. Keep the DNS records page open

### Step 2: Add DNS Records

Mailgun will display the required DNS records. Add them at your DNS provider:

#### TXT Records (SPF + DKIM)

**SPF Record:**
```
Type: TXT
Host: mail (or your subdomain)
Value: v=spf1 include:mailgun.org ~all
```

**Important:** If an SPF record already exists for the root domain:
- Do NOT add a second SPF record
- Instead, merge by adding `include:mailgun.org` to the existing record
- Example: `v=spf1 include:_spf.google.com include:mailgun.org ~all`

**DKIM Record:**
```
Type: TXT
Host: mx._domainkey.mail (Mailgun provides exact host)
Value: (Mailgun provides the DKIM key value)
```

#### MX Records (2 records)

```
Type: MX
Host: mail (or your subdomain)
Priority: 10
Value: mxa.mailgun.org

Type: MX
Host: mail (or your subdomain)
Priority: 10
Value: mxb.mailgun.org
```

#### CNAME Record (Tracking)

```
Type: CNAME
Host: email.mail (Mailgun provides exact host)
Value: mailgun.org
```

### Step 3: Verify DNS Propagation

1. Wait for DNS propagation (can take 24-48 hours)
2. In Mailgun, click **"Check DNS Records Now"**
3. All records should show green checkmarks

---

## 3. Verification Commands

Run these commands to verify DNS configuration:

```bash
#!/usr/bin/env bash
# Mailgun DNS Verification Script

DOMAIN="${1:-mail.yourdomain.com}"

echo "=== Mailgun DNS Verification for $DOMAIN ==="
echo ""

echo "--- SPF Record ---"
dig +short TXT "$DOMAIN" | tr -d '"' | grep -E "v=spf1.*mailgun"
echo ""

echo "--- DKIM Record ---"
dig +short TXT "mx._domainkey.$DOMAIN" | tr -d '"'
echo ""

echo "--- MX Records ---"
dig +short MX "$DOMAIN"
echo ""

echo "--- CNAME (Tracking) ---"
dig +short CNAME "email.$DOMAIN"
echo ""

echo "=== End Verification ==="
```

**Expected Output:**
```
--- SPF Record ---
v=spf1 include:mailgun.org ~all

--- DKIM Record ---
k=rsa; p=MIGfMA0GCSqGSI...

--- MX Records ---
10 mxa.mailgun.org.
10 mxb.mailgun.org.

--- CNAME (Tracking) ---
mailgun.org.
```

---

## 4. Odoo Configuration

### System Parameters

Set these in Odoo (Settings → Technical → System Parameters):

| Key | Value |
|-----|-------|
| `mail.catchall.domain` | `mail.yourdomain.com` |
| `mail.default.from` | `notifications@mail.yourdomain.com` |

### Outgoing Mail Server

Configure in Settings → Technical → Outgoing Mail Servers:

| Field | Value |
|-------|-------|
| Description | Mailgun SMTP |
| SMTP Server | `smtp.mailgun.org` |
| SMTP Port | `587` |
| Connection Security | TLS (STARTTLS) |
| Username | `postmaster@mail.yourdomain.com` |
| Password | (Mailgun SMTP password) |

### Test Email

1. Go to Settings → Technical → Outgoing Mail Servers
2. Click **Test Connection**
3. Send a test email from Odoo

---

## 5. Monitoring

### Mailgun Dashboard

Monitor these metrics in Mailgun:
- Delivered rate
- Bounce rate
- Spam complaints
- Opens/clicks (if tracking enabled)

### Log Commands

```bash
# Check Odoo mail queue
docker exec odoo-core odoo-bin shell -d odoo --no-http <<'EOF'
failed = env['mail.mail'].search([('state', '=', 'exception')])
print(f"Failed emails: {len(failed)}")
for mail in failed[:5]:
    print(f"  - {mail.id}: {mail.failure_reason}")
EOF

# Check Mailgun API (requires API key)
curl -s --user "api:YOUR_API_KEY" \
  "https://api.mailgun.net/v3/mail.yourdomain.com/events?limit=10" | jq .
```

---

## 6. Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| SPF fails | Multiple SPF records | Merge into single record |
| DKIM fails | Wrong TXT host | Use exact host from Mailgun |
| MX fails | Missing priority | Ensure priority is set to 10 |
| Emails in spam | No DKIM/SPF | Verify all DNS records |
| Tracking not working | Missing CNAME | Add tracking CNAME record |

### DNS Propagation Check

```bash
# Check if DNS has propagated globally
dig @8.8.8.8 +short TXT mail.yourdomain.com
dig @1.1.1.1 +short TXT mail.yourdomain.com
```

---

## 7. Checklist

- [ ] Domain added in Mailgun
- [ ] SPF TXT record added (or merged)
- [ ] DKIM TXT record added
- [ ] MX records added (both mxa and mxb)
- [ ] CNAME tracking record added
- [ ] DNS propagation complete (all green in Mailgun)
- [ ] Odoo outgoing mail server configured
- [ ] Test email sent successfully
- [ ] Production email verified

---

*Last updated: 2026-01-08*
