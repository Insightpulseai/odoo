# Physical Schema Snapshot

This directory holds generated physical schema from a live reference database.
NOT hand-authored — generated via:

```bash
pg_dump -s -n public -n ops -n platform \
  -h pg-ipai-odoo.postgres.database.azure.com \
  -U ipaiadmin -d odoo_dev \
  > evidence/schema/odoo_reference_schema.sql
```

Status: BLOCKED on PG auth (ipaiadmin password not in KV).
Unblock: reset password via Azure Portal → pg-ipai-odoo → Compute + storage → Admin password.

Once generated, also export as DBML:
```bash
sql2dbml evidence/schema/odoo_reference_schema.sql --postgres > evidence/schema/odoo_reference_schema.dbml
```
