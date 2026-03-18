# Prompt: Billing and Metering Design

## Context

You are the SaaS Platform Architect designing consumption metering and billing for a multi-tenant platform on Azure.

## Task

Given the pricing model, billable dimensions, and billing period, produce a billing and metering design covering:

1. **Meter definitions**: Specify each billable dimension — unit of measure, aggregation method (sum, max, average), collection interval, and tier thresholds
2. **Usage event pipeline**: Architecture for collecting usage events from application services. Cover event schema, ingestion (Event Hub, Service Bus), deduplication, and aggregation into billing periods
3. **Rating engine**: Logic to convert aggregated usage into monetary amounts. Handle tiered pricing, volume discounts, committed-use discounts, and overage charges
4. **Azure Marketplace integration**: If marketplace listing is required, design the metering API integration — event format, submission schedule, error handling, and reconciliation
5. **Invoice generation**: How rated usage becomes an invoice — integration with Odoo accounting or standalone billing. Cover tax calculation, currency handling, and payment method support
6. **Billing dashboard**: Tenant-facing views showing current usage, projected costs, historical invoices, and payment status

## Constraints

- Usage events must be idempotent — duplicate events must not cause double billing
- Pipeline must guarantee at-least-once delivery with application-level deduplication
- Every charge must be traceable to source usage events (audit trail)
- Free tier enforcement must be real-time (not retroactive billing)
- Marketplace metering API has a 24-hour submission deadline for usage events

## Output Format

Produce a structured document with:
- Meter definition table
- Event pipeline architecture diagram
- Rating rules (pseudocode or decision table)
- Marketplace API integration sequence
- Sample invoice with line items mapped to meters
