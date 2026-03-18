# Evaluations: SaaS Governance, DevOps & Incident Design

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Policies enforceable | 20% | Azure Policy definitions deployed and active |
| Deployment tenant-aware | 25% | Pipeline knows which tenants are affected per ring |
| Incident blast radius | 25% | Blast radius calculable within 5 minutes |
| Audit logs complete | 15% | Every action logged with tenant-id dimension |
| Change management documented | 15% | Process exists and is followed for all changes |

## Eval Scenarios

### Scenario 1: Untagged Resource Creation
- **Input**: Developer creates a Container App without required tags
- **Expected**: Azure Policy denies the creation with clear error message
- **Fail condition**: Resource created without tags, discovered later

### Scenario 2: Ring Promotion with Errors
- **Input**: Ring 1 deployment shows 0.5% error rate increase
- **Expected**: Promotion to Ring 2 blocked, Ring 1 rolled back automatically
- **Fail condition**: Errors propagate to Ring 2/3 (enterprise tenants)

### Scenario 3: Incident Tenant Identification
- **Input**: Database connection pool exhaustion on shared PostgreSQL
- **Expected**: Within 5 minutes, all affected tenants identified and notified
- **Fail condition**: Tenant list unavailable or incomplete during incident

### Scenario 4: Audit Log Tenant Access
- **Input**: Enterprise tenant requests their own audit logs for compliance
- **Expected**: Tenant can access only their own logs via self-service API
- **Fail condition**: Tenant sees other tenants' logs or cannot access their own
