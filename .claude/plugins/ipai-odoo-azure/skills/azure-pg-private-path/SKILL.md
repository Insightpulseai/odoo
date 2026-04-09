---
name: azure-pg-private-path
description: Azure PostgreSQL Flexible Server management for Odoo databases
triggers:
  - keywords: ["PostgreSQL", "pg-ipai", "flexible server", "database", "connection string"]
layer: B-platform
---

# Azure PostgreSQL Private Path Skill

Database topology:

1. Server: `pg-ipai-odoo` (General Purpose, southeastasia)
2. Databases: `odoo` (prod), `odoo_dev` (dev), `odoo_staging` (staging)
3. Test databases: `test_<module>` (disposable, created/dropped per test run)
4. Never use prod/dev/staging DBs for tests
5. Connection: private endpoint from ACA subnet only — no public access
6. Auth: password via Key Vault secret `odoo-db-password` (managed identity binding)
7. SSL mode: `require` (never `disable` or `prefer`)
8. Backup: Azure-managed PITR (7-day retention minimum)
9. Extensions allowed: `uuid-ossp`, `pgcrypto`, `unaccent` (Odoo standard set)
10. Never run `DROP DATABASE` on `odoo`, `odoo_dev`, or `odoo_staging` without explicit user confirmation
11. Fabric mirroring: enabled for analytics (read replica to Databricks via OneLake)
12. Connection string pattern: `host=pg-ipai-odoo.postgres.database.azure.com dbname=<db> user=<user> sslmode=require`
