# Examples: Tenancy Model Selection

## Example 1: Decision Matrix

| Criterion | Weight | Shared | Dedicated | Hybrid |
|-----------|--------|--------|-----------|--------|
| Cost efficiency | 30% | 9 | 3 | 7 |
| Isolation strength | 25% | 4 | 9 | 7 |
| Performance predictability | 20% | 5 | 9 | 7 |
| Compliance fit | 15% | 3 | 9 | 8 |
| Operational complexity | 10% | 8 | 4 | 5 |
| **Weighted total** | | **5.85** | **6.45** | **7.05** |

**Result**: Hybrid model selected. Best overall score balancing cost and isolation.

---

## Example 2: Tier Mapping for Hybrid Model

| Tier | Tenancy Model | Compute | Database | Rationale |
|------|--------------|---------|----------|-----------|
| Free | Shared pool | Shared Container App | Shared PG (row-level) | Cost: $0 per tenant |
| Standard | Shared pool | Shared Container App | Shared PG (schema-level) | Cost: predictable |
| Enterprise | Dedicated | Dedicated Container App | Dedicated PG server | Isolation: contractual |
| Regulated | Dedicated + isolated | Dedicated in isolated VNet | Dedicated PG in private subnet | Compliance: required |

---

## Example 3: Migration Path (Standard to Enterprise)

**Sequence**:
1. Provision dedicated database server for tenant
2. Export tenant data from shared database (schema-level export)
3. Import data into dedicated database
4. Update tenant routing to point to dedicated compute
5. Validate data integrity and application function
6. Update billing to enterprise tier
7. Decommission shared database schema after retention period

**Rollback**: At any step before routing cutover (step 4), roll back by abandoning the dedicated resources. After routing cutover, roll back by reverting the routing change.
