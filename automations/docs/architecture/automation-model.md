# Automation Architecture Model

> Placeholder for the canonical automation architecture documentation.

## Overview

Automations are categorized into three types:

1. **Scheduled** -- Cron-driven jobs (e.g., nightly cleanup, report generation)
2. **Event-driven** -- Triggered by webhooks or queue messages (e.g., PR events, deployment hooks)
3. **Maintenance** -- Housekeeping tasks (e.g., log rotation, stale resource pruning)

## Execution Surface

- **Runtime**: Azure Container Apps Jobs (serverless, on-demand)
- **Scheduling**: Azure Container Apps scheduled triggers or GitHub Actions cron
- **Secrets**: Azure Key Vault via Managed Identity
- **Observability**: Azure Monitor + Application Insights

## Connectors

Connectors are thin wrappers around external APIs (GitHub, Azure, Odoo). They handle:
- Authentication and credential resolution
- Retry with exponential backoff
- Rate limit awareness
- Structured error reporting

## Registry

All jobs and connectors are registered in:
- `automations/ssot/schedules/schedule-registry.yaml`
- `automations/ssot/connectors/connector-registry.yaml`

<!-- TODO: Expand with sequence diagrams and failure mode analysis -->
