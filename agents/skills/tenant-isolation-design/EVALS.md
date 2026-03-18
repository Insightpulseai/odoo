# Evaluations: Tenant Isolation Design

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| All layers covered | 25% | Compute, data, network, and keys all have isolation design |
| Defense in depth | 25% | No single layer is the only isolation boundary |
| Testable isolation | 25% | Automated cross-tenant tests defined and runnable |
| Assume breach | 25% | Design holds even if one tenant is compromised |

## Eval Scenarios

### Scenario 1: Cross-Tenant Data Access
- **Input**: Tenant A attempts to query tenant B's data via SQL injection
- **Expected**: RLS policy blocks access; query returns only tenant A's data
- **Fail condition**: Any of tenant B's data visible to tenant A

### Scenario 2: Container Escape
- **Input**: Compromised tenant container attempts lateral movement
- **Expected**: Network isolation (NSG, private endpoints) prevents access to other tenant resources
- **Fail condition**: Compromised container can reach another tenant's database or API

### Scenario 3: Key Vault Cross-Access
- **Input**: Tenant A's application code attempts to read tenant B's secrets
- **Expected**: Key Vault access policy denies; managed identity scoped to tenant A only
- **Fail condition**: Tenant A can enumerate or read tenant B's secrets

### Scenario 4: Backup Restoration Cross-Tenant
- **Input**: Operator restores a backup; shared database backup contains all tenants
- **Expected**: Restoration process preserves RLS; no tenant data exposed to wrong tenant
- **Fail condition**: Backup restore grants access to data outside the target tenant
