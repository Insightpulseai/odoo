# Evaluations: SaaS Resource Organization

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Subscription limits validated | 20% | Tenant count fits within Azure subscription quotas |
| Naming convention complete | 20% | Pattern includes resource type, tenant, environment, region |
| Tagging policy enforceable | 20% | Azure Policy defined for all required tags |
| RBAC least-privilege | 20% | No cross-tenant access, no over-permissioned roles |
| Cost attribution possible | 20% | Tags + RG structure enable per-tenant cost reporting |

## Eval Scenarios

### Scenario 1: Shared Pool Naming Collision
- **Input**: Two tenants with similar names in shared RG
- **Expected**: Naming convention prevents collision via tenant-id prefix/suffix
- **Fail condition**: Resource names collide or require manual disambiguation

### Scenario 2: Subscription Quota Breach
- **Input**: 500 tenants, each needing 3 Container Apps
- **Expected**: Design identifies subscription limit and proposes multi-subscription strategy
- **Fail condition**: Design assumes single subscription without validating limits

### Scenario 3: Cost Attribution Accuracy
- **Input**: Monthly Azure bill for shared infrastructure
- **Expected**: Tags and RG structure allow 95%+ cost attribution to specific tenants
- **Fail condition**: Significant shared costs cannot be attributed

### Scenario 4: RBAC Cross-Tenant Access
- **Input**: Enterprise tenant admin requests access to their resources
- **Expected**: RBAC scoped to tenant-specific RG only, no cross-tenant visibility
- **Fail condition**: Tenant admin can see or access other tenants' resources
