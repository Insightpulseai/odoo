# Outbound Email Routing Policy

Defines the intended ordering and purpose of each outbound mail server in Odoo (`ir.mail_server`).

---

## Server Registry

| Seq | Name | Host | Port | Enc | User | Purpose |
|-----|------|------|------|-----|------|---------|
| **1** | Zoho Mail API | `mail.zoho.com` | 465 | SSL | `no-reply@insightpulseai.com` | **Primary** — transactional + internal |
| **2** | Mailgun SMTP | `smtp.mailgun.org` | 2525 | STARTTLS | `no-reply@mg.insightpulseai.com` | **Secondary** — bulk, campaigns, DO SMTP-block bypass |
| **10** | Zoho SMTP Notifications | `smtppro.zoho.com` | 587 | STARTTLS | (notifications alias) | Notification-only fallback |

Odoo uses the **lowest sequence** server with a `smtp_pass` set and `active=True`.

---

## Routing Intent

- **Seq 1 (Zoho API)** is the primary sender for all transactional email (order confirmations, invoices, CRM replies). It uses the `ipai_zoho_mail_api` module which overrides the standard SMTP call path with a direct API transport.
- **Seq 2 (Mailgun SMTP)** handles bulk, campaigns, and any email where DigitalOcean's port-25 block would affect Zoho SMTP. Port 2525 is explicitly supported by Mailgun and confirmed open on the DO droplet.
- **Seq 10** is a low-priority notification alias — only used if seq 1 and 2 are both unavailable.

---

## Sequence Rules

- **Do not** renumber sequences without updating this doc.
- **Do not** add servers below seq 10 without confirming they do not shadow the notification alias.
- Mailgun SMTP password is set via `scripts/setup_mailgun_smtp_password.sh` — never hardcoded.
- Zoho API credentials (`ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN`) are set via env vars on the DO droplet, not in Odoo DB.

---

## MX Records

`mg.insightpulseai.com` has **no MX records** by design. This is an outbound-only subdomain. Do not add MX records unless inbound routing via Mailgun Routes is explicitly required.

---

## Verification

```bash
# Full preflight (DNS + Mailgun state + optional Odoo DB check)
MAILGUN_API_KEY=... python3 scripts/verify_mailgun_outbound.py

# Skip Odoo DB check (CI-safe, no DB creds needed)
MAILGUN_API_KEY=... python3 scripts/verify_mailgun_outbound.py --skip-odoo
```

See `docs/ops/email/MAILGUN_OUTBOUND_AUTOMATION.md` for the DNS publish + verify workflow.
