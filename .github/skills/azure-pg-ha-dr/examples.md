# azure-pg-ha-dr -- Worked Examples

## Example 1: Enabling Zone-Redundant HA in Bicep

Before (gap state):
```bicep
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-12-01-preview' = {
  name: pgServerName
  location: location
  sku: {
    name: 'Standard_B2ms'
    tier: 'Burstable'
  }
  properties: {
    version: '16'
    storage: { storageSizeGB: 128 }
    backup: {
      retentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
  }
}
```

After (closed):
```bicep
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-12-01-preview' = {
  name: pgServerName
  location: location
  sku: {
    name: 'Standard_D2ds_v5'
    tier: 'GeneralPurpose'     // ZoneRedundant requires GeneralPurpose or MemoryOptimized
  }
  properties: {
    version: '16'
    storage: { storageSizeGB: 128 }
    highAvailability: {
      mode: 'ZoneRedundant'
      standbyAvailabilityZone: '2'
    }
    backup: {
      retentionDays: 35        // Maximum allowed
      geoRedundantBackup: 'Enabled'
    }
  }
}
```

Key decisions:
- Burstable SKU does not support zone-redundant HA. Upgrade to GeneralPurpose.
- `standbyAvailabilityZone` should differ from the primary zone.
- Geo-redundant backup requires GeneralPurpose or MemoryOptimized tier.

## Example 2: MCP Query Sequence

```
Step 1: microsoft_docs_search("Azure PostgreSQL Flexible Server high availability zone redundant")
Result: Confirms ZoneRedundant mode provisions a synchronous standby in a
        different AZ. Automatic failover within 60-120s. Requires GP/MO SKU.

Step 2: microsoft_docs_search("Azure PostgreSQL Flexible Server backup retention geo-redundant")
Result: Max retention 35 days. Geo-redundant backup copies to paired region.
        PITR available to any point within retention window.

Step 3: microsoft_docs_search("Azure PostgreSQL Flexible Server RPO RTO disaster recovery")
Result: Zone-redundant HA RPO = 0 (synchronous replication). RTO = 60-120s.
        Geo-restore RPO = up to 1 hour (async geo-backup). Geo-restore RTO
        depends on database size (hours for large DBs).
```

## Example 3: Restore Drill Procedure Skeleton

```markdown
## PostgreSQL Restore Drill

### Pre-requisites
- Azure CLI authenticated with `Contributor` on `rg-ipai-dev-odoo-data`
- Target restore server name chosen (e.g., `pg-ipai-odoo-drill-<date>`)

### Steps
1. Record current server state:
   az postgres flexible-server show --name pg-ipai-odoo --resource-group rg-ipai-dev-odoo-data
2. Initiate point-in-time restore:
   az postgres flexible-server restore \
     --name pg-ipai-odoo-drill-20260324 \
     --source-server pg-ipai-odoo \
     --restore-time "2026-03-24T00:00:00Z" \
     --resource-group rg-ipai-dev-odoo-data
3. Wait for provisioning (expected: 15-30 min for ~5 GB database).
4. Validate connectivity:
   psql "host=pg-ipai-odoo-drill-20260324.postgres.database.azure.com ..." -c "SELECT count(*) FROM res_partner;"
5. Confirm row counts match production baseline.
6. Delete drill server:
   az postgres flexible-server delete --name pg-ipai-odoo-drill-20260324 --resource-group rg-ipai-dev-odoo-data --yes

### Success Criteria
- Restore completed within 30 minutes.
- Row counts for res_partner, account_move, sale_order match production +/- 0.
- Drill server deleted after verification.
```

## Example 4: SSOT YAML Update

```yaml
  - name: pg-ipai-odoo
    type: Microsoft.DBforPostgreSQL/flexibleServers
    resource_group: rg-ipai-dev-odoo-data
    region: southeastasia
    source: bicep
    lifecycle: active
    owner_domain: odoo
    ha_mode: ZoneRedundant
    backup_retention_days: 35
    geo_redundant_backup: Enabled
    rpo_target: "0 (zone-redundant sync replication)"
    rto_target: "< 2 minutes (automatic failover)"
    last_restore_drill: "2026-03-24"
```
