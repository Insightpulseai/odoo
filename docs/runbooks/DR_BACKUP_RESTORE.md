# Disaster Recovery: Backup and Restore Runbook

> SSOT for RPO/RTO targets and PostgreSQL restore procedures.

---

## Recovery Targets

| Metric | Target | Mechanism |
|--------|--------|-----------|
| **RPO** | 1 hour | PG Flexible Server continuous backup (WAL archiving) |
| **RTO** | 4 hours | Manual restore + ACA redeployment |

---

## Backup Configuration (IaC-enforced)

- **Retention**: 35 days (`backupRetentionDays: 35` in `postgres-flexible.bicep`)
- **Geo-redundant backup**: Enabled (`geoRedundantBackup: 'Enabled'`)
- **High availability**: Zone-redundant (`highAvailability.mode: 'ZoneRedundant'`)
- **Storage auto-grow**: Enabled

---

## Restore Procedure

### Prerequisites

- Azure CLI authenticated (`az login`)
- Contributor role on `rg-ipai-dev-odoo-data`
- Target restore time in UTC (ISO 8601)

### Step 1: Identify the restore point

```bash
# List available backup metadata
az postgres flexible-server show \
  --resource-group rg-ipai-dev-odoo-data \
  --name pg-ipai-odoo \
  --query "{earliestRestore:backup.earliestRestoreDate, retention:backup.backupRetentionDays, geoRedundant:backup.geoRedundantBackup}"
```

### Step 2: Point-in-time restore to a new server

```bash
# Restore to a new server (never restore in-place)
az postgres flexible-server restore \
  --resource-group rg-ipai-dev-odoo-data \
  --name pg-ipai-odoo-restore-$(date +%Y%m%d%H%M) \
  --source-server pg-ipai-odoo \
  --restore-time "2026-03-24T10:00:00Z"
```

Replace `--restore-time` with the desired UTC timestamp (must be within the 35-day retention window and after `earliestRestoreDate`).

### Step 3: Verify the restored database

```bash
# Connect and verify row counts on critical tables
az postgres flexible-server connect \
  --name pg-ipai-odoo-restore-YYYYMMDDHHMM \
  --admin-user odoo_admin \
  --admin-password-env PGPASSWORD \
  --database-name odoo \
  --querytext "SELECT schemaname, relname, n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC LIMIT 20;"
```

### Step 4: Swap connection strings

1. Update Key Vault secret `odoo-pg-host` to point to the restored server FQDN.
2. Restart ACA revisions to pick up the new connection:

```bash
for app in ipai-odoo-dev-web ipai-odoo-dev-worker ipai-odoo-dev-cron; do
  az containerapp revision restart \
    --resource-group rg-ipai-dev-odoo-runtime \
    --name "$app"
done
```

### Step 5: Validate application health

```bash
# Verify Odoo responds
curl -sf https://erp.insightpulseai.com/web/login | grep -q "Log in" && echo "PASS" || echo "FAIL"

# Verify database version selector is disabled (list_db=False)
curl -sf https://erp.insightpulseai.com/web/database/selector | grep -q "403\|404" && echo "PASS" || echo "FAIL"
```

### Step 6: Decommission the old server (after validation)

```bash
# Only after confirming the restored server is healthy
az postgres flexible-server delete \
  --resource-group rg-ipai-dev-odoo-data \
  --name pg-ipai-odoo \
  --yes
```

---

## Geo-Restore (Region Failure)

If the primary region (`southeastasia`) is unavailable:

```bash
az postgres flexible-server geo-restore \
  --resource-group rg-ipai-dr \
  --name pg-ipai-odoo-geo-restore \
  --source-server /subscriptions/536d8cf6-89e1-4815-aef3-d5f2c5f4d070/resourceGroups/rg-ipai-dev-odoo-data/providers/Microsoft.DBforPostgreSQL/flexibleServers/pg-ipai-odoo \
  --location eastasia
```

---

## DR Drill Schedule

| Frequency | Scope | Owner |
|-----------|-------|-------|
| **Quarterly** | Full PITR restore to new server, validate, teardown | Platform Owner |
| **Monthly** | Verify backup status via `az postgres flexible-server show` | Platform Owner |

---

## Evidence Template (for drill results)

Save to `docs/evidence/<YYYYMMDD-HHMM>/dr-drill/`:

```
drill_date: YYYY-MM-DD
restore_point_used: <ISO 8601 UTC>
restored_server_name: pg-ipai-odoo-restore-YYYYMMDDHHMM
restore_duration_minutes: <N>
row_count_validation: PASS|FAIL
application_health: PASS|FAIL
total_rto_minutes: <N>
meets_rto_target: true|false  # target: 240 min
notes: <any issues encountered>
```

---

*Last updated: 2026-03-24*
