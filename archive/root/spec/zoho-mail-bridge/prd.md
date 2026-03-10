# PRD — Zoho Mail Bridge

**Version**: 1.0.0
**Domain**: `insightpulseai.com`
**Status**: In Progress

## Problem

Odoo 19 CE needs reliable outgoing email for notifications, invoices, and CRM. Zoho Mail is the authoritative mail provider for `@insightpulseai.com`. The integration was broken because:
- Wrong regional SMTP host (`smtp.zoho.com` instead of US DC `smtppro.zoho.com`)
- No settings-as-code — credentials lived only in the Odoo UI, making them invisible to CI and DR
- No OAuth2 bridge for programmatic sends from n8n/Edge Functions without routing through Odoo

## Functional Requirements

### FR-1: Odoo SMTP (App Password)
- Odoo sends all transactional email via `smtppro.zoho.com:587` STARTTLS
- From address: `business@insightpulseai.com`
- Auth: Zoho App Password (generated in Zoho Security settings)
- `ir_mail_server` record is created/updated idempotently by `apply_mail_settings.py`

### FR-2: Odoo IMAP Catchall
- `fetchmail.server` record at `imappro.zoho.com:993` SSL
- Catchall address: `catchall@insightpulseai.com`
- Password set manually after module installation (IMAP App Password)

### FR-3: Settings-as-Code
- `config/odoo/mail_settings.yaml` is the canonical host/port/user config
- `scripts/odoo/apply_mail_settings.py` reads YAML, connects via XML-RPC, upserts records
- Supports `--env dev|prod`, `--dry-run`, `--verify`

### FR-4: DNS-as-Code
- `infra/dns/zoho_mail_dns.yaml` declares MX, SPF, DKIM, DMARC for `insightpulseai.com`
- Applied via Cloudflare API (or Terraform) — not via UI
- `docs/contracts/DNS_EMAIL_CONTRACT.md` documents drift policy

### FR-5: OAuth2 API Bridge (Supabase Edge Function)
- `supabase/functions/zoho-mail-bridge/index.ts` mints Zoho API access tokens via refresh-token grant
- Exposes `send_email` action for n8n/webhooks to send without routing through Odoo SMTP
- Every operation appended to `ops.platform_events`

### FR-6: Supabase Schema
- `integrations.zoho_accounts` — Zoho account registry
- `integrations.zoho_tokens` — refresh token refs (service-role only)
- `integrations.mail_identities` — per-company from/reply-to policies
- `bridge.odoo_mail_server_map` — links Odoo `ir.mail_server` IDs to identity records

## Out of Scope
- Zoho Campaigns (marketing email)
- Zoho CRM sync
- Multi-tenant Zoho accounts (single account only for now)
