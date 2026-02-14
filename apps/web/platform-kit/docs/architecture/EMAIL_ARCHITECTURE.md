# Email Architecture - InsightPulse AI

## Overview

This document describes the complete email architecture for InsightPulse AI, following SSOT (Single Source of Truth) principles.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     INSIGHTPULSE AI EMAIL ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  INBOUND (Receiving Email)                                                   │
│  ════════════════════════                                                    │
│                                                                              │
│  External Sender                                                             │
│       │                                                                      │
│       ▼                                                                      │
│  DNS Lookup: insightpulseai.com MX                                          │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────┐                                            │
│  │    Zoho Mail Servers        │                                            │
│  │  mx.zoho.com (priority 10)  │                                            │
│  │  mx2.zoho.com (priority 20) │                                            │
│  │  mx3.zoho.com (priority 50) │                                            │
│  └─────────────────────────────┘                                            │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────┐                                            │
│  │    Zoho Mail Inbox          │                                            │
│  │  business@insightpulseai.com│                                            │
│  │  support@insightpulseai.com │                                            │
│  └─────────────────────────────┘                                            │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  OUTBOUND (Sending Transactional Email)                                      │
│  ══════════════════════════════════════                                      │
│                                                                              │
│  ┌─────────────────────────────┐                                            │
│  │      Odoo 19 ERP            │                                            │
│  │  erp.insightpulseai.com     │                                            │
│  └─────────────────────────────┘                                            │
│       │                                                                      │
│       │ SMTP (smtp.mailgun.org:587, STARTTLS)                               │
│       │ User: no-reply@mg.insightpulseai.com                                │
│       ▼                                                                      │
│  ┌─────────────────────────────┐                                            │
│  │    Mailgun (US Region)      │                                            │
│  │  mg.insightpulseai.com      │                                            │
│  │                             │                                            │
│  │  - SPF verified             │                                            │
│  │  - DKIM signed              │                                            │
│  │  - Deliverability tracking  │                                            │
│  └─────────────────────────────┘                                            │
│       │                                                                      │
│       ▼                                                                      │
│  Recipients worldwide                                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Why This Split Architecture?

### Zoho for Inbound
- **Professional mailboxes** with full email client features
- **Collaboration** tools (calendar, contacts, tasks)
- **Spam filtering** and security
- **Compliance** with data retention policies
- **Cost-effective** for team mailboxes

### Mailgun for Outbound
- **High deliverability** for transactional email
- **API access** for programmatic sending
- **Detailed analytics** (opens, clicks, bounces)
- **Webhook support** for real-time events
- **Scalability** for high-volume sending
- **SMTP relay** for Odoo integration

## Domain Structure

| Domain | Purpose | Provider |
|--------|---------|----------|
| `insightpulseai.com` | Root domain, inbound email | Zoho Mail |
| `mg.insightpulseai.com` | Outbound transactional | Mailgun |
| `insightpulseai.net` | **DEPRECATED** | Do not use |

## DNS Configuration

### DNS Provider
- **Provider**: Wix DNS
- **Nameservers**: `ns6.wixdns.net`, `ns7.wixdns.net`
- **Management**: https://manage.wix.com

### Root Domain (insightpulseai.com)

| Type | Host | Value | Purpose |
|------|------|-------|---------|
| MX | @ | mx.zoho.com (10) | Zoho primary |
| MX | @ | mx2.zoho.com (20) | Zoho secondary |
| MX | @ | mx3.zoho.com (50) | Zoho tertiary |
| TXT | @ | `v=spf1 include:zohomail.com include:mailgun.org ~all` | SPF |
| TXT | _dmarc | `v=DMARC1; p=quarantine; rua=mailto:dmarc@...` | DMARC |

### Mailgun Subdomain (mg.insightpulseai.com)

| Type | Host | Value | Purpose |
|------|------|-------|---------|
| TXT | mg | `v=spf1 include:mailgun.org ~all` | SPF |
| TXT | mx._domainkey.mg | `k=rsa; p=MIGfMA0GCSqGSIb3...` | DKIM |
| MX | mg | mxa.mailgun.org (10) | Mailgun MX |
| MX | mg | mxb.mailgun.org (10) | Mailgun MX |
| CNAME | email.mg | mailgun.org | Tracking |

## SMTP Credentials

### Users

| User | Login | Purpose |
|------|-------|---------|
| No-Reply | `no-reply@mg.insightpulseai.com` | System notifications, invoices |
| Support | `support@mg.insightpulseai.com` | Helpdesk, customer responses |

### Connection Settings

```
Server: smtp.mailgun.org
Port: 587
Encryption: STARTTLS
Authentication: Required
```

## Odoo 19 Configuration

### Outgoing Mail Server

| Setting | Value |
|---------|-------|
| Description | Mailgun - insightpulseai.com |
| SMTP Server | smtp.mailgun.org |
| SMTP Port | 587 |
| Connection Security | TLS (STARTTLS) |
| Username | no-reply@mg.insightpulseai.com |
| FROM Filtering | insightpulseai.com |

### System Parameters

| Key | Value |
|-----|-------|
| mail.catchall.domain | insightpulseai.com |
| mail.catchall.alias | catchall |
| mail.default.from | notifications |
| mail.bounce.alias | bounce |
| web.base.url | https://erp.insightpulseai.com |

## Single Source of Truth (SSOT)

### What Lives Where

```
INTENT / POLICY (Git)
└── GitHub Repository
    ├── config/domains.yaml          # Domain policy
    ├── config/mail/mailgun.yaml     # Mailgun config
    ├── infra/dns/*.json             # DNS records
    └── docs/arch/           # This documentation

SECRETS (Never in Git)
└── Secret Store (Supabase / Vercel / .env)
    ├── MAILGUN_API_KEY
    ├── MAILGUN_SMTP_PASSWORD
    ├── MAILGUN_SMTP_PASSWORD_SUPPORT
    └── MAILGUN_WEBHOOK_SIGNING_KEY

RUNTIME STATE (Execution Only)
├── Mailgun → Sends email, tracks events
├── Zoho → Receives email, mailboxes
└── Wix DNS → Executes DNS records

UI PANELS (Views, NOT Sources)
├── Mailgun Dashboard → View/verify only
├── Wix DNS Panel → Apply records from Git
└── Zoho Admin → Mailbox management
```

### Golden Rule

> **If it's not in Git, it's not real.**

All configuration changes MUST:
1. Be committed to Git first
2. Be applied to runtime services
3. Be verified via scripts/CI

## Verification Commands

```bash
# Check DNS records
dig MX insightpulseai.com +short
dig TXT mg.insightpulseai.com +short
dig TXT mx._domainkey.mg.insightpulseai.com +short

# Verify Mailgun domain
./scripts/mailgun/mailgun-domain-setup.sh verify

# Test email sending
./scripts/mailgun/mailgun-domain-setup.sh test your-email@example.com

# Full status check
./scripts/mailgun/mailgun-domain-setup.sh status
```

## Migration Notes

### From .net to .com

The domain `mg.insightpulseai.net` is **deprecated**. All systems should use:
- Canonical: `mg.insightpulseai.com`
- Root: `insightpulseai.com`

### Checklist

- [x] Mailgun domain created (mg.insightpulseai.com)
- [x] SMTP credentials created (no-reply, support)
- [x] Repository configs updated
- [ ] DNS records added in Wix
- [ ] Mailgun domain verified
- [ ] Test email sent successfully
- [ ] Odoo mail server configured

## Related Files

| File | Purpose |
|------|---------|
| `config/domains.yaml` | Domain policy SSOT |
| `config/mail/mailgun.yaml` | Mailgun configuration |
| `infra/dns/mailgun/mg_insightpulseai_com.json` | Mailgun DNS records |
| `infra/dns/zoho_root_insightpulseai_com.json` | Zoho/root DNS records |
| `infra/dns/mailgun/WIX_DNS_INSTRUCTIONS.md` | Wix setup guide |
| `.env.example` | Environment variable template |
| `config/odoo/email_settings.xml` | Odoo XML import |
