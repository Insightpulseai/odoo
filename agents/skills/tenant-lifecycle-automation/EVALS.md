# Evaluations: Tenant Lifecycle Automation

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Zero manual steps | 25% | Provisioning fully automated end-to-end |
| Provisioning time | 20% | Shared < 5 min, dedicated < 30 min |
| Idempotent operations | 20% | Retry-safe at every step |
| Offboarding compliant | 20% | Data export + retention policy enforced |
| Self-service functional | 15% | Tenant admins can manage their own resources |

## Eval Scenarios

### Scenario 1: Provisioning Partial Failure
- **Input**: Database schema creation succeeds but DNS configuration fails
- **Expected**: Retry from DNS step only, previous steps not repeated
- **Fail condition**: Full re-provisioning required, or tenant stuck in broken state

### Scenario 2: Concurrent Provisioning
- **Input**: 10 tenants sign up simultaneously
- **Expected**: All 10 provisioned within SLO, no resource conflicts
- **Fail condition**: Provisioning queue backlog causes SLO breach

### Scenario 3: Offboarding Data Export
- **Input**: Tenant cancels and requests data export
- **Expected**: Export available within 24 hours, includes all tenant data
- **Fail condition**: Data export incomplete or unavailable before grace period expires

### Scenario 4: Reactivation During Grace Period
- **Input**: Tenant requests reactivation on day 15 of 30-day grace period
- **Expected**: Tenant reactivated with all data intact, billing resumed
- **Fail condition**: Data already deleted or tenant must re-onboard from scratch
