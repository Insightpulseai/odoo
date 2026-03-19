# Odoo Dataset Neutralize & Populate Ops Skill

## Purpose

Neutralize and populate Odoo databases via CLI. Covers odoo-bin neutralize (strip production data for safe sharing), odoo-bin populate (generate demo/test data), and safe data handling practices.

## Owner

odoo-cli-operator

## Preconditions

- Odoo CE 19.0 installed
- Target database exists
- Backup taken before neutralization (irreversible data modification)

## Covered Operations

### Neutralize

- `odoo-bin neutralize --database <db>` — strip sensitive production data
- Neutralization removes/anonymizes: emails, passwords, API keys, SMTP config, cron jobs, webhook URLs
- Preserves: module structure, views, reports, business logic configuration
- Result: database safe for development/sharing

### Populate

- `odoo-bin populate --database <db> --models <model1,model2>` — generate test data
- `odoo-bin populate --database <db> --size <small|medium|large>` — generate data with size hint
- Modules must implement `_populate_factories` and `_populate_sizes` for populate to work
- Default populate creates realistic-looking but fake data

### Workflow

1. Backup production database
2. Restore to development database name
3. Run neutralize to strip sensitive data
4. Optionally run populate to add test data
5. Verify database is safe (no real emails, no real credentials)

## Disallowed Operations

- Neutralizing production database in-place (always work on a copy)
- Populating production database with test data
- Sharing non-neutralized production data
- Running neutralize without a backup

## Verification

- After neutralize: check `ir_mail_server` has no real SMTP credentials
- After neutralize: check `res_users` passwords are reset
- After neutralize: check `ir_cron` jobs are disabled
- After populate: check target models have expected record counts
