# Evaluations: Tenant Deployment & Update Strategy

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Ring structure defined | 20% | Tenants grouped into rings with clear criteria |
| Health gates enforced | 25% | Every ring has health checks before promotion |
| Rollback tested | 25% | Rollback completes within 15 minutes, no data loss |
| Enterprise protected | 15% | Enterprise tenants in last ring with advance notice |
| Communication sent | 15% | Tenants notified before, during, and after updates |

## Eval Scenarios

### Scenario 1: Ring 1 Failure
- **Input**: Ring 1 deployment shows 1% error rate (threshold: 0.1%)
- **Expected**: Promotion halted, Ring 1 rolled back, Ring 0 preserved for debugging
- **Fail condition**: Errors propagate to Ring 2 or Ring 3

### Scenario 2: Database Migration Rollback
- **Input**: New migration adds column; rollback needed after Ring 2
- **Expected**: Expand-contract pattern allows old code to work with new schema
- **Fail condition**: Rollback requires schema change that breaks Ring 3 tenants

### Scenario 3: Enterprise Tenant Skip
- **Input**: Enterprise tenant requests to skip this update cycle
- **Expected**: Tenant excluded from Ring 3 rollout, stays on previous version
- **Fail condition**: No mechanism to exclude specific tenants from rollout

### Scenario 4: Emergency Hotfix
- **Input**: Critical security vulnerability requires immediate patch
- **Expected**: Expedited rollout: Ring 0 (5 min) -> all rings (30 min), with notification
- **Fail condition**: Emergency process takes longer than 1 hour end-to-end
