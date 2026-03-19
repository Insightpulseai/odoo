# Examples: Tenant Deployment & Update Strategy

## Example 1: Ring Deployment for Shared Model

**Rings**:
```
Ring 0 (Canary):     Internal tenants, platform team accounts
                     Auto-promote after 1 hour if error rate < 0.1%

Ring 1 (Early):      Free tier tenants opted into early access
                     Auto-promote after 4 hours if error rate < 0.1%

Ring 2 (Standard):   All remaining free and standard tier tenants
                     Manual gate + auto-promote after 24 hours

Ring 3 (Enterprise): Enterprise tier tenants
                     Manual gate + tenant notification 48 hours prior
```

**Traffic splitting**: Azure Front Door routing rules + Container Apps revision traffic splitting.

---

## Example 2: Blue-Green for Dedicated Tenants

**Per-tenant blue-green**:
```
1. Deploy new version to "green" Container App revision
2. Run health checks against green revision
3. Switch traffic: update Front Door backend to green
4. Monitor for 30 minutes
5. If healthy: decommission blue revision
6. If unhealthy: switch traffic back to blue
```

**Database compatibility**: Expand-contract migration pattern.
- Step 1 (expand): Add new column, keep old column
- Step 2 (deploy): New code writes to both, reads from new
- Step 3 (contract): After all tenants updated, drop old column

---

## Example 3: Communication Templates

**Planned update (48-hour notice)**:
```
Subject: Scheduled Platform Update - [Date]
Body:
  We will be releasing platform version X.Y.Z on [date] at [time] UTC.
  Expected duration: 30 minutes. No downtime expected.
  Changes: [link to changelog]
  Questions: support@insightpulseai.com
```

**Emergency update (immediate)**:
```
Subject: Emergency Maintenance - Action Required
Body:
  We are deploying a critical security fix immediately.
  Impact: Brief service interruption (< 5 minutes).
  Status: https://status.insightpulseai.com
  We will update you when the maintenance is complete.
```
