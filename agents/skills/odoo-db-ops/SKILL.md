# Odoo DB Ops Skill

## Purpose

Manage Odoo databases via CLI. Covers database creation, duplication, backup, restore, and the --database flag. Enforces the canonical database naming convention.

## Owner

odoo-cli-operator

## Preconditions

- Odoo CE 18.0 installed
- PostgreSQL 16 accessible
- Database user has createdb privileges (for local dev)
- Sufficient disk space for backups

## Covered Operations

### Database Flag

- `odoo-bin --database <name>` — target a specific database
- `odoo-bin -d <name>` — shorthand for --database

### Database Creation

- `odoo-bin --database <name> --init base` — create database with base module
- `odoo-bin --database <name> --init base --without-demo all` — create without demo data
- `createdb -U <user> <name>` — create empty PostgreSQL database (before Odoo init)

### Database Operations via Web Service

- Backup: `POST /web/database/backup` (requires admin password)
- Restore: `POST /web/database/restore` (requires admin password)
- Duplicate: `POST /web/database/duplicate` (requires admin password)
- Drop: `POST /web/database/drop` (destructive, requires admin password)

### Database Operations via PostgreSQL

- `pg_dump <db> > backup.sql` — raw PostgreSQL backup
- `pg_restore -d <db> < backup.sql` — raw PostgreSQL restore
- `psql -d <db> -c "SELECT ..."` — direct query (read-only debugging)

## Canonical Database Names

| Database | Purpose | Environment |
|----------|---------|-------------|
| `odoo_dev` | Clean development | Local / devcontainer |
| `odoo_dev_demo` | Demo/showroom with demo data | Local / devcontainer |
| `odoo_staging` | Staging rehearsal | Staging ACA |
| `odoo` | Production | Production ACA |
| `test_<module>` | Disposable test databases | Any (never canonical) |

## Disallowed Operations

- Creating databases with names outside the canonical set
- Dropping production database from dev machine
- Using `odoo_dev` or `odoo_staging` for test runs (use `test_<module>`)
- Direct SQL writes to production database

## Verification

- After create: `psql -d <db> -c "SELECT 1"` succeeds
- After init: `psql -d <db> -c "SELECT state FROM ir_module_module WHERE name='base'"` returns `installed`
- After backup: file exists and size > 0
- After restore: Odoo starts and `/web/health` returns 200
