# Production Environment Contract

## Purpose

Documents the expected production runtime inputs for `config/prod/odoo.conf`.

Doctrine: `docs/architecture/azure/AZURE_ODOOSH_EQUIVALENT.md` §4

## Required runtime assumptions

- Postgres service hostname: `postgres` (Azure PostgreSQL Flexible Server)
- Postgres port: `5432`
- Postgres database user: `odoo`
- Postgres database password: resolved via Key Vault + managed identity
- Odoo service port: `8069`
- Public URL: `https://erp.insightpulseai.com`

## Database

- `odoo` — single production database
- Data source: live operational data
- PITR enabled via Azure PostgreSQL

## Production behavior

- `workers = 4` — multi-process for concurrent request handling
- `max_cron_threads = 2` — all crons active
- `proxy_mode = True` — behind Azure Front Door
- `list_db = False` — no database selector
- SMTP via Zoho (`smtppro.zoho.com:587`) — live email delivery
- All integrations live
- Payment providers in production mode

## Secrets

All secrets resolved at runtime via Azure Key Vault (`kv-ipai-dev`):

| Secret | Key Vault Name | Env Var |
|--------|---------------|---------|
| DB password | `odoo-db-password` | `PGPASSWORD` |
| SMTP user | `zoho-smtp-user` | `ZOHO_SMTP_USER` |
| SMTP password | `zoho-smtp-password` | `ZOHO_SMTP_PASSWORD` |
| Admin password | Disabled (`False`) | — |

No credentials in `odoo.conf`. The `db_password = odoo` line is a template
placeholder — actual value injected via container env var at runtime.

## Backup

- Daily backup, 30-day retention
- Point-in-time restore via Azure PostgreSQL
- Filestore synced to Azure Blob Storage

## Access

- All authorized users
- Public-facing at `erp.insightpulseai.com`

## Related

- `config/dev/` — local development config
- `config/staging/` — staging with safety controls
- `ssot/governance/azure-odoosh-equivalent.yaml` — environment model
