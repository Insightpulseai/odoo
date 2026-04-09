# CP-6: Database-per-Tenant Routing Validation

> **Date:** 2026-03-20T00:10:00Z
> **Status:** DONE

## Evidence

### Container Environment Variables (ipai-odoo-dev-web)

```
Name                Value                                         SecretRef
------------------  --------------------------------------------  -----------
HOST                ipai-odoo-dev-pg.postgres.database.azure.com
PORT                5432
USER                odoo_admin
PASSWORD                                                          db-password
db_name             odoo
dbfilter            ^odoo$
ODOO_STAGE          production
ODOO_DATA_DIR       /var/lib/odoo
AZURE_FRONTDOOR_ID  38c7f9ab-c904-4c47-ad53-4b9fb1abea8e
```

### Validation

- `dbfilter = ^odoo$` — strictly routes all requests to the `odoo` database
- `db_name = odoo` — explicit database name set
- Database manager is blocked (smoke test CP-7 confirms `/web/database/selector` returns "disabled by the administrator")
- `list_db` is enforced by the DB manager block (confirmed via smoke test)

### Method

```bash
az containerapp show --name ipai-odoo-dev-web --resource-group rg-ipai-dev \
  --query "properties.template.containers[0].env[]" -o table
```
