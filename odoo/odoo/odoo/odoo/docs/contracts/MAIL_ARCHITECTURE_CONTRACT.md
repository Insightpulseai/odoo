# Mail Architecture Contract — insightpulseai.com

> **Contract ID**: C-26
> **Status**: Active
> **Supersedes**: C-02 (Outbound Mail Bridge — deprecated)
> **Owner**: Platform Engineering
> **Last Updated**: 2026-03-08

---

## 1. Provider Split

| Provider | Domain | Use Case | SMTP Host | Port |
|----------|--------|----------|-----------|------|
| **Mailgun** | `mg.insightpulseai.com` | Odoo outbound transactional mail | `smtp.mailgun.org` | 587 (prod), 2525 (dev/stage) |
| **Zoho** | `insightpulseai.com` (root) | Human/business mailboxes | `smtppro.zoho.com` | 587 |

---

## 2. Sender Policy

### Mailgun path (app/system mail)

Allowed senders on `mg.insightpulseai.com`:

| Sender | Use Case |
|--------|----------|
| `no-reply@mg.insightpulseai.com` | Default Odoo transactional mail |
| `odoo@mg.insightpulseai.com` | Odoo system notifications |
| `notifications@mg.insightpulseai.com` | Automated alerts |
| `invoices@mg.insightpulseai.com` | Invoice/quotation delivery |
| `auth@mg.insightpulseai.com` | Authentication/password reset |

### Zoho path (human/business mail)

Root-domain addresses handled by Zoho:

| Sender | Use Case |
|--------|----------|
| `business@insightpulseai.com` | Primary business contact |
| `info@insightpulseai.com` | General inquiries |
| `billing@insightpulseai.com` | Billing correspondence |
| `finance@insightpulseai.com` | Finance team |
| `devops@insightpulseai.com` | DevOps/operations |

### Forbidden

- Odoo sending from root-domain addresses (e.g. `business@insightpulseai.com`) through Mailgun
- Human/business correspondence routed through Mailgun transactional path
- Any bridge module (`ipai_mail_bridge_zoho`) overriding standard `ir.mail_server`

---

## 3. DNS Authentication

### Root domain (`insightpulseai.com`) — Zoho

| Type | Name | Value | Purpose |
|------|------|-------|---------|
| MX | `@` | `mx.zoho.com` (10), `mx2.zoho.com` (20), `mx3.zoho.com` (50) | Mail routing |
| TXT | `@` | `v=spf1 include:zoho.com ~all` | SPF |
| TXT | `zoho._domainkey` | `<DKIM key>` | DKIM |
| TXT | `_dmarc` | `v=DMARC1; p=quarantine; ...` | DMARC |

### Subdomain (`mg.insightpulseai.com`) — Mailgun

| Type | Name | Value | Purpose |
|------|------|-------|---------|
| CNAME | `email.mg` | Mailgun tracking CNAME | Tracking |
| TXT | `mg` | `v=spf1 include:mailgun.org ~all` | SPF |
| TXT | Mailgun DKIM selector under `mg` | `<DKIM key>` | DKIM |
| TXT | `_dmarc.mg` | `v=DMARC1; p=quarantine; ...` | DMARC |

---

## 4. Odoo Configuration

Odoo uses standard `ir.mail_server` pointed at Mailgun SMTP. No bridge module required.

```
Outgoing Mail Server:
  Name: Mailgun (mg.insightpulseai.com)
  SMTP Server: smtp.mailgun.org
  SMTP Port: 587 (prod) / 2525 (dev/stage)
  Connection Security: TLS (STARTTLS)
  Username: <Mailgun SMTP credential>
  Password: <Mailgun SMTP password>
```

Credentials are stored in env vars / secrets, never in source.

---

## 5. Environment Policy

| Environment | SMTP Host | Port | Credentials | Mail Catcher |
|-------------|-----------|------|-------------|--------------|
| PROD | `smtp.mailgun.org` | 587 | Production Mailgun | No |
| STAGE | `smtp.mailgun.org` | 2525 | Non-prod Mailgun | Required |
| DEV | `smtp.mailgun.org` | 2525 | Non-prod Mailgun | Required |

See `docs/contracts/C-MAIL-01-mail-catcher.md` for catcher requirements.

---

## 6. Why This Split

- **Deliverability isolation**: Odoo transactional volume stays on `mg` subdomain, protecting root-domain business reputation
- **Operational clarity**: App automation → Mailgun, people/business mail → Zoho
- **DNS simplicity**: Each provider authenticates its own subdomain independently
- **Bounce/complaint tracking**: Mailgun webhooks handle transactional delivery events without affecting business mail

---

## 7. Deprecated

| Item | Status | Reason |
|------|--------|--------|
| `ipai_mail_bridge_zoho` module | Deprecated | Odoo uses `ir.mail_server` → Mailgun SMTP directly |
| `zoho-mail-bridge` Edge Function | Deprecated | No bridge needed — standard SMTP |
| C-02 (Outbound Mail Bridge Contract) | Superseded by C-26 | Bridge architecture replaced by direct SMTP |

---

## 8. SSOT References

| Resource | Path |
|----------|------|
| DNS config (Zoho) | `infra/dns/zoho_mail_dns.yaml` |
| DNS config (Mailgun) | `infra/dns/subdomain-registry.yaml` (mg subdomain) |
| Mail catcher contract | `docs/contracts/C-MAIL-01-mail-catcher.md` |
| Mailgun integration SSOT | `ssot/integrations/mailgun.yaml` |
| Agent rule | `.claude/rules/ssot-platform.md` (Rule 7) |

---

## 9. Policy Statement

> Root domain mailboxes on `insightpulseai.com` are handled by Zoho.
> System-generated outbound mail from Odoo and other automated app flows uses Mailgun on the `mg.insightpulseai.com` subdomain.
> Human/business correspondence must not be sent through the Mailgun transactional path unless explicitly approved.
