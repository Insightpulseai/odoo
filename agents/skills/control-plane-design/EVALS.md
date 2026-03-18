# Evaluations: Control Plane Design

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Catalog completeness | 20% | All tenant state resolvable from catalog alone |
| Fault domain isolation | 25% | Control plane operational when tenant stamps are down |
| API completeness | 20% | All management operations available via API |
| Audit trail | 20% | Every mutation logged with actor, action, timestamp |
| Configuration management | 15% | Config versioned, rollback tested |

## Eval Scenarios

### Scenario 1: Stamp Outage

- **Input**: One tenant stamp goes completely offline
- **Expected**: Control plane still operational, shows affected tenants as unhealthy, admin can investigate
- **Fail condition**: Control plane unavailable because it shares infrastructure with tenant stamp

### Scenario 2: Tenant Suspension

- **Input**: Admin suspends a tenant via control plane API
- **Expected**: Tenant state updated to "suspended", tenant users get 403, resources paused, audit logged
- **Fail condition**: Tenant still accessible, or no audit trail

### Scenario 3: Configuration Rollback

- **Input**: New configuration applied to tenant causes issues, admin rolls back
- **Expected**: Previous configuration version re-applied, tenant operational with old config
- **Fail condition**: Rollback fails or no previous version available

### Scenario 4: Audit Query

- **Input**: Security team requests all changes made to tenant "acme-corp" in last 30 days
- **Expected**: Audit log returns complete list of operations with actors and timestamps
- **Fail condition**: Incomplete audit trail or missing operations

## Grading Rubric

| Grade | Criteria |
|-------|----------|
| A | All 5 criteria pass, all 4 scenarios handled |
| B | 4/5 criteria pass, scenarios 1-3 handled |
| C | 3/5 criteria pass, catalog and API work |
| F | Control plane shares fault domain with tenants or no audit trail |

## Pass Criteria

Minimum grade B for production. Grade A required for platforms with >50 tenants.
