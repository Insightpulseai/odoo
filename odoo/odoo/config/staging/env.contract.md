# Staging Environment Contract

## Purpose

Documents the expected staging runtime inputs for `config/staging/odoo.conf`.
Staging is a production-like rehearsal environment with safety controls.

Doctrine: `docs/architecture/azure/AZURE_ODOOSH_EQUIVALENT.md` §4

## Required runtime assumptions

- Postgres service hostname: `postgres`
- Postgres port: `5432`
- Postgres database user: `odoo`
- Postgres database password: resolved via Key Vault / env var
- Odoo service port: `8069`
- Public URL: `https://erp-staging.insightpulseai.com`

## Database

- `odoo_staging` — single staging database
- Data source: sanitized production snapshot (weekly refresh)
- PII masking applied during refresh

## Staging-specific behavior

- `workers = 2` — multi-process (prod-like) but reduced scale
- `max_cron_threads = 1` — gated cron (most crons inactive by default)
- `proxy_mode = True` — behind Front Door/nginx
- `list_db = False` — no database selector
- `dev_mode` — NOT set (no dev ergonomics in staging)
- SMTP points to MailHog on port 1025 — **no external email delivery**
- All outbound mail is captured at `http://mailhog:8025`
- Payment providers in test mode
- External API integrations sandboxed

## Non-prod safety controls

| Control | Setting |
|---------|---------|
| Mail delivery | MailHog sink — no external delivery |
| Cron jobs | Default inactive, whitelist-only |
| Payment providers | Test mode only |
| SMS gateway | Disabled |
| External APIs | Sandbox endpoints only |
| PII | Masked during refresh |
| Webhooks | Disabled |
| Production API keys | Never present |

## Backup

- Daily backup, 7-day retention
- Staging is rebuildable — not a data authority

## Access

- Developers, QA, and Project Managers
- Not public-facing for end users

## Related

- `config/dev/` — local development config
- `config/prod/` — production-optimized config
- `ssot/governance/azure-odoosh-equivalent.yaml` — environment model
