# DNS Settings Reference — insightpulseai.net

> **Last Updated:** 2026-01-13
> **Registrar:** Namecheap
> **Email Provider:** Mailgun (mg.insightpulseai.net subdomain)
> **Hosting:** DigitalOcean (178.128.112.214)

---

## Overview

This document captures the canonical DNS configuration for `insightpulseai.net` and its subdomains. All services are hosted on a single DigitalOcean droplet with nginx reverse proxy routing.

---

## A Records (IPv4)

| Host | TTL | Points To | Service |
|------|-----|-----------|---------|
| `@` (root) | 4 hrs | 178.128.112.214 | Main site |
| `n8n` | 1 hr | 178.128.112.214 | n8n automation |
| `mcp` | 1 hr | 178.128.112.214 | MCP coordinator |
| `erp` | 1 hr | 178.128.112.214 | Odoo ERP |
| `auth` | 1 hr | 178.128.112.214 | Keycloak SSO |
| `superset` | 4 hrs | 178.128.112.214 | Apache Superset BI |

---

## CNAME Records

| Host | TTL | Points To | Purpose |
|------|-----|-----------|---------|
| `www` | 1 hr | insightpulseai.net | WWW redirect |
| `email.mg` | 1 hr | mailgun.org | Mailgun tracking |

---

## MX Records (Mail Exchange)

| Host | Priority | TTL | Points To |
|------|----------|-----|-----------|
| `mg` | 10 | 1 hr | mxa.mailgun.org |
| `mg` | 10 | 1 hr | mxb.mailgun.org |

> **Note:** MX records are on the `mg` subdomain only. The root domain does not receive email.

---

## TXT Records

### SPF (Sender Policy Framework)

| Host | TTL | Value |
|------|-----|-------|
| `mg` | 5 mins | `v=spf1 include:mailgun.org ~all` |

### DKIM (DomainKeys Identified Mail)

| Host | TTL | Value |
|------|-----|-------|
| `pic._domainkey.mg` | 1 hr | `k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDcYB3DG10ylI4z6PWaiwyiByMrjwr9kfgJK8ccsZYT4guxi8+Emyf/nUs7IqR/LTZwwymeTZDaS/vQ6pjDhIaF2J9M9XsdgP+nv3wx99BqQ7dA+aa5sNwJKI3WRhr1YMK6IJQJIWSLERPBr74eMBAVa/Zmrfui1BOCgUFvQN9GBQIDAQAB` |

### DMARC (Domain-based Message Authentication)

| Host | TTL | Value |
|------|-----|-------|
| `_dmarc.mg` | 4 hrs | `v=DMARC1; p=none; pct=100; fo=1; ri=3600; rua=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com; ruf=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com;` |

---

## CAA Record (Certificate Authority Authorization)

| Host | TTL | Value |
|------|-----|-------|
| `@` | 1 hr | `0 issue "letsencrypt.org"` |

> Only Let's Encrypt is authorized to issue SSL certificates for this domain.

---

## Mailgun Configuration

### Domain

- **Sending Domain:** `mg.insightpulseai.net`
- **Postmaster:** `postmaster@mg.insightpulseai.net`
- **Created:** 2026-01-06

### SMTP Settings

| Setting | Value |
|---------|-------|
| **Server** | smtp.mailgun.org |
| **Ports** | 25, 587, 2525, 465 (SSL/TLS) |
| **Username** | `<user>@mg.insightpulseai.net` |
| **Authentication** | Required |

### API Keys

| Key ID | Description | Role |
|--------|-------------|------|
| `f6d80573-4c6f8ebe` | Odoo | Admin |
| `42b8ce75-98a02c53` | router | Admin |

### HTTP Webhook Signing Key

```
c0c7520dd678591f7b352e0f18c17b60
```

> Used to verify webhook payloads from Mailgun. See [Mailgun webhook documentation](https://documentation.mailgun.com/docs/mailgun/api-reference/openapi-final/tag/Webhooks/).

### Verification Public Key (Deprecated v3)

```
pubkey-5b792f9cc31ca46f66ed27884143e219
```

> Only for deprecated v3 validations endpoint. Use v4 validations with API keys instead.

### Webhooks

Mailgun can send webhook events for email tracking. Configure via API or dashboard.

**Webhook Event Types:**

| Event | Description |
|-------|-------------|
| `accepted` | Message accepted by Mailgun |
| `delivered` | Message delivered to recipient |
| `opened` | Recipient opened the message |
| `clicked` | Recipient clicked a link |
| `unsubscribed` | Recipient unsubscribed |
| `complained` | Recipient marked as spam |
| `permanent_fail` | Hard bounce (invalid address) |
| `temporary_fail` | Soft bounce (temporary issue) |

**Webhook URL (n8n):**

```
https://n8n.insightpulseai.net/webhook/mailgun
```

**Verifying Webhook Signatures:**

Use the HTTP Webhook Signing Key to verify payload authenticity. See [Mailgun Webhooks API](https://documentation.mailgun.com/docs/mailgun/api-reference/send/mailgun/webhooks).

---

## DNS Record Verification

### Check SPF

```bash
dig TXT mg.insightpulseai.net +short
```

### Check DKIM

```bash
dig TXT pic._domainkey.mg.insightpulseai.net +short
```

### Check MX

```bash
dig MX mg.insightpulseai.net +short
```

### Check DMARC

```bash
dig TXT _dmarc.mg.insightpulseai.net +short
```

### Check A Records

```bash
dig A insightpulseai.net +short
dig A erp.insightpulseai.net +short
dig A n8n.insightpulseai.net +short
```

---

## Service Endpoints

| Subdomain | URL | Service | Port (Internal) |
|-----------|-----|---------|-----------------|
| Root | https://insightpulseai.net | Main site | 80/443 |
| erp | https://erp.insightpulseai.net | Odoo ERP | 8069 |
| n8n | https://n8n.insightpulseai.net | n8n Automation | 5678 |
| auth | https://auth.insightpulseai.net | Keycloak SSO | 8080 |
| superset | https://superset.insightpulseai.net | Apache Superset | 8088 |
| mcp | https://mcp.insightpulseai.net | MCP Coordinator | 8766 |

---

## Nginx Reverse Proxy

All subdomains are routed through nginx on the DigitalOcean droplet. Configuration location:

```
/etc/nginx/sites-available/
├── erp.insightpulseai.net
├── n8n.insightpulseai.net
├── auth.insightpulseai.net
├── superset.insightpulseai.net
└── mcp.insightpulseai.net
```

SSL certificates are managed by Certbot (Let's Encrypt).

---

## Mailgun Integration with Odoo

### Environment Variables

```bash
# .env
MAILGUN_API_KEY=key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MAILGUN_DOMAIN=mg.insightpulseai.net
MAILGUN_SMTP_SERVER=smtp.mailgun.org
MAILGUN_SMTP_PORT=587
MAILGUN_SMTP_USER=postmaster@mg.insightpulseai.net
MAILGUN_SMTP_PASSWORD=<smtp-password>
```

### Odoo Outgoing Mail Server Configuration

| Field | Value |
|-------|-------|
| Description | Mailgun SMTP |
| SMTP Server | smtp.mailgun.org |
| SMTP Port | 587 |
| Connection Security | TLS (STARTTLS) |
| Username | postmaster@mg.insightpulseai.net |
| Password | (from Mailgun SMTP credentials) |

---

## References

### Mailgun

- [Mailgun Documentation](https://documentation.mailgun.com/)
- [Mailgun API Reference](https://documentation.mailgun.com/docs/mailgun/api-reference/openapi-final/tag/Domains/)
- [Webhooks API](https://documentation.mailgun.com/docs/mailgun/api-reference/send/mailgun/webhooks)
- [Webhook Signing Key API](https://documentation.mailgun.com/docs/mailgun/api-reference/send/mailgun/account-management/post-v5-accounts-http_signing_key)
- [Webhooks Help Center](https://help.mailgun.com/hc/en-us/articles/202236504-Webhooks)
- [Webhooks Guide](https://www.mailgun.com/blog/product/a-guide-to-using-mailguns-webhooks/)

### DNS & SSL

- [Namecheap DNS Management](https://www.namecheap.com/support/knowledgebase/article.aspx/767/10/how-to-change-dns-for-a-domain/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

---

*This document is auto-maintained. Update via PR to main branch.*
