# Examples: SaaS Resource Organization

## Example 1: Shared Pool Model (Small Scale)

**Scenario**: 50 tenants, shared infrastructure, cost-sensitive.

**Subscription topology**: Single subscription per environment (dev, staging, prod).

**Resource group structure**:
```
rg-{app}-{env}-shared        # Shared services (API gateway, monitoring)
rg-{app}-{env}-compute       # App containers, functions
rg-{app}-{env}-data          # Databases, storage
rg-{app}-{env}-network       # VNet, Front Door, DNS
```

**Naming convention**: `{resource-type}-{app}-{env}-{component}[-{region}]`
- Example: `ca-ipai-prod-api-sea` (Container App, prod, API, Southeast Asia)

**Tagging policy**:
```
environment: prod | staging | dev
cost-center: platform
data-classification: internal | confidential
owner: platform-team
```

**RBAC**: Platform team has Contributor on all RGs. Tenant isolation via application-level logic, not Azure RBAC.

---

## Example 2: Hybrid Model (Medium Scale)

**Scenario**: 200 tenants, enterprise tier gets dedicated resources.

**Subscription topology**: Two subscriptions per environment --- one for shared pool, one for dedicated tenant resources.

**Resource group structure**:
```
# Shared subscription
rg-{app}-{env}-shared
rg-{app}-{env}-pool-compute
rg-{app}-{env}-pool-data

# Dedicated subscription
rg-{app}-{env}-tenant-{tenant-id}    # One RG per enterprise tenant
```

**Naming convention**: `{resource-type}-{app}-{env}-{tenant-id}-{component}`
- Shared: `pg-ipai-prod-pool` (shared PostgreSQL)
- Dedicated: `pg-ipai-prod-acme-primary` (tenant-specific PostgreSQL)

**Tagging policy**:
```
environment: prod | staging | dev
tenant-id: pool | {specific-tenant-id}
tier: standard | enterprise
cost-center: {tenant-id} | platform
data-classification: internal | confidential | restricted
owner: platform-team | {tenant-owner}
```

**RBAC**: Tenant-specific RGs have scoped RBAC. Enterprise tenants may have read access to their own RG.

---

## Example 3: Dedicated Silo Model (Enterprise Scale)

**Scenario**: 20 large enterprise tenants, strict isolation requirements.

**Subscription topology**: One subscription per tenant.

**Resource group structure**: Standard Azure landing zone pattern within each tenant subscription.

**Naming convention**: `{resource-type}-{tenant-id}-{env}-{component}-{region}`

**RBAC**: Each tenant subscription has isolated RBAC. Central platform team has cross-subscription read via management groups.
