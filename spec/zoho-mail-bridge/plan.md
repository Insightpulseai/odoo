# Plan — Zoho Mail Bridge

## Implementation Order

### Step 0: Hotfix (DONE — commit b9e192936)
- `addons/ipai/ipai_zoho_mail/data/mail_server.xml`: `smtp.zoho.com` → `smtppro.zoho.com`; `noreply@` → `business@`
- `addons/ipai/ipai_zoho_mail/data/fetchmail_server.xml`: `imap.zoho.com` → `imappro.zoho.com`
- Live DB: patched `ir_mail_server` row directly via psql + new app password `NAHwkS9cpvzh`
- SMTP probe: **PASSED** `smtppro.zoho.com:587` AUTH OK

### Step A: Config SSOT
- `config/odoo/mail_settings.yaml` — dev/prod sections, smtppro endpoints
- Passwords as `${ENV_VAR}` placeholders

### Step B: Settings-as-Code Script
- `scripts/odoo/apply_mail_settings.py`
- argparse: `--env dev|prod`, `--dry-run`, `--verify`
- XML-RPC upsert of `ir.mail_server` and `fetchmail.server`
- Passwords masked in all output

### Step C: DNS Codification
- `infra/dns/zoho_mail_dns.yaml` — MX(×3), SPF, DKIM placeholder, DMARC
- `docs/contracts/DNS_EMAIL_CONTRACT.md` — record table, drift policy

### Step D: Supabase Migration
- `supabase/migrations/20260221000000_integrations_zoho.sql`
- 4 tables in existing `integrations` + `bridge` schemas
- Append-safe (IF NOT EXISTS), RLS policies, indexes

### Step E: Edge Function
- `supabase/functions/zoho-mail-bridge/index.ts`
- Routes: `mint_token`, `send_email`
- Reads Vault vars: `ZOHO_REFRESH_TOKEN`, `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`
- Audit to `ops.platform_events`
- `supabase/functions/zoho-mail-bridge/README.md`

### Step F: Vault Update
- `infra/supabase/vault_secrets.tf` — add 3 Zoho variables

## Architecture

```
Odoo 19 CE
  └─ ipai_zoho_mail module
       ├─ ir.mail_server  →  smtppro.zoho.com:587 (app pwd)
       └─ fetchmail.server → imappro.zoho.com:993 (app pwd)

apply_mail_settings.py
  reads config/odoo/mail_settings.yaml
  XML-RPC upsert → Odoo prod

n8n / external callers
  → supabase/functions/zoho-mail-bridge
       ├─ mint_token (refresh_token grant)
       └─ send_email (Zoho Mail API)
  → audit → ops.platform_events

Supabase Vault
  ZOHO_CLIENT_ID / ZOHO_CLIENT_SECRET / ZOHO_REFRESH_TOKEN
```
