# Checklist: SaaS Migration Design

## Pre-flight

- [ ] Migration type classified (intra-stamp, inter-stamp, cross-region)
- [ ] Downtime tolerance confirmed with tenant
- [ ] Data volume measured and migration duration estimated
- [ ] Destination stamp capacity verified
- [ ] Communication plan prepared (tenant, support, ops team)

## Pre-Migration

- [ ] Source data backup created and verified
- [ ] Destination resources provisioned (database, compute, storage)
- [ ] Replication or migration tool configured and tested with dry run
- [ ] DNS TTL lowered in advance (if DNS cutover needed)
- [ ] Monitoring dashboards prepared for migration metrics
- [ ] Rollback procedure documented and reviewed

## Data Migration

- [ ] Initial data sync started (full copy or logical replication)
- [ ] Replication lag monitored and within acceptable threshold
- [ ] Incremental sync catching up to near-zero lag
- [ ] Data integrity checksum computed on source
- [ ] No schema conflicts on destination

## Cutover

- [ ] Write traffic paused (if required for consistency)
- [ ] Final replication catch-up completed
- [ ] Data integrity checksum verified on destination (matches source)
- [ ] Application configuration updated to point to destination
- [ ] DNS or Front Door routing updated
- [ ] Control plane tenant catalog updated with new stamp assignment
- [ ] Write traffic resumed

## Post-Migration Verification

- [ ] Application smoke tests pass on destination
- [ ] Row counts match between source and destination
- [ ] Data checksums match between source and destination
- [ ] SLA metrics (latency, error rate) within normal range
- [ ] Tenant admin notified of successful migration
- [ ] No errors in application logs post-cutover

## Rollback Readiness

- [ ] Source data preserved for rollback window (minimum 24 hours)
- [ ] Rollback procedure tested before migration
- [ ] Rollback DNS/routing change prepared
- [ ] Rollback decision criteria defined (what triggers rollback)
- [ ] Rollback completion time estimated and acceptable

## Post-flight

- [ ] Source resources cleaned up after rollback window expires
- [ ] Migration metrics documented (duration, data volume, downtime)
- [ ] Lessons learned captured
- [ ] Migration runbook updated with any adjustments
- [ ] Tenant confirmation of normal operation received
