# Mailgun DNS Setup for mg.insightpulseai.com

**Domain**: `mg.insightpulseai.com`
**Created**: 2026-01-06
**Provider**: Mailgun

---

## DNS Records Required

### Sending Records (SPF & DKIM)

| Type | Host | Value |
|------|------|-------|
| TXT | `mg.insightpulseai.com` | `v=spf1 include:mailgun.org ~all` |
| TXT | `pic._domainkey.mg.insightpulseai.com` | `k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDcYB3DG10ylI4z6PWaiwyiByMrjwr9kfgJK8ccsZYT4guxi8+Emyf/nUs7IqR/LTZwwymeTZDaS/vQ6pjDhIaF2J9M9XsdgP+nv3wx99BqQ7dA+aa5sNwJKI3WRhr1YMK6IJQJIWSLERPBr74eMBAVa/Zmrfui1BOCgUFvQN9GBQIDAQAB` |

### Receiving Records (MX) - Optional

Only needed if you want to receive email at this subdomain. Skip if using Gmail/other for receiving.

| Type | Host | Value | Priority |
|------|------|-------|----------|
| MX | `mg.insightpulseai.com` | `mxa.mailgun.org` | 10 |
| MX | `mg.insightpulseai.com` | `mxb.mailgun.org` | 10 |

### Tracking Record (CNAME)

Required for open/click tracking and unsubscribe links.

| Type | Host | Value |
|------|------|-------|
| CNAME | `email.mg.insightpulseai.com` | `mailgun.org` |

### Authentication Record (DMARC)

Required by Google and Yahoo for deliverability.

| Type | Host | Value |
|------|------|-------|
| TXT | `_dmarc.mg.insightpulseai.com` | `v=DMARC1; p=none` |

---

## Verification

After adding DNS records, verify in Mailgun dashboard:
- Go to: **Sending > Domain Settings > mg.insightpulseai.com**
- Click **Verify DNS Settings**

Or use external tools:
- **MX Toolbox**: https://mxtoolbox.com/
- **DKIM Validator**: https://dkimvalidator.com/

---

## Odoo Configuration

Run on production:

```bash
docker exec -i odoo-ce odoo shell -d odoo < scripts/configure_mailgun_smtp.py
```

Then set SMTP password in Odoo UI:
1. Settings > Technical > Outgoing Mail Servers
2. Click "Mailgun SMTP - InsightPulse"
3. Enter password from Mailgun dashboard
4. Save and Test Connection

---

## SMTP Settings Reference

| Setting | Value |
|---------|-------|
| Server | `smtp.mailgun.org` |
| Port | `2525` (DigitalOcean compatible) |
| Encryption | STARTTLS |
| Username | `postmaster@mg.insightpulseai.com` |
| Password | (from Mailgun dashboard) |

---

**Last Updated**: 2026-01-09
