# Examples: SaaS Governance, DevOps & Incident Design

## Example 1: Ring-Based Deployment

**Ring structure**:
```
Ring 0: Internal/canary (platform team tenants)     - 1% traffic
Ring 1: Early adopter tenants (opted in)            - 5% traffic
Ring 2: Standard tier tenants                       - 40% traffic
Ring 3: Enterprise tier tenants                     - 54% traffic
```

**Pipeline stages**:
```
Build --> Test --> Ring 0 (auto) --> Ring 1 (auto after 2h) -->
  Ring 2 (manual gate) --> Ring 3 (manual gate + enterprise notification)
```

**Rollback**: Per-ring rollback. If Ring 1 shows errors > 0.1%, halt promotion and roll back Ring 1. Ring 0 remains on new version for debugging.

---

## Example 2: Incident Escalation Matrix

| Severity | Description | Response | Blast Radius | Communication |
|----------|-------------|----------|-------------|---------------|
| P1 | Platform-wide outage | 15 min | All tenants | Status page + email + Slack |
| P2 | Single-tier degradation | 30 min | Tier subset | Affected tenants via email |
| P3 | Single-tenant issue | 2 hours | One tenant | Direct tenant communication |
| P4 | Non-impacting anomaly | Next business day | None | Internal tracking only |

**Blast radius calculation**: Query tenant-to-infrastructure mapping. If affected resource is shared, all tenants on that resource are in blast radius. If dedicated, only the owning tenant.

---

## Example 3: Azure Policy for Governance

**Required tags policy** (deny if missing):
```json
{
  "if": {
    "allOf": [
      { "field": "type", "notEquals": "Microsoft.Resources/subscriptions/resourceGroups" },
      { "field": "tags['tenant-id']", "exists": "false" }
    ]
  },
  "then": { "effect": "deny" }
}
```

**Allowed regions policy**: Restrict to `southeastasia` and `eastus` for data residency compliance.
