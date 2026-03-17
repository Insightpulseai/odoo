# Examples: Per-Tenant Metering Design

## Example 1: Metering Event Schema

```json
{
  "event_id": "evt-uuid-123",
  "tenant_id": "tenant-uuid-456",
  "timestamp": "2026-03-17T10:30:00.123Z",
  "metering_point": "api-gateway",
  "dimension": "api_call",
  "quantity": 1,
  "metadata": {
    "method": "POST",
    "endpoint": "/api/v1/orders",
    "status_code": 200,
    "response_time_ms": 145,
    "request_size_bytes": 1024,
    "response_size_bytes": 2048
  }
}
```

---

## Example 2: Collection Pipeline Architecture

```
Metering Points (API GW, App, DB)
        |
        v
  Event Hub (partitioned by tenant_id)
        |
        v
  Stream Analytics (5-min tumbling window)
        |
        +---> Cosmos DB (raw events, 90-day TTL)
        |
        +---> SQL Database (aggregated usage, permanent)
                    |
                    v
              Rating Engine (nightly batch)
                    |
                    v
              Invoice Generation
```

**Resilience**: Each metering point buffers events locally for 5 minutes. Event Hub provides at-least-once delivery. Stream Analytics deduplicates by event_id.

---

## Example 3: Rating Engine Rules

**Tier: Standard ($15/user/mo + overage)**:
```python
def calculate_charge(tenant_usage, tier_config):
    base_charge = tier_config.base_price  # $15/user
    included_calls = tier_config.included_api_calls  # 100,000

    api_calls = tenant_usage.api_call_count
    overage_calls = max(0, api_calls - included_calls)
    overage_charge = overage_calls * tier_config.overage_rate  # $0.005/call

    storage_gb = tenant_usage.storage_bytes / (1024**3)
    included_storage = tier_config.included_storage_gb  # 50
    storage_overage = max(0, storage_gb - included_storage)
    storage_charge = storage_overage * tier_config.storage_rate  # $0.10/GB

    return {
        "base": base_charge,
        "api_overage": overage_charge,
        "storage_overage": storage_charge,
        "total": base_charge + overage_charge + storage_charge
    }
```

---

## Example 4: Fraud Detection Rule

**API key sharing detection**:
```
Rule: api_key_geographic_spread
Condition: Single API key used from > 5 distinct IP geolocations in 1 hour
Action: Flag for review, send alert to tenant admin
Escalation: If pattern persists 24h, throttle to 50% rate limit
```
