# Zoho Workplace DNS Configuration for insightpulseai.com

**Domain**: insightpulseai.com (not .net)
**Email**: business@insightpulseai.com
**Zoho Workplace Account**: Active

---

## Required DNS Records

Add these records to your DNS provider (DigitalOcean, Cloudflare, etc.):

### MX Records (Mail Routing)

| Host | Type | Priority | Value | TTL |
|------|------|----------|-------|-----|
| `@` | MX | 10 | `mx.zoho.com` | 1 hour |
| `@` | MX | 20 | `mx2.zoho.com` | 1 hour |
| `@` | MX | 50 | `mx3.zoho.com` | 1 hour |

**Note**: `@` means root domain (insightpulseai.com)

---

### SPF Record (Prevent Email Spoofing)

| Host | Type | Value | TTL |
|------|------|-------|-----|
| `@` | TXT | `v=spf1 include:zoho.com ~all` | 1 hour |

**Explanation**: This tells receiving mail servers that Zoho is authorized to send email on behalf of insightpulseai.com.

---

### DKIM Record (Email Signing)

**Get from Zoho Admin Console**:
1. Login to: https://www.zoho.com/workplace/
2. Go to: Control Panel → Email Configuration → Domain Keys (DKIM)
3. Click "Add Selector" or view existing DKIM record
4. Copy the generated TXT record

**Example format** (actual values will differ):

| Host | Type | Value | TTL |
|------|------|-------|-----|
| `zmail._domainkey` | TXT | `v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4...` | 1 hour |

---

### DMARC Record (Email Policy)

| Host | Type | Value | TTL |
|------|------|-------|-----|
| `_dmarc` | TXT | `v=DMARC1; p=quarantine; rua=mailto:business@insightpulseai.com` | 1 hour |

**Explanation**:
- `p=quarantine`: Suspicious emails go to spam (not rejected)
- `rua=mailto:business@insightpulseai.com`: Daily reports sent here

---

## Verification Steps

### 1. Check MX Records
```bash
dig MX insightpulseai.com +short
# Should show:
# 10 mx.zoho.com.
# 20 mx2.zoho.com.
# 50 mx3.zoho.com.
```

### 2. Check SPF Record
```bash
dig TXT insightpulseai.com +short | grep spf
# Should show:
# "v=spf1 include:zoho.com ~all"
```

### 3. Test Email Sending (After DigitalOcean Unblocks SMTP)
```bash
# From Odoo UI
Settings → Technical → Outgoing Mail Servers → Zoho SMTP - InsightPulse → Test Connection

# Should show: "Connection Test Succeeded!"
```

### 4. Test Email Receiving
Send a test email to: **business@insightpulseai.com**
- Check Zoho Workplace inbox
- Should arrive within 1-2 minutes

---

## DigitalOcean DNS Configuration

If using DigitalOcean for DNS:

1. Go to: https://cloud.digitalocean.com/networking/domains
2. Click on: `insightpulseai.com`
3. Add each record from tables above:
   - Click "Add Record"
   - Select record type (MX, TXT)
   - Enter Host, Priority (MX only), Value
   - Set TTL to 3600 (1 hour)
   - Click "Create Record"

---

## Common Issues

### Issue 1: "Domain not verified" in Zoho
**Solution**: Wait 24-48 hours for DNS propagation, then verify domain in Zoho Control Panel

### Issue 2: Emails not sending from Odoo
**Causes**:
1. ❌ DigitalOcean still blocking SMTP ports → Submit support ticket
2. ❌ Password not set in Odoo UI → Go to Settings → Technical → Outgoing Mail Servers
3. ❌ Wrong SMTP server → Must be `smtppro.zoho.com` (not `smtp.zoho.com`)

### Issue 3: Emails marked as spam
**Causes**:
1. Missing SPF record → Add SPF TXT record
2. Missing DKIM record → Add DKIM from Zoho Control Panel
3. Missing DMARC record → Add DMARC TXT record

---

## Final Checklist

- [ ] MX records added (3 records: priority 10, 20, 50)
- [ ] SPF record added (`v=spf1 include:zoho.com ~all`)
- [ ] DKIM record added (from Zoho Control Panel)
- [ ] DMARC record added (`v=DMARC1; p=quarantine`)
- [ ] DNS propagation verified (use `dig` commands)
- [ ] Zoho domain verified in Control Panel
- [ ] Odoo SMTP password set (Settings → Technical → Outgoing Mail Servers)
- [ ] DigitalOcean support ticket submitted (unblock ports 465, 587)
- [ ] Test Connection successful in Odoo

---

**Last Updated**: 2025-12-30 01:00 UTC
