# Blocker 2: PG PITR Restore Test

> Evidence: point-in-time restore to temporary server succeeded

## Date

2026-04-05T00:54Z

## Source Server

- Name: `pg-ipai-odoo`
- Resource Group: `rg-ipai-dev-odoo-data`
- SKU: `Standard_D2ds_v5`
- Version: PostgreSQL 16
- Backup retention: 35 days
- Earliest restore point: 2026-03-21T06:26:44Z
- Geo-redundant backup: Disabled

## Restore Parameters

- Restore point: 2026-04-05T00:24:12Z (30 minutes before test)
- Target server: `pg-ipai-odoo-restore-test`

## Result

- State: `Ready`
- FQDN: `pg-ipai-odoo-restore-test.postgres.database.azure.com`

## Database Integrity Check

All 3 Odoo databases restored:

| Database | Present |
|---|---|
| `odoo` (production) | Yes |
| `odoo_dev` (development) | Yes |
| `odoo_staging` (staging) | Yes |
| `postgres` (system) | Yes |
| `azure_maintenance` | Yes |
| `azure_sys` | Yes |

## Verdict

**PASS** — PITR restore works. Blocker 2 closed.

## Remaining Gaps

- Geo-redundant backup: Disabled (single-region risk)
- No DR rehearsal across regions
- Restore timing not benchmarked (should measure RTO)

## Impact on Assessment

- Reliability: +0.5 (backup restore unproven -> proven)

## Cleanup

Test server `pg-ipai-odoo-restore-test` should be deleted after evidence capture.
