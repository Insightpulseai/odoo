# Runbook: Azure PostgreSQL CLI Operations

This runbook provides automated CLI commands for managing the **ipai-odoo-dev-pg** flexible server.

## 1. Prerequisites
Ensure the Azure CLI is installed and you are logged in:
```bash
az login
az extension add --name postgres-flexible
```

## 2. Common Operations

### A. Quick Connection (psql)
Connect directly to the database without manual password entry (uses Azure CLI auth):
```bash
az postgres flexible-server connect \
    --name ipai-odoo-dev-pg \
    --admin-user odoo_admin \
    --database-name postgres \
    --interactive
```

### B. Execute SQL File
Execute a local SQL script (e.g., for schema updates or data seeding):
```bash
az postgres flexible-server execute \
    --name ipai-odoo-dev-pg \
    --admin-user odoo_admin \
    --database-name postgres \
    --file-path ./scripts/my_seed_script.sql
```

### C. Show Connection Strings
Generate formatted connection strings for various languages:
```bash
az postgres flexible-server show-connection-string \
    --server-name ipai-odoo-dev-pg \
    --database-name postgres
```

### D. Manage Firewall Rules
Whitelist a specific IP address for development access:
```bash
az postgres flexible-server firewall-rule create \
    --name ipai-odoo-dev-pg \
    --rule-name AllowMyIP \
    --start-ip-address <YOUR_IP> \
    --end-ip-address <YOUR_IP>
```

## 3. Health & Status
Check the current state and parameters of the server:
```bash
az postgres flexible-server show --name ipai-odoo-dev-pg
az postgres flexible-server parameter list --server-name ipai-odoo-dev-pg
```

---
**Resource URI**: `ipai-odoo-dev-pg.postgres.database.azure.com`
**Managed by**: Agent Factory Platform Ops
