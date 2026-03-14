---
title: SSOT boundaries
description: Domain-by-domain map of which system is the single source of truth.
---

# SSOT boundaries

Every domain in the platform has exactly one single source of truth (SSOT). When two systems could each claim ownership, this page decides.

## Boundary map

| Domain | SSOT | Relying party | Mirror contract |
|--------|------|---------------|-----------------|
| **Identity and access** | Supabase Auth | Odoo `res.users` | Minimal projection only (UUID, email, org). Passwords, MFA, sessions never cross the boundary. |
| **Mail configuration** | `config/odoo/mail_settings.yaml` | Odoo `ir.mail_server` / `fetchmail.server` | Applied idempotently by `apply_mail_settings.py`. YAML is truth; DB row is a cache. |
| **DNS records** | `infra/dns/subdomain-registry.yaml` | Cloudflare | Via Terraform. Never edit Cloudflare dashboard directly. |
| **Secrets** | Azure Key Vault + Supabase Vault | Odoo conf, Edge Functions, container env vars | Never committed to Git. Names only in `infra/supabase/vault_secrets.tf`. |
| **ERP data** | Odoo PostgreSQL (`odoo`) | Supabase (read-only projections), ADLS (bronze copies) | Bridge functions only. Supabase replicas are non-authoritative for transactions. |
| **Automation workflows** | n8n (live instance) + `automations/n8n/` JSON | Supabase task queue | Deployed via `deploy_n8n_all.py`. Credentials are env references, never literal values. |
| **Module code** | `addons/ipai/` (OCA-style) | Odoo runtime | Installed via `odoo -i <module>`. Never modify OCA source -- use `_inherit` overrides. |
| **Specs and contracts** | `spec/<feature>/` (spec-kit) | CI, agent instructions | Enforced by `spec_validate.sh`. |
| **Platform events** | `ops.platform_events` (Supabase) | All services append | Append-only. No updates, no deletes. |

## Identity: Supabase Auth is SSOT

Supabase owns user identities, sessions, MFA, social/OAuth links, SAML federation, JWT signing keys, RBAC roles, and RLS policies.

Odoo is a **relying party**, not an identity provider. It receives a minimal projection:

| Supabase field | Odoo field | Notes |
|----------------|-----------|-------|
| `auth.users.id` (UUID) | `res.users.x_supabase_user_id` | Linkage key |
| `auth.users.email` | `res.users.login` / `res.partner.email` | Kept in sync |
| Org / company ID | `res.users.company_ids` | Derived from Supabase org membership |
| Role label | `res.users.groups_id` (via bridge) | Mapped, not authoritative |

!!! danger "Never mirror"
    Passwords, MFA factors, sessions, tokens, social identity metadata, and raw JWT claims must never cross from Supabase into Odoo.

## Mail: YAML is SSOT

```
config/odoo/mail_settings.yaml          <-- edit this (SSOT)
        |
        v
scripts/odoo/apply_mail_settings.py     <-- idempotent applier
        |
        v
Odoo DB: ir_mail_server, fetchmail_server  <-- derived (SoR for sending)
```

Outbound mail routes through Zoho SMTP (`smtppro.zoho.com:587`, STARTTLS). Mailgun (`mg.insightpulseai.com`) is permanently deprecated.

## Secrets: never in Git

| Secret | Storage | Access pattern |
|--------|---------|---------------|
| Zoho SMTP credentials | Azure Key Vault (`kv-ipai-dev`) | Managed identity to env vars |
| Odoo admin password | Container env var | Injected at container start |
| Supabase service role key | GitHub Actions secret + Vault | Never in files |
| DB password | Container CMD arg | Never logged |

!!! warning "Log hygiene"
    Scripts print only `host`, `port`, `user`, `PASS/FAIL`. Never print a token, password, or key -- even partially.

## ERP data: Odoo is SoR

Odoo PostgreSQL is authoritative for:

- Accounting entries, invoices, payments
- HR records (employees, contracts, timesheets)
- Inventory and stock moves
- CRM leads and opportunities
- Purchases and sales orders

Data mirrors into Supabase as read-only projections. Supabase tables mirroring Odoo enforce RLS read-only policies. No dual-write is permitted.

## Platform events: append-only

The `ops.platform_events` table in Supabase is the canonical audit log for all cross-system events. All services may append. No service may update or delete rows.

!!! info "Supabase migrations"
    Never generate a migration that drops or truncates any table in the `ops` schema. New columns use `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`.

## Cross-domain contract objects

Objects that cross SSOT boundaries require explicit mirror contracts:

| Object | Source SSOT | Consumer | Contract |
|--------|------------|----------|----------|
| Supabase JWT | Supabase Auth | Odoo middleware, Azure Edge | JWT signing key via JWKS endpoint |
| Outbound email | Odoo `ir.mail_server` | Zoho SMTP | `docs/contracts/DNS_EMAIL_CONTRACT.md` |
| DNS record set | `infra/dns/subdomain-registry.yaml` | Cloudflare, Odoo `web.base.url` | Terraform apply |
| n8n to task queue | n8n workflows | `ops.task_queue` (Supabase) | REST POST to Edge Function |
| Design tokens | Figma (canonical) | `packages/design-tokens/tokens.json` | `export_tokens.sh` |
