# Evaluations: Tenancy Model Selection

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Decision matrix complete | 25% | All three models scored against weighted criteria |
| Rationale documented | 25% | Selection justified with evidence, not opinion |
| Tier mapping clear | 20% | Every tier has a defined tenancy model |
| Migration path defined | 15% | Upgrade and downgrade procedures documented |
| Risks mitigated | 15% | Top risks identified with concrete mitigations |

## Eval Scenarios

### Scenario 1: Compliance Forces Dedicated
- **Input**: Tenant in healthcare sector requires HIPAA-compliant isolation
- **Expected**: Tenant placed in dedicated model regardless of pricing tier
- **Fail condition**: Compliance tenant placed in shared pool without isolation

### Scenario 2: Cost Justification for Dedicated
- **Input**: Small tenant requests dedicated infrastructure
- **Expected**: Cost analysis shows per-tenant cost vs shared; tier upgrade required
- **Fail condition**: Dedicated resources provisioned without cost justification

### Scenario 3: Noisy Neighbor in Shared Pool
- **Input**: Shared pool tenant causes resource contention
- **Expected**: Noisy neighbor mitigation activates (rate limiting, throttling)
- **Fail condition**: Other tenants degraded without mitigation

### Scenario 4: Hybrid Migration
- **Input**: Standard tenant upgrades to Enterprise
- **Expected**: Migration path executed with zero data loss and minimal downtime
- **Fail condition**: Data loss, extended downtime, or tenant locked in wrong model
