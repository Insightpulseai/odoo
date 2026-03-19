# Examples: SaaS Migration Design

## Example 1: Zero-Downtime Inter-Stamp Migration (PostgreSQL Logical Replication)

**Scenario**: Tenant "acme-corp" migrating from stamp-sea-001 to stamp-sea-002 due to capacity.

**Timeline**:
```
T-24h: Lower DNS TTL to 60 seconds
T-4h:  Start logical replication (source → destination)
T-1h:  Verify replication lag < 1 second
T-0:   Cutover window opens
  T+0m:  Pause write traffic (application returns 503 for writes, reads continue)
  T+1m:  Confirm replication fully caught up (lag = 0)
  T+2m:  Compute source data checksum
  T+3m:  Compute destination data checksum, verify match
  T+4m:  Update Front Door routing to destination stamp
  T+5m:  Resume write traffic on destination
  T+5m:  Update tenant catalog: stamp = stamp-sea-002
T+24h: Source database archived and decommissioned
```

**Data migration commands**:
```sql
-- Source: Create publication
CREATE PUBLICATION tenant_acme_pub FOR ALL TABLES;

-- Destination: Create subscription
CREATE SUBSCRIPTION tenant_acme_sub
    CONNECTION 'host=pg-ipai-prod-sea-001 dbname=odoo_tenant_acme_corp'
    PUBLICATION tenant_acme_pub;

-- Monitor replication lag
SELECT slot_name, confirmed_flush_lsn, pg_current_wal_lsn(),
       pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) as lag_bytes
FROM pg_replication_slots WHERE slot_name = 'tenant_acme_sub';
```

**Write downtime**: ~5 minutes.

---

## Example 2: Tier Upgrade (Shared to Dedicated)

**Scenario**: Tenant upgrading from standard (shared database) to enterprise (dedicated database).

**Migration steps**:
1. Provision dedicated PostgreSQL server: `pg-ipai-prod-acme-primary`
2. Export tenant data: `pg_dump -Fc -d odoo_shared -n acme_schema > acme.dump`
3. Restore to dedicated server: `pg_restore -d odoo_tenant_acme acme.dump`
4. Provision dedicated Container App: `ca-ipai-prod-acme-web`
5. Configure dedicated Container App to point to dedicated PostgreSQL
6. Update Front Door: route `acme.erp.insightpulseai.com` to dedicated Container App
7. Verify dedicated environment operational
8. Remove tenant from shared database

**Rollback**: Revert Front Door routing to shared stamp, shared database still has data until cleanup.

---

## Example 3: Cross-Region Migration (Data Residency)

**Scenario**: EU tenant must move from Southeast Asia stamp to West Europe stamp.

**Special considerations**:
- Data transfer across regions requires encrypted transit
- GDPR implications — data must not persist in SEA after migration
- Higher replication lag due to geographic distance

**Approach**: pg_dump/restore (not logical replication due to cross-region latency).

```bash
# 1. Backup on source
pg_dump -Fc -h pg-ipai-prod-sea-001 -d odoo_tenant_eu_corp > eu_corp.dump

# 2. Transfer to destination region (encrypted)
azcopy copy eu_corp.dump "https://stipaiprodweu001.blob.core.windows.net/migrations/eu_corp.dump"

# 3. Restore on destination
pg_restore -h pg-ipai-prod-weu-001 -d odoo_tenant_eu_corp eu_corp.dump

# 4. Verify checksums
pg_dump -Fc -h pg-ipai-prod-weu-001 -d odoo_tenant_eu_corp | md5sum
# Compare with source dump checksum

# 5. Purge source data (GDPR compliance)
DROP DATABASE odoo_tenant_eu_corp;  -- On SEA server
```

**Maintenance window**: Required (30-60 minutes depending on data volume).
