# Canonical Odoo Database Naming

Canonical Odoo database naming is environment-based only:

| Environment | Database       | Runtime                                    | Config                    |
|-------------|----------------|--------------------------------------------|---------------------------|
| local dev   | `odoo_dev`     | local Docker / devcontainer                | `config/dev/odoo.conf`    |
| demo        | `odoo_dev_demo`| local Docker / devcontainer (on-demand)    | `config/dev/odoo.conf`    |
| staging     | `odoo_staging` | staging ACA apps                           | `config/stage/odoo.conf`  |
| prod        | `odoo`         | prod ACA apps                              | `config/prod/odoo.conf`   |

## Rules

- Local runtime connects only to `odoo_dev`.
- Azure Container Apps staging connects only to `odoo_staging`.
- Azure Container Apps production connects only to `odoo`.
- `list_db = False` in all environments.
- `dbfilter` must match exactly one database per environment.
- Test databases use `test_<module>` pattern (disposable, never shared).

## Deprecated names (never use)

| Name | Replacement | Date |
|------|-------------|------|
| `odoo_prod` | `odoo` | 2026-03 |
| `odoo_core` | `odoo_dev` (local) / `odoo` (prod) | 2026-03 |
| `odoo_db` | `odoo_dev` | 2026-03 |
| `odoo_stage` | `odoo_staging` | 2026-03 |

## Hostname vs environment authority

PostgreSQL server hostnames are **not** authoritative for environment classification.
Environment classification is determined by canonical database names only.

| Database | Environment | Authoritative? |
|----------|-------------|----------------|
| `odoo` | production | Yes — name is the authority |
| `odoo_staging` | staging | Yes — name is the authority |
| `odoo_dev` | local control development | Yes — name is the authority |
| `odoo_dev_demo` | local demo/showroom | Yes — name is the authority |

The Azure PostgreSQL server `ipai-odoo-dev-pg` hosts both `odoo` (production) and `odoo_staging` (staging). The `-dev-` in the server hostname is a legacy naming artifact from initial provisioning — it does not indicate environment. Do not use the server hostname to infer which environment a database belongs to.

## Cross-References

- `docs/contracts/PROD_DB_RUNTIME_CONTRACT.md` — confirms prod = `odoo`
- `spec/odoo-sh-azure-equivalent/constitution.md` — confirms prod = `odoo`
- `ssot/governance/project-charter.yaml` — canonical environment naming

---

*Last updated: 2026-03-17*
