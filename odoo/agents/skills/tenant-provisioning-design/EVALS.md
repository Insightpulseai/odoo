# Evaluations: Tenant Provisioning Design

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Idempotency | 25% | Re-running provisioning does not create duplicates |
| Rollback completeness | 25% | Partial failure leaves no orphaned resources |
| SLA measurability | 20% | Provisioning duration tracked and alerted |
| Automation coverage | 15% | No manual steps in the provisioning workflow |
| Configuration validation | 15% | Invalid tenant config rejected before resource creation |

## Eval Scenarios

### Scenario 1: Happy Path Provisioning

- **Input**: Valid tenant registration for standard tier
- **Expected**: Tenant fully operational within SLA, all resources created, welcome email sent
- **Fail condition**: Any manual intervention required, or SLA exceeded

### Scenario 2: Duplicate Registration

- **Input**: Same tenant ID submitted twice concurrently
- **Expected**: First request provisions, second is rejected or returns existing tenant
- **Fail condition**: Two sets of resources created for same tenant

### Scenario 3: Mid-Provisioning Failure

- **Input**: Database creation succeeds but Container App deployment fails
- **Expected**: Compensation action drops database, tenant marked as failed, admin notified
- **Fail condition**: Orphaned database remains, tenant in inconsistent state

### Scenario 4: Provisioning Under Load

- **Input**: 20 simultaneous provisioning requests
- **Expected**: All complete within SLA, no resource conflicts, no deadlocks
- **Fail condition**: Provisioning queue stalls, resources conflict, SLA breached for >10%

## Grading Rubric

| Grade | Criteria |
|-------|----------|
| A | All 5 criteria pass, design handles all 4 scenarios |
| B | 4/5 criteria pass, handles scenarios 1-3 |
| C | 3/5 criteria pass, handles scenario 1 |
| F | Fewer than 3 criteria pass or no rollback design |

## Pass Criteria

Minimum grade B required for production deployment. Grade A required for platforms with >100 tenants.
