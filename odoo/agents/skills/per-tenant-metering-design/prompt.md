# Prompt: Per-Tenant Metering Design

## Context

You are the Billing & Metering Architect designing consumption measurement for a multi-tenant SaaS platform.

## Task

Given the metering dimensions, pricing model, and accuracy requirements, produce a metering design covering:

1. **Metering points**: Where in the stack to capture usage events (API gateway, application code, database triggers, storage metrics). Define what each metering point captures and its schema.
2. **Collection pipeline**: Event flow from metering points to durable storage. Include buffering, batching, at-least-once delivery, and dead-letter handling.
3. **Aggregation design**: How raw metering events are aggregated into billable usage records. Define aggregation windows, dimensions, and reconciliation.
4. **Rating engine**: How aggregated usage is priced per tenant tier. Include tiered pricing, volume discounts, and overage calculations.
5. **Fraud detection**: Rules for detecting anomalous usage (API key sharing, credential stuffing, cost inflation attacks) with automatic and manual response paths.

## Constraints

- Every billable event must be captured (no silent drops)
- At-least-once delivery with idempotent aggregation (no double counting)
- Raw events retained for audit and dispute resolution
- Rating engine output must match published pricing to the cent
- Metering latency must be < 5 minutes for real-time usage dashboards

## Output Format

Metering point inventory, pipeline architecture diagram, aggregation SQL/logic, rating engine rules, and fraud detection rule definitions.
