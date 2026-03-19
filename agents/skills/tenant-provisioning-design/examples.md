# Examples: Tenant Provisioning Design

## Example 1: Shared Pool Provisioning (Odoo CE + Azure Container Apps)

**Scenario**: New standard-tier tenant for Odoo CE multi-tenant platform.

**Registration flow**:
1. Tenant submits registration via API (name, admin email, tier: standard)
2. Validation: check uniqueness, email verification
3. Auto-approved (standard tier — no manual gate)
4. Provisioning triggered via Service Bus message

**Resource allocation** (shared pool — no dedicated Azure resources):
- PostgreSQL database created on shared Azure Flexible Server: `odoo_tenant_{tenant_id}`
- Container App environment shared — no new compute resources
- DNS record: `{tenant_slug}.erp.insightpulseai.com` via Front Door

**Configuration**:
```json
{
  "tenant_id": "acme-corp",
  "tier": "standard",
  "database": "odoo_tenant_acme_corp",
  "modules": ["base", "sale", "account", "crm"],
  "admin_email": "admin@acme.example.com",
  "locale": "en_US",
  "timezone": "Asia/Manila"
}
```

**Onboarding automation** (Durable Functions):
1. Create PostgreSQL database (compensate: drop database)
2. Initialize Odoo schema (`odoo-bin -d {db} -i base --stop-after-init`)
3. Install tenant modules
4. Create admin user via Odoo RPC
5. Apply tenant configuration (locale, timezone, branding)
6. Send welcome email
7. Update tenant catalog: status = active

**Provisioning SLA**: 5 minutes (standard tier).

---

## Example 2: Dedicated Stamp Provisioning (Enterprise Tier)

**Scenario**: Enterprise tenant requiring dedicated compute and database.

**Registration flow**:
1. Sales team submits provisioning request via control plane API
2. Manual approval required (enterprise tier)
3. Provisioning triggered after approval

**Resource allocation** (dedicated stamp):
```bicep
// Dedicated resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: 'rg-ipai-prod-tenant-${tenantId}'
  location: stampRegion
}

// Dedicated PostgreSQL
resource pg 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01' = {
  name: 'pg-ipai-prod-${tenantId}'
  // ... tier-specific SKU
}

// Dedicated Container App
resource ca 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'ca-ipai-prod-${tenantId}-web'
  // ... dedicated scaling rules
}
```

**Provisioning SLA**: 30 minutes (enterprise tier, includes dedicated resource creation).

**Rollback**: If Container App deployment fails after database creation, compensation deletes the database and resource group.

---

## Example 3: Concurrent Provisioning Stress Test

**Scenario**: 20 tenants register simultaneously during a launch event.

**Design considerations**:
- Service Bus queue with competing consumers (max 5 concurrent provisioning workflows)
- Database creation serialized per PostgreSQL server to avoid connection pool exhaustion
- ARM deployment uses deployment scripts with `dependsOn` to prevent race conditions
- Provisioning status endpoint allows tenants to poll progress
- SLA clock starts at queue insertion, not at processing start

**Monitoring**:
```kusto
// KQL: Provisioning SLA compliance
customEvents
| where name == "TenantProvisioningComplete"
| extend duration = datetime_diff('minute', timestamp, todatetime(customDimensions.startTime))
| summarize p50=percentile(duration, 50), p95=percentile(duration, 95), breaches=countif(duration > 5) by tier=tostring(customDimensions.tier)
```
