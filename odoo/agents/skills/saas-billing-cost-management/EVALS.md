# Evaluations: SaaS Billing & Cost Management

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Pricing model complete | 20% | Tiers defined with feature gates and limits |
| Cost attribution possible | 25% | Per-tenant cost can be calculated from Azure data |
| Budget alerts configured | 20% | Both platform and per-tenant alerts defined |
| Billing pipeline auditable | 20% | End-to-end trail from metering to invoice |
| Antipatterns addressed | 15% | Known billing antipatterns identified and mitigated |

## Eval Scenarios

### Scenario 1: Free Tier Cost Overrun
- **Input**: Free tier tenant generates excessive API calls
- **Expected**: Hard limit enforced, tenant throttled or upgraded
- **Fail condition**: Free tier tenant incurs unbounded infrastructure cost

### Scenario 2: Shared Cost Attribution
- **Input**: 10 tenants share a PostgreSQL Flexible Server
- **Expected**: Cost allocation formula distributes DB cost by usage weight
- **Fail condition**: Shared DB cost unattributed or split equally regardless of usage

### Scenario 3: Usage Spike Detection
- **Input**: Tenant API usage increases 10x in one hour
- **Expected**: Anomaly alert fires, investigation triggered before invoice
- **Fail condition**: Spike goes unnoticed until monthly bill

### Scenario 4: Tier Downgrade
- **Input**: Enterprise tenant downgrades to Standard mid-cycle
- **Expected**: Prorated billing, feature gates applied, dedicated resources deprovisioned
- **Fail condition**: Tenant retains enterprise features at standard pricing
