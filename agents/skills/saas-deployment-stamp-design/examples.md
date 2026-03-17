# Examples: SaaS Deployment Stamp Design

## Example 1: Regional Stamps for Odoo CE Platform

**Scenario**: Odoo CE multi-tenant platform serving APAC and US tenants.

**Stamp composition** (per stamp):
```
Stamp: stamp-sea-001
├── Container Apps Environment: cae-ipai-prod-sea-001
│   ├── ca-ipai-prod-sea-001-web        (Odoo web)
│   ├── ca-ipai-prod-sea-001-worker     (background jobs)
│   └── ca-ipai-prod-sea-001-cron       (scheduled jobs)
├── PostgreSQL Flexible Server: pg-ipai-prod-sea-001
├── Redis Cache: redis-ipai-prod-sea-001
├── Storage Account: stipaiprod sea001
└── VNet: vnet-ipai-prod-sea-001
```

**Capacity model**:
| Resource | Limit per Stamp | Tenants Supported |
|----------|----------------|-------------------|
| PostgreSQL connections | 500 | 50 (10 conn/tenant) |
| Container App replicas | 30 | 50 (shared pool) |
| Storage | 1 TB | 50 (20 GB/tenant) |
| **Bottleneck** | **PG connections** | **50 tenants/stamp** |

**Stamp assignment**:
- APAC tenants: `stamp-sea-001`, `stamp-sea-002`
- US tenants: `stamp-eus-001`
- Assignment stored in control plane database: `tenant_catalog.stamp_assignment`

---

## Example 2: Capacity-Based Stamps (Single Region)

**Scenario**: 200 tenants in Southeast Asia, stamps created as capacity fills.

**Assignment algorithm**:
```python
def assign_tenant_to_stamp(tenant):
    # Find stamps with available capacity
    available = [s for s in stamps if s.tenant_count < s.max_capacity * 0.8]
    if not available:
        stamp = create_new_stamp(region=tenant.region)
        available = [stamp]
    # Assign to least-loaded stamp
    target = min(available, key=lambda s: s.tenant_count)
    target.assign_tenant(tenant.id)
    return target.id
```

**Scaling triggers**:
- 80% capacity: alert, pre-provision new stamp
- 90% capacity: new stamp must be ready, block new assignments to full stamp
- 100% capacity: hard block, new tenants queued until stamp available

---

## Example 3: Bicep Template for Stamp Deployment

**Stamp IaC**:
```bicep
@description('Stamp identifier (e.g., sea-001)')
param stampId string

@description('Azure region')
param location string

@description('Max tenants for this stamp')
param maxTenants int = 50

module networking 'modules/stamp-networking.bicep' = {
  name: 'networking-${stampId}'
  params: { stampId: stampId, location: location }
}

module database 'modules/stamp-database.bicep' = {
  name: 'database-${stampId}'
  params: { stampId: stampId, location: location, maxConnections: maxTenants * 10 }
}

module compute 'modules/stamp-compute.bicep' = {
  name: 'compute-${stampId}'
  params: { stampId: stampId, location: location, vnetId: networking.outputs.vnetId }
}

output stampEndpoint string = compute.outputs.webAppFqdn
output stampCapacity int = maxTenants
```

**Deployment**: `az deployment sub create --template-file stamp.bicep --parameters stampId=sea-002 location=southeastasia`
