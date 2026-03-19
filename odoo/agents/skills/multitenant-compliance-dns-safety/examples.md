# Examples: Multitenant Compliance & DNS Safety

## Example 1: Compliance Matrix

| Tenant | Tier | Compliance | Controls Required | Status |
|--------|------|------------|-------------------|--------|
| Acme Corp | Enterprise | SOC 2, HIPAA | Dedicated DB, encryption at rest, audit logs, BAA | Compliant |
| Beta Inc | Standard | SOC 2 | Shared DB with RLS, encryption at rest, audit logs | Compliant |
| Gamma LLC | Enterprise | GDPR | EU region only, data portability, right to erasure | Gap: erasure automation |
| Delta Co | Free | None | Standard platform security | Compliant |

---

## Example 2: Subdomain Takeover Prevention

**Risk scenario**:
```
1. Tenant "acme" offboards
2. Container App "ca-ipai-prod-acme" deleted
3. DNS record "acme.app.insightpulseai.com" still points to deleted resource
4. Attacker claims the resource name in their own subscription
5. Attacker serves malicious content on acme.app.insightpulseai.com
```

**Prevention**:
```
Offboarding workflow (order matters):
1. Disable tenant access (application level)
2. Remove Front Door route for tenant subdomain
3. Delete DNS CNAME record for tenant subdomain  <-- DNS cleanup BEFORE resource deletion
4. Delete Container App
5. Delete database/storage resources
6. Verify: DNS record resolves to NXDOMAIN
```

**Monitoring**:
```bash
# Daily dangling CNAME scan
for record in $(list_all_tenant_cnames); do
    target=$(dig +short $record CNAME)
    if ! resource_exists $target; then
        alert "Dangling CNAME detected: $record -> $target"
        auto_remove_dns_record $record
    fi
done
```

---

## Example 3: Data Residency Enforcement

**Azure Policy for EU-only tenant**:
```json
{
  "if": {
    "allOf": [
      { "field": "tags['data-residency']", "equals": "eu" },
      { "field": "location", "notIn": ["westeurope", "northeurope", "francecentral", "germanywestcentral"] }
    ]
  },
  "then": { "effect": "deny" }
}
```

**Validation query** (run weekly):
```sql
SELECT tenant_id, resource_type, location
FROM platform.resource_inventory
WHERE tenant_id IN (SELECT id FROM tenants WHERE data_residency = 'eu')
  AND location NOT IN ('westeurope', 'northeurope', 'francecentral', 'germanywestcentral');
-- Expected: 0 rows
```
