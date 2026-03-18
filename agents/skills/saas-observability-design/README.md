# Skill: SaaS Observability Design

## Overview

Design multi-tenant observability that provides per-tenant visibility into health, performance, and SLA compliance without cross-tenant data leakage.

## Owner

- **Persona**: saas-platform-architect

## Classification

- **Type**: capability_uplift
- **Family**: azure-saas-mt

## Purpose

Without tenant-aware observability, operators cannot diagnose per-tenant issues, enforce SLAs, or detect noisy neighbors. This skill ensures all telemetry carries tenant context and provides actionable per-tenant dashboards.

## Canonical Fit

The canonical stack (Odoo CE + Azure Container Apps) uses Azure Monitor, Application Insights, and Log Analytics. This skill designs tenant ID propagation through Odoo request middleware, Container Apps logs, and PostgreSQL query logs to enable per-tenant observability.

## Key Topics

- Tenant context propagation: enriching all telemetry with tenant_id
- Per-tenant metrics: request rate, latency, error rate, resource usage
- Log partitioning: Log Analytics workspace strategy for multi-tenant logs
- Distributed tracing: correlation IDs spanning Odoo, background workers, and external services
- SLA dashboards: availability and latency tracking per tenant tier
- Anomaly detection: baseline comparison for tenant-level performance deviations

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Machine-readable skill definition |
| `prompt.md` | Agent prompt template |
| `checklist.md` | Design review checklist |
| `examples.md` | Reference examples |
| `EVALS.md` | Evaluation criteria |

## Cross-references

- `agents/skills/saas-resource-organization/`
- `agents/skills/noisy-neighbor-mitigation/`
- `agents/skills/control-plane-design/`
- `agents/knowledge/benchmarks/azure-saas-well-architected.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
