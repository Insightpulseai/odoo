# Checklist: Billing and Metering Design

## Pre-flight

- [ ] Pricing model selected (flat, per-seat, usage-based, tiered, hybrid)
- [ ] Billable dimensions identified and prioritized
- [ ] Billing period defined (monthly, annual)
- [ ] Azure Marketplace listing decision made
- [ ] Tax and currency requirements documented

## Meter Definitions

- [ ] Each billable dimension has a meter specification
- [ ] Units of measure defined (API calls, GB, hours, seats)
- [ ] Aggregation method specified (sum, max, average, percentile)
- [ ] Collection interval defined (real-time, hourly, daily)
- [ ] Tier thresholds documented (free, standard, enterprise limits)

## Usage Event Pipeline

- [ ] Event schema defined with required fields (tenant_id, meter_id, quantity, timestamp, idempotency_key)
- [ ] Ingestion endpoint deployed (Event Hub, Service Bus, or HTTP)
- [ ] Deduplication logic implemented using idempotency_key
- [ ] Aggregation job runs on schedule, produces billing period summaries
- [ ] Dead-letter queue for failed events with alerting
- [ ] Pipeline throughput tested against expected event volume

## Rating Engine

- [ ] Pricing rules documented for each meter and tier
- [ ] Volume discount logic implemented
- [ ] Committed-use discount tracking (pre-paid credits)
- [ ] Overage calculation correct at tier boundaries
- [ ] Currency conversion handled if multi-currency
- [ ] Rating results auditable — input usage maps to output charges

## Marketplace Integration (if applicable)

- [ ] Azure Marketplace metering API integrated
- [ ] Usage events submitted within 24-hour deadline
- [ ] Submission retry logic handles transient failures
- [ ] Reconciliation job verifies accepted vs submitted events
- [ ] Marketplace-specific dimension IDs mapped to internal meters

## Invoice Generation

- [ ] Invoice generated from rated usage per billing period
- [ ] Tax calculated correctly per jurisdiction
- [ ] Invoice delivered to tenant (email, portal, API)
- [ ] Payment methods configured (credit card, wire, marketplace)
- [ ] Dunning workflow for failed payments

## Post-flight

- [ ] End-to-end test: usage event to invoice line item
- [ ] Duplicate event test: same event submitted twice, billed once
- [ ] Free tier test: usage throttled at limit
- [ ] Marketplace reconciliation: submitted matches accepted
- [ ] Billing audit: every charge traceable to source events
