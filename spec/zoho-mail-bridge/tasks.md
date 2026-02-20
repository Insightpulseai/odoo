# Tasks — Zoho Mail Bridge

## Completed

- [x] T01 Fix SMTP/IMAP hostnames in data XML files (b9e192936)
- [x] T02 Update live production DB `ir_mail_server` row (smtppro.zoho.com + new app pwd)
- [x] T03 SMTP probe passes: `smtppro.zoho.com:587` AUTH OK

## In Progress / Pending

- [x] T04 Create spec kit (constitution/prd/plan/tasks) — this file
- [ ] T05 Create `config/odoo/mail_settings.yaml`
- [ ] T06 Create `scripts/odoo/apply_mail_settings.py`
- [ ] T07 Create `infra/dns/zoho_mail_dns.yaml`
- [ ] T08 Create `docs/contracts/DNS_EMAIL_CONTRACT.md`
- [ ] T09 Create `supabase/migrations/20260221000000_integrations_zoho.sql`
- [ ] T10 Create `supabase/functions/zoho-mail-bridge/index.ts`
- [ ] T11 Create `supabase/functions/zoho-mail-bridge/README.md`
- [ ] T12 Update `infra/supabase/vault_secrets.tf`
- [ ] T13 Commit all deliverables

## [MANUAL_REQUIRED] After Code Merge

- **T-M1**: Create Zoho OAuth2 client at https://api-console.zoho.com
  - Add Client → Server-based
  - Scopes: `ZohoMail.messages.CREATE`, `ZohoMail.accounts.READ`
  - Redirect URI: `https://erp.insightpulseai.com/oauth/callback`
  - Store `client_id`, `client_secret`, `refresh_token` in Supabase Vault

- **T-M2**: Generate IMAP App Password for `catchall@insightpulseai.com` in Zoho Security settings
  - Apply to `fetchmail.server` record via Odoo Settings UI or `apply_mail_settings.py --env prod`

- **T-M3**: Deploy Edge Function
  - `supabase functions deploy zoho-mail-bridge`
  - Wire Vault secrets as Edge Function env vars
