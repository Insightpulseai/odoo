# Canonical Odoo Database Naming

Canonical Odoo database naming is environment-based only:

| Environment | Database       | Runtime                                    | Config                    |
|-------------|----------------|--------------------------------------------|---------------------------|
| local dev   | `odoo_dev`     | local Docker / devcontainer                | `config/dev/odoo.conf`    |
| staging     | `odoo_staging` | staging ACA apps                           | `config/stage/odoo.conf`  |
| prod        | `odoo_prod`    | prod ACA apps                              | `config/prod/odoo.conf`   |

## Rules

- Local runtime connects only to `odoo_dev`.
- Azure Container Apps staging connects only to `odoo_staging`.
- Azure Container Apps production connects only to `odoo_prod`.
- No bare `odoo` database name. No `odoo_core`. No `odoo_db`.
- `list_db = False` in all environments.
- `dbfilter` must match exactly one database per environment.

## Deprecated names (never use)

| Name | Replacement | Date |
|------|-------------|------|
| `odoo_core` | `odoo_dev` (local) / `odoo_prod` (prod) | 2026-03 |
| `odoo` (bare) | `odoo_prod` | 2026-03 |
| `odoo_db` | `odoo_dev` | 2026-03 |
| `odoo_stage` | `odoo_staging` | 2026-03 |
