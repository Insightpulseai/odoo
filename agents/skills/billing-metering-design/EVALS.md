# Evaluations: Billing and Metering Design

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Metering accuracy | 25% | Aggregated usage matches source events within 0.1% |
| Deduplication | 20% | Duplicate events do not cause double billing |
| Rating correctness | 20% | Charges match pricing rules for all tier boundaries |
| Audit traceability | 20% | Every invoice line traceable to source usage events |
| Free tier enforcement | 15% | Usage blocked or degraded at free tier limit in real-time |

## Eval Scenarios

### Scenario 1: Duplicate Usage Event

- **Input**: Same usage event submitted twice with identical idempotency_key
- **Expected**: Event stored once, tenant billed once
- **Fail condition**: Double billing for same usage

### Scenario 2: Tier Boundary Pricing

- **Input**: Tenant uses 50,001 API calls (1 over standard plan inclusion of 50,000)
- **Expected**: Invoice shows base plan + 1 overage unit charged correctly
- **Fail condition**: Overage calculated incorrectly (off-by-one) or entire usage billed as overage

### Scenario 3: Free Tier Limit Enforcement

- **Input**: Free tier tenant reaches 1,000 API call limit mid-month
- **Expected**: Subsequent API calls throttled (429) or upgrade prompt shown
- **Fail condition**: Free tier tenant continues unlimited usage

### Scenario 4: End-to-End Billing Audit

- **Input**: Request audit trail for a specific invoice line item
- **Expected**: Chain from invoice line to rated usage to aggregated events to individual source events
- **Fail condition**: Any link in the audit chain is missing

## Grading Rubric

| Grade | Criteria |
|-------|----------|
| A | All 5 criteria pass, all 4 scenarios handled |
| B | 4/5 criteria pass, scenarios 1-3 handled |
| C | 3/5 criteria pass, basic metering works |
| F | Billing accuracy below 99% or duplicate billing possible |

## Pass Criteria

Minimum grade B for production. Grade A required for Azure Marketplace listed offerings.
