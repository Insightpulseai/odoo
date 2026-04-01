# Fabric Mirroring Rehearsal Runbook

> **Scope**: First rehearsal -- `odoo_staging` database only on `pg-ipai-odoo`.
> **Owner**: Data Platform team
> **Status**: Pre-flight
> **Last reviewed**: 2026-03-30

---

## Overview

This runbook documents the end-to-end rehearsal for enabling Microsoft Fabric Mirroring from the Odoo PostgreSQL server (`pg-ipai-odoo`) to a Fabric workspace via OneLake. The rehearsal uses only the `odoo_staging` database. Production (`odoo`) is out of scope until rehearsal is validated and a 48-hour soak period completes.

### Architecture Context

```text
pg-ipai-odoo (Azure PG Flexible, General Purpose)
    |
    |-- database: odoo_staging (rehearsal target)
    |
    v
Fabric Mirroring (CDC via logical replication)
    |
    v
OneLake (Delta tables, Bronze layer)
    |
    v
Databricks / Power BI (consumption -- post-rehearsal)
```

Fabric Mirroring is the **tactical complement** to the primary Databricks-first analytics path. It provides near-real-time CDC replication for operational dashboards. It does NOT replace the governed medallion pipeline. See `docs/architecture/DATABRICKS_FABRIC_ROLE_SPLIT.md`.

---

## 1. Pre-Flight Checklist

Complete all items before initiating the mirroring setup in the Fabric portal.

### 1.1 PostgreSQL Server Readiness

| Check | Expected Value | Verified |
|-------|---------------|----------|
| Server name | `pg-ipai-odoo` | [ ] |
| Resource group | `rg-ipai-dev-odoo-data` | [ ] |
| Region | Southeast Asia | [ ] |
| SKU tier | General Purpose (required for mirroring) | [ ] |
| PostgreSQL version | 16 | [ ] |
| `wal_level` | `logical` | [ ] |
| `max_worker_processes` | >= 8 (currently 11) | [ ] |
| `max_replication_slots` | >= 4 (must have headroom for mirroring) | [ ] |
| Public network access | Enabled (required for Fabric to connect) | [ ] |
| Firewall rule for Fabric | Azure services allowed | [ ] |
| Database `odoo_staging` exists | Yes | [ ] |
| Table ownership | All tables owned by `azure_pg_admin` or the admin login | [ ] |

### 1.2 Fabric Capacity

| Check | Expected Value | Verified |
|-------|---------------|----------|
| Fabric capacity provisioned | Yes (F2 minimum for dev/test) | [ ] |
| Capacity name | `fabric-ipai-dev` (or as provisioned) | [ ] |
| Capacity region | Southeast Asia (same as PG server) | [ ] |
| Capacity state | Active | [ ] |
| Admin members include platform owner | Yes | [ ] |

### 1.3 Fabric Workspace

| Check | Expected Value | Verified |
|-------|---------------|----------|
| Workspace exists | Yes (create if not) | [ ] |
| Workspace assigned to Fabric capacity | Yes | [ ] |
| Workspace name | `ipai-data-mirror-dev` (or equivalent) | [ ] |

### 1.4 Identity and Access

| Check | Expected Value | Verified |
|-------|---------------|----------|
| PG admin credentials available | Via Azure Key Vault (`kv-ipai-dev`) | [ ] |
| Fabric workspace member with Contributor role | Platform owner Entra account | [ ] |
| No hardcoded credentials | Verified -- all via Key Vault | [ ] |

### 1.5 DDL Freeze Confirmation

| Check | Expected Value | Verified |
|-------|---------------|----------|
| No pending Odoo module installs on `odoo_staging` | Confirmed | [ ] |
| No pending schema migrations | Confirmed | [ ] |
| DDL freeze communicated to dev team | Yes | [ ] |
| TRUNCATE operations prohibited during rehearsal | Communicated | [ ] |

---

## 2. Verify PG Server Readiness (Azure CLI)

Run these commands to confirm the server is ready for mirroring.

### 2.1 Verify Server Exists and Check SKU

```bash
az postgres flexible-server show \
  --resource-group rg-ipai-dev-odoo-data \
  --name pg-ipai-odoo \
  --query '{name:name, state:state, version:version, sku:sku, location:location}' \
  --output table
```

**Expected**: State = `Ready`, Version = `16`, SKU tier = `GeneralPurpose`.

### 2.2 Verify WAL Level

```bash
az postgres flexible-server parameter show \
  --resource-group rg-ipai-dev-odoo-data \
  --server-name pg-ipai-odoo \
  --name wal_level \
  --query '{name:name, value:value, source:source}' \
  --output table
```

**Expected**: `value = logical`. If not `logical`, set it:

```bash
az postgres flexible-server parameter set \
  --resource-group rg-ipai-dev-odoo-data \
  --server-name pg-ipai-odoo \
  --name wal_level \
  --value logical
```

**Note**: Changing `wal_level` requires a server restart (see section 2.6).

### 2.3 Verify Replication Slots Capacity

```bash
az postgres flexible-server parameter show \
  --resource-group rg-ipai-dev-odoo-data \
  --server-name pg-ipai-odoo \
  --name max_replication_slots \
  --query '{name:name, value:value}' \
  --output table
```

**Expected**: Value >= 4. Fabric Mirroring uses one replication slot per mirrored database.

### 2.4 Verify Worker Processes

```bash
az postgres flexible-server parameter show \
  --resource-group rg-ipai-dev-odoo-data \
  --server-name pg-ipai-odoo \
  --name max_worker_processes \
  --query '{name:name, value:value}' \
  --output table
```

**Expected**: Value >= 8 (currently 11).

### 2.5 Verify Database Exists

```bash
az postgres flexible-server db show \
  --resource-group rg-ipai-dev-odoo-data \
  --server-name pg-ipai-odoo \
  --database-name odoo_staging \
  --query '{name:name, charset:charset, collation:collation}' \
  --output table
```

**Expected**: Database exists, collation = `en_US.utf8`.

### 2.6 Verify Firewall (Allow Azure Services)

```bash
az postgres flexible-server firewall-rule list \
  --resource-group rg-ipai-dev-odoo-data \
  --name pg-ipai-odoo \
  --output table
```

**Expected**: A rule allowing Azure services (start IP `0.0.0.0`, end IP `0.0.0.0`) exists. If not:

```bash
az postgres flexible-server firewall-rule create \
  --resource-group rg-ipai-dev-odoo-data \
  --name pg-ipai-odoo \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### 2.7 Restart Server (if parameter changes were made)

```bash
az postgres flexible-server restart \
  --resource-group rg-ipai-dev-odoo-data \
  --name pg-ipai-odoo
```

**Impact**: Server restart causes ~30-60 seconds of downtime. All connected Odoo instances using this server will briefly lose database connectivity. Schedule during a maintenance window.

**Wait**: Confirm server returns to `Ready` state:

```bash
az postgres flexible-server show \
  --resource-group rg-ipai-dev-odoo-data \
  --name pg-ipai-odoo \
  --query 'state' \
  --output tsv
```

---

## 3. Provision Fabric Capacity (if not already provisioned)

Fabric capacity is required before mirroring can be activated. If already provisioned, skip to section 4.

```bash
az fabric capacity create \
  --resource-group rg-ipai-data-dev \
  --capacity-name fabric-ipai-dev \
  --sku-name F2 \
  --location southeastasia \
  --admin-members platform-owner@insightpulseai.com
```

Verify:

```bash
az fabric capacity show \
  --resource-group rg-ipai-data-dev \
  --capacity-name fabric-ipai-dev \
  --query '{name:name, state:state, sku:sku}' \
  --output table
```

**Expected**: State = `Active`, SKU = `F2`.

---

## 4. Create Mirrored Database in Fabric Portal

Fabric Mirroring for Azure Database for PostgreSQL is configured through the Fabric portal. There is no CLI equivalent for the mirroring connection setup.

### 4.1 Navigate to Fabric Portal

1. Open [https://app.fabric.microsoft.com](https://app.fabric.microsoft.com)
2. Select the target workspace (e.g., `ipai-data-mirror-dev`)
3. Ensure the workspace is assigned to the Fabric capacity

<!-- SCREENSHOT: Fabric workspace overview showing capacity assignment -->

### 4.2 Create New Mirrored Database

1. Click **+ New item** in the workspace
2. Select **Mirrored database** > **Azure Database for PostgreSQL**
3. Enter connection details:
   - **Server**: `pg-ipai-odoo.postgres.database.azure.com`
   - **Database**: `odoo_staging`
   - **Authentication**: PostgreSQL authentication (use admin credentials from Key Vault)
   - **Username**: Retrieved from `kv-ipai-dev` secret `odoo-db-user` (or the admin login)
   - **Password**: Retrieved from `kv-ipai-dev` secret `odoo-db-password`

<!-- SCREENSHOT: Fabric mirrored database connection dialog -->

4. Click **Connect**

### 4.3 Select Tables to Mirror

1. After connection succeeds, Fabric displays available tables
2. For the rehearsal, select **all public schema tables** (Odoo's standard schema)
3. Review the table list -- exclude system/temporary tables if shown
4. Click **Mirror database**

<!-- SCREENSHOT: Fabric table selection for mirroring -->

### 4.4 Wait for Initial Snapshot

1. Fabric performs an initial full snapshot of selected tables
2. Monitor the replication status in the Fabric portal
3. Initial snapshot duration depends on database size -- expect 5-30 minutes for staging
4. Status should transition: `Initializing` -> `Snapshotting` -> `Replicating`

<!-- SCREENSHOT: Fabric mirroring status showing replication active -->

---

## 5. Validation Queries

After mirroring is active (`Replicating` status), verify data is flowing correctly.

### 5.1 Check Mirroring Status in Fabric

In the Fabric portal mirrored database view:
- All selected tables should show status `Replicating`
- `Last sync` timestamp should be within the last few minutes
- Row counts should be non-zero for populated tables

### 5.2 Validate Row Counts (Source vs Mirror)

Connect to the Fabric SQL analytics endpoint for the mirrored database and compare row counts against the source.

**On the source PG (via psql or Azure CLI):**

```sql
-- Run against pg-ipai-odoo / odoo_staging
SELECT schemaname, relname, n_live_tup
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_live_tup DESC
LIMIT 20;
```

**On the Fabric SQL analytics endpoint:**

```sql
-- Run in Fabric SQL analytics endpoint
SELECT TABLE_NAME, ROW_COUNT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'dbo'
ORDER BY ROW_COUNT DESC;
```

**Expected**: Row counts should match within a small delta (CDC lag). Exact match is expected after initial snapshot completes.

### 5.3 Validate Specific Business Tables

Check that core Odoo tables are present and populated:

```sql
-- Fabric SQL analytics endpoint
SELECT COUNT(*) as row_count FROM res_partner;
SELECT COUNT(*) as row_count FROM account_move;
SELECT COUNT(*) as row_count FROM sale_order;
SELECT COUNT(*) as row_count FROM product_template;
SELECT COUNT(*) as row_count FROM hr_employee;
SELECT COUNT(*) as row_count FROM project_project;
SELECT COUNT(*) as row_count FROM project_task;
```

### 5.4 Validate CDC (Change Propagation)

1. Insert or update a record in `odoo_staging` via Odoo or direct SQL
2. Wait 1-2 minutes (CDC propagation delay)
3. Query the same record in the Fabric SQL analytics endpoint
4. Confirm the change is reflected

**Source (psql):**

```sql
-- Create a test partner on odoo_staging
INSERT INTO res_partner (name, email, create_date, write_date, active)
VALUES ('Fabric Mirror Test', 'fabric-test@insightpulseai.com', NOW(), NOW(), true);
```

**Fabric SQL analytics endpoint (after 1-2 min):**

```sql
SELECT name, email, create_date
FROM res_partner
WHERE name = 'Fabric Mirror Test';
```

**Expected**: Record appears in Fabric within 2 minutes.

### 5.5 Validate Data Types

Spot-check that data types are correctly mapped:

```sql
-- Fabric SQL analytics endpoint
SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'res_partner'
ORDER BY ORDINAL_POSITION;
```

Compare against the PG source schema to ensure no truncation or type mismatch.

---

## 6. Rollback Procedure

If the rehearsal encounters issues, follow this rollback sequence.

### 6.1 Stop Mirroring (Fabric Portal)

1. Open the mirrored database item in the Fabric workspace
2. Click **Stop mirroring**
3. Confirm the action
4. This stops CDC replication and the logical replication slot

### 6.2 Clean Up Replication Slot (if stuck)

If mirroring fails to clean up its replication slot:

```sql
-- Connect to pg-ipai-odoo / odoo_staging via psql
SELECT slot_name, active, restart_lsn
FROM pg_replication_slots
WHERE database = 'odoo_staging';

-- Drop the Fabric replication slot if inactive
SELECT pg_drop_replication_slot('<slot_name>');
```

**Warning**: Only drop slots that are `active = false`. Dropping an active slot while mirroring is running will corrupt the mirror.

### 6.3 Delete Mirrored Database Item (Fabric Portal)

1. In the Fabric workspace, right-click the mirrored database item
2. Select **Delete**
3. Confirm deletion
4. This removes the OneLake Delta tables created by mirroring

### 6.4 Verify Server Health Post-Rollback

```bash
az postgres flexible-server show \
  --resource-group rg-ipai-dev-odoo-data \
  --name pg-ipai-odoo \
  --query '{name:name, state:state}' \
  --output table
```

```sql
-- Confirm no orphaned replication slots
SELECT slot_name, active FROM pg_replication_slots;
```

**Expected**: Server state = `Ready`, no orphaned replication slots.

---

## 7. Known Constraints

These constraints apply during and after Fabric Mirroring is active.

### 7.1 DDL Freeze

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| `ALTER TABLE` (add/drop/rename column) | Breaks mirroring for the affected table | Stop mirroring, apply DDL, restart mirroring |
| `CREATE TABLE` | New table not automatically mirrored | Add table to mirror configuration manually |
| `DROP TABLE` | Mirrored table becomes stale/error | Stop mirroring, drop, restart |
| Schema migrations (Odoo module install/upgrade) | Runs DDL against many tables | Coordinate: stop mirroring before upgrade, restart after |

**Rule**: No Odoo module installs, upgrades, or `--update` runs on `odoo_staging` while mirroring is active without first pausing the mirror.

### 7.2 TRUNCATE Restriction

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| `TRUNCATE TABLE` | Breaks mirroring for the affected table | Use `DELETE FROM` instead (slower but mirroring-safe) |

### 7.3 Server Restart

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| PG server restart | Temporarily disconnects mirroring | Mirroring auto-reconnects; verify status after restart |
| Parameter changes requiring restart | Downtime window | Schedule during maintenance; verify mirror recovery |

### 7.4 Table Ownership

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| Tables must be owned by `azure_pg_admin` | Tables owned by other roles are not mirrored | `ALTER TABLE <table> OWNER TO azure_pg_admin;` |

### 7.5 Supported Data Types

Fabric Mirroring supports most PostgreSQL data types. Known limitations:

| PG Type | Fabric Support | Notes |
|---------|---------------|-------|
| `jsonb` | Mapped to `varchar(max)` | Queryable but not structured |
| `array` types | Mapped to `varchar(max)` | Flattened to string |
| `bytea` | Not mirrored | Binary data excluded |
| `uuid` | Mapped to `uniqueidentifier` | Supported |
| `timestamp with timezone` | Mapped to `datetimeoffset` | Supported |
| Custom domains/types | Depends on base type | Verify per type |

### 7.6 Performance Considerations

| Factor | Guideline |
|--------|-----------|
| Initial snapshot | May increase PG CPU and I/O; schedule off-peak |
| Ongoing CDC | Low overhead (~1-3% additional WAL write amplification) |
| Replication lag | Typical 1-5 minutes; may increase during heavy write bursts |
| Replication slot WAL retention | If mirror is paused/broken, WAL accumulates on PG; monitor disk |

---

## 8. Post-Rehearsal: 48-Hour Monitoring

After mirroring is active and initial validation passes, monitor for 48 hours before promoting to production scope.

### 8.1 Monitoring Checklist

| Check | Frequency | Tool | Threshold |
|-------|-----------|------|-----------|
| Mirroring status | Every 4 hours | Fabric portal | All tables = `Replicating` |
| Replication lag | Every 4 hours | Fabric portal | < 5 minutes |
| PG WAL disk usage | Every 8 hours | Azure Portal / CLI | < 80% of storage |
| PG CPU utilization | Every 8 hours | Azure Portal metrics | < 70% average |
| PG connection count | Every 8 hours | Azure Portal metrics | < 80% of max connections |
| Replication slot WAL retention | Every 12 hours | `pg_replication_slots` query | `restart_lsn` advancing |
| Row count drift | At 24h and 48h | Source vs mirror query | < 1% delta |

### 8.2 Azure CLI Monitoring Commands

**Check PG storage usage:**

```bash
az postgres flexible-server show \
  --resource-group rg-ipai-dev-odoo-data \
  --name pg-ipai-odoo \
  --query '{storageUsedMb:storage.storageSizeGb, fqdn:fullyQualifiedDomainName}' \
  --output table
```

**Check PG metrics (CPU, connections):**

```bash
az monitor metrics list \
  --resource "/subscriptions/<sub-id>/resourceGroups/rg-ipai-dev-odoo-data/providers/Microsoft.DBforPostgreSQL/flexibleServers/pg-ipai-odoo" \
  --metric "cpu_percent" \
  --interval PT1H \
  --start-time $(date -u -v-24H +%Y-%m-%dT%H:%M:%SZ) \
  --output table
```

**Check replication slots (psql):**

```sql
SELECT slot_name, active, restart_lsn, confirmed_flush_lsn,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS wal_retained
FROM pg_replication_slots
WHERE database = 'odoo_staging';
```

### 8.3 Success Criteria for Promotion

All of the following must be true before mirroring `odoo` (production):

| Criterion | Required |
|-----------|----------|
| All tables in `Replicating` status for 48h continuous | Yes |
| No mirroring errors or restarts during the period | Yes |
| Replication lag consistently < 5 minutes | Yes |
| PG CPU impact < 5% incremental | Yes |
| PG WAL retention not growing unbounded | Yes |
| Row count delta < 1% at 24h and 48h marks | Yes |
| No DDL or TRUNCATE incidents during the period | Yes |
| CDC change propagation validated at least twice | Yes |

### 8.4 If Rehearsal Fails

| Failure Mode | Action |
|--------------|--------|
| Mirror does not start | Check PG firewall, credentials, `wal_level`, table ownership |
| Initial snapshot hangs | Check PG CPU/IO; consider off-peak retry |
| CDC stops propagating | Check replication slot status; restart mirroring |
| WAL retention growing | Mirror is stuck; stop and recreate the mirror |
| Fabric capacity paused | Resume capacity; mirroring will reconnect |
| Data type mapping errors | Document affected columns; check supported types table |

---

## 9. Post-Rehearsal Next Steps

After the 48-hour soak succeeds:

1. **Document results** in `docs/evidence/<YYYYMMDD-HHMM>/fabric-mirroring/rehearsal-results.md`
2. **Update SSOT** in `data-intelligence/ssot/mirroring/fabric-mirror-config.yaml` with actual runtime values
3. **Plan production mirroring** for `odoo` database with the same procedure
4. **Create OneLake shortcuts** from the Databricks workspace to the mirrored tables (if hybrid path is chosen)
5. **Wire to Power BI** via Direct Lake or SQL analytics endpoint for first operational dashboard

---

## References

- [Microsoft Fabric Mirroring for Azure Database for PostgreSQL](https://learn.microsoft.com/en-us/fabric/database/mirrored-database/azure-database-postgresql)
- [Fabric Mirroring limitations and known issues](https://learn.microsoft.com/en-us/fabric/database/mirrored-database/azure-database-postgresql-limitations)
- Architecture: `docs/architecture/DATABRICKS_FABRIC_ROLE_SPLIT.md`
- Architecture: `docs/architecture/data-intelligence-architecture.md`
- Target state: `docs/architecture/FABRIC_FINANCE_PPM_TARGET_STATE.md`
- Capacity decision: `docs/runbooks/fabric-capacity-decision.md`
- SSOT config: `data-intelligence/ssot/mirroring/fabric-mirror-config.yaml`

---

*Last updated: 2026-03-30*
