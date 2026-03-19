# Examples: Tenant Isolation Design

## Example 1: Isolation Matrix (Hybrid Model)

| Layer | Free/Standard (Shared) | Enterprise (Dedicated) |
|-------|----------------------|----------------------|
| Compute | Shared Container App, per-tenant rate limits | Dedicated Container App per tenant |
| Data | Shared PG with row-level security (tenant_id column) | Dedicated PG Flexible Server |
| Network | Shared VNet, NSG rules per subnet | Dedicated subnet, private endpoints |
| Keys | Shared Key Vault, access policy per tenant | Dedicated Key Vault per tenant |
| Backup | Shared backup with tenant-scoped restore | Dedicated backup schedule |

## Example 2: Row-Level Security (Shared Database)

**PostgreSQL RLS policy**:
```sql
-- Enable RLS on all tenant-scoped tables
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Policy: users can only see their tenant's rows
CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Force RLS even for table owner
ALTER TABLE orders FORCE ROW LEVEL SECURITY;
```

**Application middleware**:
```python
# Set tenant context on every database connection
def set_tenant_context(connection, tenant_id):
    with connection.cursor() as cursor:
        cursor.execute("SET app.current_tenant_id = %s", [str(tenant_id)])
```

**Testing**:
```python
# Cross-tenant access test
def test_cross_tenant_isolation():
    # Connect as tenant A
    set_tenant_context(conn, tenant_a_id)
    tenant_a_orders = query_orders(conn)

    # Connect as tenant B
    set_tenant_context(conn, tenant_b_id)
    tenant_b_orders = query_orders(conn)

    # Verify no overlap
    assert not set(tenant_a_orders).intersection(set(tenant_b_orders))
```

## Example 3: Network Isolation (Enterprise Tier)

**Architecture**:
```
Internet --> Azure Front Door --> WAF -->
  Shared subnet (free/standard tenants)
    --> Container App (shared)
    --> Shared PG (private endpoint)

  Tenant-A subnet (enterprise)
    --> Container App (dedicated)
    --> PG Flexible Server (private endpoint, tenant-A only)
    --> Key Vault (private endpoint, tenant-A only)
```

**NSG rules**: Enterprise tenant subnet allows only ingress from Front Door and egress to its own private endpoints. No cross-subnet communication allowed.
