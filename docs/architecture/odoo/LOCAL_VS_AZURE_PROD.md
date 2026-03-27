# Odoo Architecture: Local Dev vs Azure Production

> Canonical reference for how Odoo runs locally vs in production.
> Source of truth for runtime topology decisions.

---

## Principle

Local dev does **not** replicate Azure networking, HA, or WAF.
Local dev preserves the **same code, addons, and config structure** as prod.

---

## Local = Fast, Deterministic Dev Sandbox

| Item | Value |
|------|-------|
| **Runtime** | `docker compose up -d` in `infra/` |
| **Config** | `config/dev/odoo.conf` |
| **Odoo mode** | Single-process (`workers=0`) |
| **Database** | PostgreSQL 16 (local container, port 5433 external) |
| **Databases** | `odoo_dev`, `odoo_dev_demo` |
| **Addons** | `addons/oca` → `/mnt/oca`, `addons/ipai` → `/mnt/extra-addons/ipai` |
| **SMTP** | Mailpit (port 1025, no real mail delivery) |
| **Proxy** | Nginx on port 80 (optional, for local parity testing) |
| **Filestore** | Docker volume `odoo-web-data` |
| **`list_db`** | `True` (dev convenience) |
| **`dbfilter`** | `^odoo(_dev|_dev_demo)?$` |
| **`dev_mode`** | `xml,reload,qweb,werkzeug` |
| **Redis** | Local container (queue_job support) |

### What local does NOT have

- Azure Front Door / WAF
- Multi-process workers
- Private VNet networking
- Zone-redundant database HA
- Application Insights / Log Analytics
- Key Vault managed identity bindings
- Split runtime (web/worker/cron)

These are **production concerns only**. Forcing them locally adds complexity without development value.

---

## Production on Azure = Private, Split, Observable

```
Internet
  │
  ▼
Cloudflare DNS (authoritative)
  │
  ▼
Azure Front Door + WAF ─── TLS termination, DDoS, geo-routing
  │
  ├── /web/*         → ipai-odoo-dev-web    (ACA, port 8069)
  ├── /websocket/*   → ipai-odoo-dev-web    (gevent worker, longpoll)
  └── (blocked)      → origins reject non-AFD traffic
                          │
                          ├── ipai-odoo-dev-worker  (background jobs)
                          ├── ipai-odoo-dev-cron    (scheduled actions)
                          │
                          ▼
                    Azure Database for PostgreSQL
                    Flexible Server (private VNet)
                    ├── DB: odoo (prod)
                    ├── HA: zone-redundant
                    └── Backup: automated + PITR
```

| Item | Value |
|------|-------|
| **Config** | `config/prod/odoo.conf` (credentials from env vars via Key Vault) |
| **Odoo mode** | Multi-process (`workers=4`) |
| **Database** | Azure PostgreSQL Flexible Server (private VNet access) |
| **Database name** | `odoo` |
| **Runtime split** | `web` (HTTP), `worker` (queue_job), `cron` (ir.cron) |
| **Ingress** | Azure Front Door → origin lockdown (no bypass) |
| **SMTP** | Zoho SMTP (`smtp.zoho.com:587`, TLS, credentials from Key Vault) |
| **`proxy_mode`** | `True` (required behind Front Door) |
| **`list_db`** | `False` (security lockdown) |
| **`dbfilter`** | `^odoo$` (strict single database) |
| **`admin_passwd`** | `False` (disabled) |
| **`web.base.url`** | `https://erp.insightpulseai.com` |
| **Observability** | Application Insights + Azure Monitor + Log Analytics |
| **Secrets** | Azure Key Vault (`kv-ipai-dev`) via managed identity |
| **Filestore** | Azure Files (persistent, shared across web/worker/cron) |

---

## Staging = Prod-Like Sandbox

| Item | Value |
|------|-------|
| **Config** | `config/staging/odoo.conf` |
| **Workers** | 2 (reduced from prod) |
| **Database** | `odoo_staging` |
| **SMTP** | MailHog sink (all mail captured, none delivered) |
| **`proxy_mode`** | `True` |
| **`web.base.url`** | `https://erp-staging.insightpulseai.com` |

---

## Azure ACA Template

`config/azure/odoo.conf` is the base for all ACA deployments.
Database credentials are **not in the config file** — they come from Azure env vars
injected via Key Vault managed identity bindings.

---

## What Is NOT Correct Setup

| Anti-pattern | Why |
|-------------|-----|
| Exposing Odoo directly to internet without reverse proxy | No `proxy_mode`, IP detection breaks, no TLS termination |
| Running prod with `workers=0` | Single-threaded, no concurrency, no crash isolation |
| Public PostgreSQL endpoint | Attack surface; use private VNet access |
| `/web/database/*` exposed on internet | Database manager allows create/drop/backup — must be blocked |
| `list_db = True` in production | Leaks database names to unauthenticated users |
| Filestore treated as disposable | Attachments, reports, images lost if not backed up with DB |
| Local dev mimicking full Azure topology | Adds complexity with zero development value |

---

## Config File Map

| Tier | File | Database | Workers | SMTP | Proxy |
|------|------|----------|---------|------|-------|
| dev | `config/dev/odoo.conf` | `odoo_dev` | 0 | Mailpit:1025 | No |
| staging | `config/staging/odoo.conf` | `odoo_staging` | 2 | MailHog:1025 | Yes |
| prod | `config/prod/odoo.conf` | `odoo` | 4 | Zoho:587 | Yes |
| azure | `config/azure/odoo.conf` | `odoo` (env vars) | 4 | Zoho:587 | Yes |

---

## References

- [Odoo 19 Deployment Guide](https://www.odoo.com/documentation/19.0/administration/on_premise/deploy.html)
- [Azure Front Door Origin Security](https://learn.microsoft.com/en-us/azure/frontdoor/origin-security)
- [Azure PostgreSQL Flexible Server Private Access](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-networking-private)

---

*Last updated: 2026-03-18*
