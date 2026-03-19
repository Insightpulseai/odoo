# Checklist: Per-Tenant Metering Design

## Metering Points

- [ ] API gateway metering captures all API calls with tenant-id
- [ ] Storage metering captures bytes stored per tenant
- [ ] Compute metering captures processing time per tenant
- [ ] Data transfer metering captures egress per tenant
- [ ] Each metering point has a defined event schema
- [ ] Metering points cover all billable dimensions

## Collection Pipeline

- [ ] Events buffered locally before transmission (resilience)
- [ ] At-least-once delivery guaranteed (Event Hub, Service Bus)
- [ ] Dead-letter queue configured for failed events
- [ ] Pipeline health monitoring with alert on event loss
- [ ] Batch processing with configurable window size
- [ ] Pipeline latency < 5 minutes end-to-end

## Aggregation

- [ ] Aggregation windows defined (hourly, daily, monthly)
- [ ] Idempotent aggregation (deduplication by event ID)
- [ ] Raw events retained for audit (minimum 90 days)
- [ ] Aggregation reconciliation checks scheduled
- [ ] Per-tenant usage summaries available via API

## Rating Engine

- [ ] Rating rules match published pricing exactly
- [ ] Tiered pricing handled (volume discounts applied correctly)
- [ ] Overage calculation correct for usage beyond tier limits
- [ ] Rating engine output auditable (input usage + rules = output charge)
- [ ] Currency and tax handling defined

## Fraud Detection

- [ ] API key sharing detection rules defined
- [ ] Credential stuffing detection active
- [ ] Usage spike anomaly detection configured
- [ ] Automatic response actions defined (throttle, alert, block)
- [ ] Manual review process for flagged accounts
