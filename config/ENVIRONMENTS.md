# Odoo Environment Configuration — Index

> Three environments. No more, no less.
> Doctrine: `docs/architecture/azure/AZURE_ODOOSH_EQUIVALENT.md`
> SSOT: `ssot/governance/azure-odoosh-equivalent.yaml`

## Environment Matrix

| Property | dev | staging | production |
|----------|-----|---------|------------|
| Config path | `config/dev/` | `config/staging/` | `config/prod/` |
| Database | `odoo_dev` | `odoo_staging` | `odoo` |
| Workers | 0 (single-process) | 2 | 4+ |
| Mail | Mailpit sink (1025) | MailHog sink (1025) | Zoho SMTP (587) |
| Cron | 1 thread, local only | Gated (whitelist) | Live (2 threads) |
| Integrations | Local/mock | Sandbox | Live |
| Payments | N/A | Test mode | Live |
| Data source | Seed / fixtures | Sanitized prod snapshot | Live |
| Public URL | `erp-dev.insightpulseai.com` | `erp-staging.insightpulseai.com` | `erp.insightpulseai.com` |
| `list_db` | `True` (dev only) | `False` | `False` |
| `proxy_mode` | `False` | `True` | `True` |
| Dev mode | `xml,reload,qweb,werkzeug` | Off | Off |
| Backup | None | Daily / 7-day | Daily / 30-day + PITR |

## Per-environment files

Each environment directory contains:

| File | Purpose |
|------|---------|
| `odoo.conf` | Odoo server configuration (runtime) |
| `features.yaml` | Machine-readable feature flags and safety controls |
| `env.contract.md` | Human-readable environment contract |

## Rules

1. **Three environments only**: `dev`, `staging`, `production`
2. **Auxiliary DB**: `odoo_dev_demo` is on-demand, not a separate environment
3. **Test DBs**: `test_<module>` are disposable, never shared
4. **No secrets in config files**: Credentials via Key Vault / env vars at runtime
5. **Staging is never production**: Mail sink, gated crons, sandboxed integrations
6. **Dev is never staging**: Single-process, dev mode, local-only
7. **Addons paths must match staging↔prod**: Parity prevents "works in staging" failures
