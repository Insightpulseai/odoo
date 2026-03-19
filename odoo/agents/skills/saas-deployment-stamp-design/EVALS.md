# Evaluations: SaaS Deployment Stamp Design

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Stamp deployability | 25% | New stamp deployed from IaC in under 30 minutes |
| Blast radius isolation | 25% | Stamp failure does not affect other stamps |
| Tenant mobility | 20% | Tenant can migrate between stamps with zero downtime |
| Capacity planning | 15% | Scaling triggers prevent capacity exhaustion |
| Geo-compliance | 15% | Tenants served from region matching data residency requirements |

## Eval Scenarios

### Scenario 1: Stamp Capacity Threshold

- **Input**: Stamp reaches 80% tenant capacity
- **Expected**: Alert fires, new stamp provisioning initiated, new tenants routed to new stamp
- **Fail condition**: New tenants assigned to over-capacity stamp, or no alerting

### Scenario 2: Stamp Failure Isolation

- **Input**: Simulate complete stamp failure (all resources in one stamp unavailable)
- **Expected**: Tenants on failed stamp experience outage. Tenants on other stamps unaffected.
- **Fail condition**: Failure cascades to other stamps

### Scenario 3: Tenant Migration Between Stamps

- **Input**: Enterprise tenant needs to move from shared stamp to dedicated stamp
- **Expected**: Data migrated, DNS updated, zero downtime during cutover
- **Fail condition**: Downtime during migration, or data loss

### Scenario 4: New Stamp from Template

- **Input**: Deploy a new stamp using the IaC template
- **Expected**: All resources created, health checks pass, ready to accept tenants
- **Fail condition**: Manual steps required, or stamp not operational after deployment

## Grading Rubric

| Grade | Criteria |
|-------|----------|
| A | All 5 criteria pass, all 4 scenarios handled |
| B | 4/5 criteria pass, scenarios 1-3 handled |
| C | 3/5 criteria pass, stamps deploy from IaC |
| F | Stamps require manual setup or failure cascades |

## Pass Criteria

Minimum grade B for production multi-region. Grade A for mission-critical SaaS.
