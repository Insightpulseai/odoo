# Evaluations: Tenant Context Mapping

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Every request mapped | 25% | No request proceeds without tenant-id |
| Context propagated | 25% | Tenant-id present at every service boundary |
| Async context preserved | 25% | Background jobs and messages carry tenant-id |
| Observability complete | 25% | Logs, traces, and metrics include tenant-id |

## Eval Scenarios

### Scenario 1: Missing Tenant Header
- **Input**: API request without X-Tenant-Id header and no subdomain mapping
- **Expected**: 400 Bad Request returned, request logged as unresolved
- **Fail condition**: Request processed under a default or null tenant

### Scenario 2: Service-to-Service Propagation
- **Input**: Service A calls Service B on behalf of tenant
- **Expected**: Service B receives and validates tenant-id in call metadata
- **Fail condition**: Service B processes request without tenant context

### Scenario 3: Queue Message Without Tenant
- **Input**: Message published to queue without tenant_id in metadata
- **Expected**: Consumer dead-letters the message, alert raised
- **Fail condition**: Message processed without tenant context

### Scenario 4: Log Search by Tenant
- **Input**: Support request to investigate issue for specific tenant
- **Expected**: All logs, traces, and metrics filterable by tenant-id
- **Fail condition**: Logs missing tenant-id, requiring manual correlation
