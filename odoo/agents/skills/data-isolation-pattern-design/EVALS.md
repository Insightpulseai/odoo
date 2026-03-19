# Evaluations: Data Isolation Pattern Design

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Cross-tenant data prevention | 30% | No query path returns another tenant's data |
| Per-tenant backup capability | 20% | Individual tenant can be backed up and restored |
| Encryption per tenant | 15% | Confidential data encrypted with per-tenant keys |
| GDPR data lifecycle | 20% | Export and delete scoped to single tenant, verified complete |
| Pattern-to-requirements fit | 15% | Selected pattern matches isolation, cost, and scale needs |

## Eval Scenarios

### Scenario 1: Cross-Tenant Query in Shared Model

- **Input**: Application queries shared table without explicit tenant filter
- **Expected**: RLS policy returns only authenticated tenant's rows (zero rows from other tenants)
- **Fail condition**: Rows from other tenants visible

### Scenario 2: Tenant Data Export (GDPR)

- **Input**: Tenant requests full data export under GDPR right of access
- **Expected**: Export package contains all tenant data across all tables, nothing from other tenants
- **Fail condition**: Export missing tenant data, or contains other tenant data

### Scenario 3: Tenant Deletion

- **Input**: Tenant account terminated, data deletion requested
- **Expected**: All tenant data removed from all tables/databases. Verification query confirms zero residual rows.
- **Fail condition**: Orphaned data in any table after deletion

### Scenario 4: Encryption Key Rotation

- **Input**: Per-tenant encryption key rotated on schedule
- **Expected**: New key active, old data re-encrypted, no service interruption
- **Fail condition**: Downtime during rotation, or data inaccessible after rotation

## Grading Rubric

| Grade | Criteria |
|-------|----------|
| A | All 5 criteria pass, all 4 scenarios handled, hybrid pattern supported |
| B | 4/5 criteria pass, scenarios 1-3 handled |
| C | 3/5 criteria pass, basic cross-tenant prevention works |
| F | Cross-tenant data access possible in any scenario |

## Pass Criteria

Minimum grade B for production. Grade A required for platforms handling financial or health data.
