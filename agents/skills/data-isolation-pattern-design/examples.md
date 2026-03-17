# Examples: Data Isolation Pattern Design

## Example 1: Database-Per-Tenant (Odoo CE Default)

**Scenario**: 30 tenants, Odoo CE on Azure, enterprise customers requiring strict isolation.

**Pattern**: Database-per-tenant (Odoo's native model).

**Topology**:
```
Azure PostgreSQL Flexible Server: pg-ipai-prod
├── odoo_tenant_acme       (Tenant: Acme Corp)
├── odoo_tenant_globex     (Tenant: Globex Inc)
├── odoo_tenant_initech    (Tenant: Initech LLC)
└── ... (one database per tenant)
```

**Connection management**:
- PgBouncer in front of PostgreSQL for connection pooling
- Max connections per tenant database: 20 (standard), 50 (enterprise)
- Connection string resolved from tenant catalog at request time

**Encryption**:
- TDE enabled at server level (Azure-managed keys)
- Enterprise tenants: customer-managed key in dedicated Key Vault section

**Tenant lifecycle**:
- Backup: `pg_dump odoo_tenant_{id}` via Azure automated backups + on-demand
- Export: `pg_dump --data-only` filtered to tenant database
- Delete: `DROP DATABASE odoo_tenant_{id}` after retention period

**Trade-offs**: Maximum isolation, simple queries (no tenant filter needed). Cost scales linearly with tenants. Server resource limits at ~100 databases per Flexible Server.

---

## Example 2: Row-Level Isolation with PostgreSQL RLS

**Scenario**: 500 tenants, cost-sensitive, shared Odoo tables with RLS.

**Pattern**: Shared tables with PostgreSQL RLS policies.

**RLS implementation**:
```sql
-- Enable RLS on all tenant-scoped tables
ALTER TABLE res_partner ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY tenant_isolation ON res_partner
    USING (company_id = current_setting('app.current_tenant_id')::int);

-- Set tenant context at session start
SET app.current_tenant_id = '42';

-- Query returns only tenant 42's partners
SELECT * FROM res_partner; -- RLS automatically filters
```

**Application integration**:
```python
# Odoo middleware sets tenant context per request
def set_tenant_context(cr, tenant_id):
    cr.execute("SET app.current_tenant_id = %s", [tenant_id])
```

**Trade-offs**: Lowest cost (single database), most complex (RLS on every table). Risk of RLS bypass if application code uses SUPERUSER. Performance overhead from RLS policy evaluation.

---

## Example 3: Hybrid Pattern (Tier-Based)

**Scenario**: 200 tenants across three tiers.

**Pattern selection matrix**:

| Criterion | DB-per-tenant | Schema-per-tenant | Row-level |
|-----------|--------------|-------------------|-----------|
| Isolation strength | 5 | 4 | 3 |
| Cost per tenant | 1 | 3 | 5 |
| Query simplicity | 5 | 4 | 2 |
| Scalability | 2 | 3 | 5 |
| Backup granularity | 5 | 4 | 2 |

**Hybrid assignment**:
- **Enterprise** (10 tenants): Database-per-tenant (max isolation)
- **Standard** (50 tenants): Schema-per-tenant (good isolation, moderate cost)
- **Free** (140 tenants): Row-level isolation (shared tables, minimal cost)

**Migration path**: Tenant upgrade from Free to Standard triggers schema migration. Standard to Enterprise triggers full database migration with zero-downtime cutover via logical replication.
