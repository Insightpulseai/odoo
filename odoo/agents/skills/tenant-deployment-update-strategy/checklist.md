# Checklist: Tenant Deployment & Update Strategy

## Deployment Strategy

- [ ] Deployment model selected (ring, canary, blue-green)
- [ ] Rings defined with tenant assignment criteria
- [ ] Traffic splitting mechanism configured
- [ ] Feature flags integrated for per-tenant control
- [ ] Dedicated tenant deployments handled separately

## Rollout Plan

- [ ] Each ring has defined health check gates
- [ ] Automatic promotion criteria defined (error rate, latency, success rate)
- [ ] Manual approval gates configured for production rings
- [ ] Hold and abort conditions documented
- [ ] Rollout timeline estimated with buffer for issues

## Rollback

- [ ] Per-tenant rollback procedure documented
- [ ] Platform-wide rollback procedure documented
- [ ] Maximum rollback time defined (< 15 minutes)
- [ ] Database migration rollback tested (expand-contract pattern)
- [ ] Rollback does not cause data loss for any tenant
- [ ] Rollback procedure tested in staging environment

## Versioning

- [ ] API versioning strategy selected (path, header, query param)
- [ ] Backward compatibility rules documented
- [ ] Deprecation policy defined (minimum support period)
- [ ] Sunset notification process documented
- [ ] Version negotiation mechanism implemented

## Communication

- [ ] Planned update notification sent N days in advance
- [ ] Status page updated during rollout
- [ ] Emergency update notification process defined
- [ ] Post-update summary sent to affected tenants
- [ ] Opt-in early access program for interested tenants
