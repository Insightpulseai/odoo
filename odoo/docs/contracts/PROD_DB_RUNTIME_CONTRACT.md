# Production Database Runtime Contract

> **Contract ID**: C-PROD-DB-RUNTIME
> **Status**: Active
> **Created**: 2026-03-13
> **Owner**: Platform / DevOps

---

## Canonical Production Database

| Parameter | Value | Source |
|-----------|-------|--------|
| Database name | `odoo` | `config/azure/odoo.conf`, `config/prod/odoo.conf` |
| Database filter | `^odoo$` | Same config files |
| ACA runtime flag | `-d odoo --db-filter '^odoo$'` | Container command args |
| PostgreSQL server | `ipai-odoo-dev-pg.postgres.database.azure.com` | ACA env var `HOST` |
| Admin user | `odoo_admin` | ACA env var `USER` |

## Non-Canonical / Legacy

| Name | Status | Notes |
|------|--------|-------|
| `odoo_prod` | **Deprecated** | Legacy name, may still contain data. Do not target from runtime. Do not delete until data comparison is complete. |
| `odoo_core` | Deprecated | Never use. |
| `odoo_db` | Deprecated | Never use. |

## Canonical Database Model (All Environments)

| Database | Purpose | Runtime |
|----------|---------|---------|
| `odoo_dev` | Clean control development DB — base only, no demo data | local Docker / devcontainer |
| `odoo_dev_demo` | Auxiliary development showroom/demo DB — demo data enabled | local Docker / devcontainer |
| `odoo_staging` | Staging rehearsal DB — mirrors production topology | staging ACA apps |
| `odoo` | Production DB | prod ACA apps |

## Rules

1. **Never** set `db_name` to `odoo_prod` in any config file or container command.
2. **Never** delete `odoo_prod` from the PG server until a data comparison proves it is obsolete.
3. All config files (`config/azure/odoo.conf`, `config/prod/odoo.conf`) must contain `db_name = odoo` and `dbfilter = ^odoo$`.
4. The ACA container command must use `-d odoo --db-filter '^odoo$'`.
5. Test databases use `test_<module_name>` pattern — never any of the 4 canonical DBs.

## Validation

Contract compliance is enforced by `tests/contracts/test_prod_db_contract.py`.

## Known Residual Issues (as of 2026-03-13)

- `web.assets_frontend_minimal.min.js` returns HTTP 500 — asset compilation defect, not a DB routing issue.
- `odoo_prod` database still exists on PG server — data truth comparison pending.
