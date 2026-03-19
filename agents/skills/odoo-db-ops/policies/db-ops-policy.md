# Database Ops Policy

## Naming Enforcement

- Only canonical names allowed: odoo_dev, odoo_dev_demo, odoo_staging, odoo
- Test databases must follow pattern: test_<module_name>
- Deprecated names are rejected: odoo_core, odoo_prod, odoo_db, odoo_stage

## Backup Rules

- Backup before any destructive operation
- Production backups managed by Azure (not this skill)
- Local backups stored in /tmp/ with timestamp in filename
- Backup format: gzipped SQL dump (pg_dump | gzip)

## Restore Rules

- Never restore into a database that is currently running Odoo
- Always restore to a new/separate database name first, verify, then swap
- Production restores require explicit approval and follow incident protocol

## Drop Rules

- Test databases (test_<module>) can be dropped freely
- odoo_dev can be dropped and recreated (development database)
- odoo_staging and odoo must never be dropped from dev machines
- Always confirm database name before drop

## Access Control

- Local dev: user `tbwa` with createdb privileges
- Devcontainer: user `odoo` connecting to `db` service
- Production: managed identity via Azure, no direct access

## Data Classification

- odoo_dev: no sensitive data, safe to share
- odoo_dev_demo: demo data only, safe to share
- odoo_staging: may contain sanitized production-like data
- odoo: production data, never accessible from dev
