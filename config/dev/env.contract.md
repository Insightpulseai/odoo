# Dev Environment Contract

## Purpose

Documents the expected local-dev runtime inputs for `config/dev/odoo.conf`.

## Required runtime assumptions

- Postgres service hostname: `db`
- Postgres port: `5432`
- Postgres database user: `odoo`
- Postgres database password: `odoo`
- Odoo service port: `8069`
- Odoo gevent/longpolling port: `8072`

## Required mount paths

- `/mnt/oca` — OCA addons
- `/mnt/extra-addons/ipai` — IPAI bridge modules
- `/mnt/extra-addons/local` — local/custom addons

## Canonical local DB names

- `odoo_dev` — primary development database (no demo data)
- `odoo_dev_demo` — development database with demo/showroom data if needed

## Dev-specific behavior

- `workers = 0` — single-process mode for debugger attachment
- `max_cron_threads = 1` — minimal cron for local dev
- `dev_mode = xml,reload,qweb,werkzeug` — full dev ergonomics
- `without_demo = all` — clean DB by default
- `logfile = False` — logs to stdout
- SMTP points to Mailpit on port 1025

## Non-goals

- No production secrets
- No production hostnames
- No TLS/proxy assumptions unless the local runtime actually uses them
- No internet-facing configuration

## Related

- `config/staging/` — rehearsal / pre-prod-like config
- `config/prod/` — production-optimized config
