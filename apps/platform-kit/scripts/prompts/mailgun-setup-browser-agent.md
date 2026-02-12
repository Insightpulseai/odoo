# Claude Browser Agent: Complete Mailgun Dashboard Setup

## Objective
Configure Mailgun dashboard to add and verify the domain `mg.insightpulseai.com` for transactional email sending with Odoo 19.

## Prerequisites
- Logged into Mailgun dashboard at https://app.mailgun.com
- Access to DNS provider for insightpulseai.com

---

## Task 1: Add New Sending Domain

1. Navigate to **Sending** → **Domains** in the left sidebar
2. Click **"Add New Domain"** button
3. Enter domain: `mg.insightpulseai.com`
4. Select region: **US** (recommended for lower latency)
5. Click **"Add Domain"**

**Expected Result**: Domain added in "Unverified" state with DNS records displayed.

---

## Task 2: Copy DNS Records

After adding the domain, Mailgun will display required DNS records. Copy these exact values:

### SPF Record
- **Type**: TXT
- **Host**: `mg`
- **Value**: `v=spf1 include:mailgun.org ~all`

### DKIM Records (2 records)
- **Type**: TXT
- **Host**: `smtp._domainkey.mg`
- **Value**: Copy the full `k=rsa; p=...` value from Mailgun

- **Type**: TXT
- **Host**: `krs._domainkey.mg` (or similar - check exact hostname)
- **Value**: Copy the full `k=rsa; p=...` value from Mailgun

### MX Records (for inbound routing/webhooks)
- **Type**: MX
- **Host**: `mg`
- **Priority**: 10
- **Value**: `mxa.mailgun.org`

- **Type**: MX
- **Host**: `mg`
- **Priority**: 10
- **Value**: `mxb.mailgun.org`

### Tracking CNAME (Optional)
- **Type**: CNAME
- **Host**: `email.mg`
- **Value**: `mailgun.org`

**Action**: Save all these values - they need to be added to DNS.

---

## Task 3: Add DNS Records

Navigate to your DNS provider (DigitalOcean, Cloudflare, Namecheap, etc.) and add all records from Task 2.

For DigitalOcean DNS:
1. Go to Networking → Domains → insightpulseai.com
2. Add each record with exact values from Mailgun

---

## Task 4: Verify Domain in Mailgun

1. Return to Mailgun dashboard → Sending → Domains
2. Click on `mg.insightpulseai.com`
3. Click **"Verify DNS Settings"** or **"Check DNS Records Now"**
4. Wait for verification (may take 5-60 minutes for DNS propagation)

**Expected Result**: All checks should show green checkmarks:
- ✓ SPF Record
- ✓ DKIM Record(s)
- ✓ MX Records
- Domain state changes to **"Active"**

---

## Task 5: Configure SMTP Credentials

1. In Mailgun, go to **Sending** → **Domain Settings** → **SMTP Credentials**
2. Default user is `postmaster@mg.insightpulseai.com`
3. Click **"Reset Password"** or **"Add New SMTP User"**
4. Generate and copy the SMTP password securely

**SMTP Settings to Save**:
```
SMTP Server: smtp.mailgun.org
Port: 587 (TLS) or 465 (SSL)
Username: postmaster@mg.insightpulseai.com
Password: <generated_password>
```

---

## Task 6: Configure Webhooks (Optional but Recommended)

1. Go to **Sending** → **Webhooks**
2. Click **"Add Webhook"** for each event type:

| Event | Webhook URL |
|-------|-------------|
| Delivered | `https://erp.insightpulseai.com/mailgun/webhook/delivered` |
| Opened | `https://erp.insightpulseai.com/mailgun/webhook/opened` |
| Clicked | `https://erp.insightpulseai.com/mailgun/webhook/clicked` |
| Permanent Failure | `https://erp.insightpulseai.com/mailgun/webhook/bounced` |
| Complained | `https://erp.insightpulseai.com/mailgun/webhook/complained` |
| Unsubscribed | `https://erp.insightpulseai.com/mailgun/webhook/unsubscribed` |

3. Copy the **Webhook Signing Key** from Settings → Security → Webhook signing key

---

## Task 7: Get API Key

1. Go to **Settings** → **API Security** (or API Keys)
2. Copy the **Private API Key** (starts with `key-`)
3. Store securely - needed for programmatic access

---

## Task 8: Configure Sending Settings

1. Go to **Sending** → **Domain Settings**
2. Configure:
   - **Open Tracking**: Enable
   - **Click Tracking**: Enable
   - **Unsubscribe Tracking**: Enable (for marketing emails)
   - **DKIM**: Verify enabled
   - **Dedicated IP**: Optional (for high volume)

---

## Task 9: Send Test Email

1. Go to **Sending** → **Overview** or use API playground
2. Send test email:
   - **From**: `test@mg.insightpulseai.com`
   - **To**: Your email address
   - **Subject**: `Mailgun Configuration Test`
   - **Body**: `Testing mg.insightpulseai.com domain setup`
3. Click **"Send"**
4. Verify email is received

---

## Final Verification Checklist

After completing all tasks, verify:

- [ ] Domain `mg.insightpulseai.com` shows as **Active** (green)
- [ ] All DNS records verified (SPF ✓, DKIM ✓, MX ✓)
- [ ] SMTP credentials generated and saved
- [ ] Test email received successfully
- [ ] Webhooks configured (if using)
- [ ] API key copied securely

---

## Credentials to Save

After setup, save these values to `.env.local`:

```bash
# Mailgun Configuration
MAILGUN_DOMAIN=mg.insightpulseai.com
MAILGUN_API_KEY=key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MAILGUN_SMTP_LOGIN=postmaster@mg.insightpulseai.com
MAILGUN_SMTP_PASSWORD=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MAILGUN_WEBHOOK_SIGNING_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Odoo SMTP Settings
ODOO_SMTP_HOST=smtp.mailgun.org
ODOO_SMTP_PORT=587
ODOO_SMTP_USER=postmaster@mg.insightpulseai.com
ODOO_SMTP_PASSWORD=${MAILGUN_SMTP_PASSWORD}
ODOO_SMTP_ENCRYPTION=starttls
```

---

## Deprecate Old Domain (After Verification)

Once `mg.insightpulseai.com` is working:

1. Go to **Sending** → **Domains**
2. Find `mg.insightpulseai.net` (old domain)
3. Click domain → **Settings** → **Delete Domain** (or just leave inactive)
4. Remove old DNS records for `.net` subdomain

---

## Troubleshooting

**DNS not verifying?**
- Wait 15-60 minutes for propagation
- Use `dig TXT mg.insightpulseai.com` to check records
- Ensure no typos in DNS values

**SMTP connection refused?**
- Check port 587 not blocked by firewall
- Try port 465 (SSL) as alternative
- Verify credentials are correct

**Test email not received?**
- Check spam folder
- Verify domain is "Active" status
- Check Mailgun logs for delivery status
