# Infrastructure

Production infrastructure configuration for `erp.insightpulseai.net`.

---

## Environment Overview

| Component | Value |
|-----------|-------|
| **Production URL** | https://erp.insightpulseai.net |
| **Server** | DigitalOcean Droplet (178.128.112.214) |
| **Odoo Version** | 18.0 CE |
| **Database** | PostgreSQL 15 |
| **Docker Image** | `ghcr.io/jgtolentino/odoo-ce:edge-standard` |

---

## Mailgun Email Configuration

### Domain Setup

| Setting | Value |
|---------|-------|
| **Mail Domain** | `mg.insightpulseai.net` |
| **SMTP Server** | `smtp.mailgun.org` |
| **SMTP Ports** | 25, 587, 2525, 465 (SSL/TLS) |
| **SMTP Login** | `postmaster@mg.insightpulseai.net` |

### DNS Records Required

#### Sending Records (SPF + DKIM)

| Type | Host | Value |
|------|------|-------|
| TXT | `mg.insightpulseai.net` | `v=spf1 include:mailgun.org ~all` |
| TXT | `pic._domainkey.mg.insightpulseai.net` | `k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDcYB3DG10ylI4z6PWaiwyiByMrjwr9kfgJK8ccsZYT4guxi8+Emyf/nUs7IqR/LTZwwymeTZDaS/vQ6pjDhIaF2J9M9XsdgP+nv3wx99BqQ7dA+aa5sNwJKI3WRhr1YMK6IJQJIWSLERPBr74eMBAVa/Zmrfui1BOCgUFvQN9GBQIDAQAB` |

#### Receiving Records (MX)

| Type | Host | Value | Priority |
|------|------|-------|----------|
| MX | `mg.insightpulseai.net` | `mxa.mailgun.org` | 10 |
| MX | `mg.insightpulseai.net` | `mxb.mailgun.org` | 10 |

#### Tracking Records (CNAME)

| Type | Host | Value |
|------|------|-------|
| CNAME | `email.mg.insightpulseai.net` | `mailgun.org` |

#### Authentication Records (DMARC)

| Type | Host | Value |
|------|------|-------|
| TXT | `_dmarc.mg.insightpulseai.net` | `v=DMARC1; p=none; pct=100; fo=1; ri=3600; rua=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com; ruf=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com;` |

### Mailgun Preferences

| Setting | Value |
|---------|-------|
| Message retention | 1 day |
| Inbound spam filter | No filtering |
| Wildcard domain | Off |
| TLS connection | Opportunistic |
| Certificate verification | Required |
| Click tracking | Off |
| Open tracking | Off |

---

## Odoo Mail Configuration

### Outgoing Mail Server

Configure in **Settings > Technical > Outgoing Mail Servers**:

| Field | Value |
|-------|-------|
| Description | Mailgun SMTP |
| SMTP Server | `smtp.mailgun.org` |
| SMTP Port | `587` |
| Connection Security | TLS (STARTTLS) |
| Username | `postmaster@mg.insightpulseai.net` |
| Password | *(Mailgun SMTP password)* |

### System Parameters

```
mail.smtp.host = smtp.mailgun.org
mail.smtp.port = 587
mail.smtp.user = postmaster@mg.insightpulseai.net
mail.smtp.encryption = starttls
```

---

## GitHub Secrets Required

| Secret Name | Purpose | Scope |
|-------------|---------|-------|
| `WIKI_SYNC_TOKEN` | Sync docs/wiki to GitHub Wiki | PAT with `repo` scope |
| `PROJECT_TOKEN` | GitHub Projects automation | PAT with `project` scope |
| `MAILGUN_SMTP_PASSWORD` | Odoo email sending | Mailgun SMTP credential |

---

## DNS Verification Checklist

- [ ] SPF record (`v=spf1 include:mailgun.org ~all`)
- [ ] DKIM record (`pic._domainkey`)
- [ ] MX records (mxa, mxb)
- [ ] CNAME tracking record
- [ ] DMARC record
- [ ] Test email from Odoo Settings

---

## Related Documentation

- [Mailgun Domain Settings](https://app.mailgun.com/app/sending/domains/mg.insightpulseai.net)
- [Odoo Email Configuration](https://www.odoo.com/documentation/18.0/applications/general/email_communication.html)
