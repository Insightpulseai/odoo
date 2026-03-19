# Evaluations: Per-Tenant Metering Design

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| All billable events captured | 25% | No silent event drops in metering pipeline |
| No double counting | 25% | Idempotent aggregation verified |
| Rating accuracy | 25% | Output matches published pricing exactly |
| Audit trail complete | 15% | Raw events retained and queryable |
| Fraud detection active | 10% | Anomalous patterns detected and actioned |

## Eval Scenarios

### Scenario 1: Pipeline Event Loss
- **Input**: Event Hub partition temporarily unavailable for 2 minutes
- **Expected**: Local buffer retains events, replays after recovery, no events lost
- **Fail condition**: Events dropped during outage, tenant under-billed

### Scenario 2: Duplicate Event Processing
- **Input**: Same metering event delivered twice (at-least-once delivery)
- **Expected**: Aggregation deduplicates by event_id, count remains correct
- **Fail condition**: Tenant double-charged for same usage

### Scenario 3: Billing Dispute
- **Input**: Tenant disputes API call count on invoice
- **Expected**: Raw events queryable by tenant_id and time range, audit trail proves count
- **Fail condition**: Raw events purged or not queryable, dispute unresolvable

### Scenario 4: Overage Calculation
- **Input**: Tenant uses 150,000 API calls on a plan including 100,000
- **Expected**: Invoice shows base charge + 50,000 overage calls at published rate
- **Fail condition**: Overage not calculated or calculated at wrong rate
