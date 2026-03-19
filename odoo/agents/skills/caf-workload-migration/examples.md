# Examples — caf-workload-migration

## Example 1: PostgreSQL migration (replatform)

**Input**: Migrate PostgreSQL from DigitalOcean Docker to Azure Database for PostgreSQL Flexible Server.

**Output**:
- Assessment: PostgreSQL 16 on Docker, 2GB data, 5 databases, pg_dump compatible
- Pattern: Replatform (Docker PG to Azure managed PG Flexible Server)
- Wave: Single-workload wave, database migrates before application
- Cutover runbook:
  1. Enable read replica on source (0 min)
  2. pg_dump all databases (est. 5 min)
  3. pg_restore to Azure PG (est. 10 min)
  4. Verify row counts and checksums (est. 5 min)
  5. Update Odoo connection string in Key Vault (est. 2 min)
  6. Restart ACA apps to pick up new connection (est. 3 min)
  7. Validate Odoo login and basic operations (est. 5 min)
- Rollback: Revert Key Vault secret to old connection string, restart ACA apps
- Validation: Row count match, Odoo health check, 3 functional tests
- Total estimated downtime: 30 minutes

## Example 2: Container App migration (rehost)

**Input**: Migrate n8n from DigitalOcean Docker to Azure Container Apps.

**Output**:
- Assessment: n8n Docker image, environment variables for config, webhook URLs in DNS
- Pattern: Rehost (same container image, new orchestrator)
- Wave: After database migration (n8n depends on PostgreSQL)
- Cutover runbook:
  1. Deploy n8n Container App with existing image (est. 5 min)
  2. Configure environment variables from Key Vault (est. 5 min)
  3. Verify n8n UI accessible via ACA FQDN (est. 2 min)
  4. Add Front Door origin for n8n (est. 5 min)
  5. Update DNS CNAME for n8n.insightpulseai.com (est. 2 min)
  6. Validate webhooks trigger correctly (est. 10 min)
- Rollback: Revert DNS CNAME to DigitalOcean origin
- Validation: n8n UI loads, test workflow executes, webhook receives test event

## Example 3: Migration blocked by dependency

**Input**: Attempt to migrate Superset before its PostgreSQL backend is migrated.

**Output**:
- Assessment: Superset depends on `pg-ipai-dev` PostgreSQL, which is not yet migrated
- Pattern: Cannot determine — blocked
- Blocker: Superset migration depends on PostgreSQL migration completing first
- Recommendation: Move PostgreSQL migration to Wave 1, Superset to Wave 2
- Rollback: N/A (migration not started)
