# Evaluations: SaaS Migration Design

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Data integrity | 30% | Checksums match source and destination |
| Downtime minimization | 25% | Write downtime under 5 minutes (zero-downtime type) |
| Rollback capability | 20% | Rollback completes within defined window |
| Tenant impact | 15% | Other tenants unaffected during migration |
| Verification completeness | 10% | All smoke tests pass post-migration |

## Eval Scenarios

### Scenario 1: Zero-Downtime Inter-Stamp Migration

- **Input**: Migrate tenant with 10 GB database between stamps in same region
- **Expected**: Read availability maintained throughout, write downtime < 5 minutes, checksums match
- **Fail condition**: Data loss, extended downtime, or checksum mismatch

### Scenario 2: Migration Failure and Rollback

- **Input**: Migration fails during cutover (destination database corruption)
- **Expected**: Rollback initiated, tenant operational on source stamp within 15 minutes
- **Fail condition**: Rollback takes longer than defined window, or data loss during rollback

### Scenario 3: Cross-Region Migration with Data Purge

- **Input**: EU tenant migrated from APAC to EU stamp for data residency
- **Expected**: All data in EU region, zero data remaining in APAC, GDPR compliant
- **Fail condition**: Data residue in source region after migration

### Scenario 4: Concurrent Tenant Impact

- **Input**: Migrate one tenant while 50 other tenants on same source stamp are active
- **Expected**: No performance degradation for other tenants during migration
- **Fail condition**: Other tenants experience latency increase or errors

## Grading Rubric

| Grade | Criteria |
|-------|----------|
| A | All 5 criteria pass, all 4 scenarios handled |
| B | 4/5 criteria pass, scenarios 1-3 handled |
| C | 3/5 criteria pass, data integrity and rollback work |
| F | Data integrity not verified or rollback not possible |

## Pass Criteria

Minimum grade B for production migrations. Grade A required for zero-downtime SLA commitments.
