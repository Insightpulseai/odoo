# Mailgun Domain Verification Runbook

## Overview

This runbook covers the operational steps to verify a domain with Mailgun for email sending from Odoo.

---

## Prerequisites

- Mailgun account with API access
- DNS management access for your domain
- Environment variables configured (NOT in repo):
  - `MAILGUN_API_KEY`
  - `MAILGUN_DOMAIN`

---

## 1. Add Domain in Mailgun

### 1.1 Via Dashboard

1. Log in to [Mailgun Dashboard](https://app.mailgun.com)
2. Navigate to **Sending** > **Domains**
3. Click **Add New Domain**
4. Enter your domain (e.g., `mail.insightpulseai.net`)
5. Select region (US or EU)

### 1.2 Via API

```bash
curl -s --user "api:${MAILGUN_API_KEY}" \
  https://api.mailgun.net/v4/domains \
  -F name="${MAILGUN_DOMAIN}"
```

---

## 2. Configure DNS Records

Mailgun will provide DNS records to add. Required records:

### 2.1 SPF Record

```
Type: TXT
Host: @
Value: v=spf1 include:mailgun.org ~all
```

### 2.2 DKIM Records

```
Type: TXT
Host: smtp._domainkey
Value: (provided by Mailgun - long string)
```

### 2.3 MX Records (for receiving)

```
Type: MX
Host: @
Priority: 10
Value: mxa.mailgun.org

Type: MX
Host: @
Priority: 10
Value: mxb.mailgun.org
```

### 2.4 CNAME for Tracking (optional)

```
Type: CNAME
Host: email
Value: mailgun.org
```

---

## 3. Verify DNS Propagation

### 3.1 Check SPF

```bash
dig +short TXT ${MAILGUN_DOMAIN} | grep spf
```

### 3.2 Check DKIM

```bash
dig +short TXT smtp._domainkey.${MAILGUN_DOMAIN}
```

### 3.3 Check MX

```bash
dig +short MX ${MAILGUN_DOMAIN}
```

---

## 4. Verify Domain in Mailgun

### 4.1 Via Dashboard

1. Go to **Sending** > **Domains** > Your Domain
2. Click **Verify DNS Settings**
3. All checks should show green

### 4.2 Via API

```bash
curl -s --user "api:${MAILGUN_API_KEY}" \
  "https://api.mailgun.net/v4/domains/${MAILGUN_DOMAIN}/verify" \
  -X PUT
```

---

## 5. Configure Odoo

### 5.1 System Parameters

Set in Odoo via Settings > Technical > Parameters > System Parameters:

| Key | Value |
|-----|-------|
| `mail.catchall.domain` | `insightpulseai.net` |
| `mail.default.from` | `notifications@insightpulseai.net` |

### 5.2 Outgoing Mail Server

Configure via Settings > Technical > Outgoing Mail Servers:

| Field | Value |
|-------|-------|
| Description | Mailgun SMTP |
| SMTP Server | `smtp.mailgun.org` |
| SMTP Port | `587` |
| Connection Security | TLS (STARTTLS) |
| Username | `postmaster@${MAILGUN_DOMAIN}` |
| Password | (from Mailgun SMTP credentials) |

---

## 6. Test Email Sending

### 6.1 Via Mailgun API

```bash
curl -s --user "api:${MAILGUN_API_KEY}" \
  "https://api.mailgun.net/v3/${MAILGUN_DOMAIN}/messages" \
  -F from="Test <postmaster@${MAILGUN_DOMAIN}>" \
  -F to="test@example.com" \
  -F subject="Mailgun Test" \
  -F text="Domain verification successful"
```

### 6.2 Via Odoo

1. Go to Settings > Technical > Outgoing Mail Servers
2. Click **Test Connection** on the Mailgun server
3. Send a test email from any record with chatter

---

## 7. Verification Checklist

- [ ] Domain added in Mailgun
- [ ] SPF record configured and verified
- [ ] DKIM record configured and verified
- [ ] MX records configured (if receiving)
- [ ] Domain status shows "Verified" in Mailgun
- [ ] Odoo outgoing mail server configured
- [ ] Test email sent successfully

---

## 8. Troubleshooting

### DNS Not Propagating

- Wait up to 48 hours for propagation
- Use `dig` to check current DNS state
- Verify with multiple DNS servers: `dig @8.8.8.8 TXT ${MAILGUN_DOMAIN}`

### DKIM Verification Fails

- Ensure the full DKIM value is copied (often truncated)
- Some DNS providers have character limits - may need to split record

### Emails Going to Spam

- Ensure SPF and DKIM are both verified
- Add DMARC record for better reputation
- Warm up domain gradually (don't send bulk immediately)

---

## 9. Security Notes

- NEVER commit `MAILGUN_API_KEY` to repo
- Use environment variables or secrets manager
- Rotate API keys periodically
- Use domain-level keys instead of account-level when possible

---

*Last updated: 2026-01-08*
