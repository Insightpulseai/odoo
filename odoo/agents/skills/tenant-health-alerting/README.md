# Skill: Tenant Health & Alerting

## Overview

Design per-tenant monitoring, metrics, and alerting to ensure tenant-level visibility into platform health and performance.

## Owner

- **Persona**: tenant-lifecycle-operator

## Classification

- **Type**: encoded_preference

## Purpose

Provide tenant-dimensioned observability so that issues affecting individual tenants are detected and resolved before they escalate.

## Key Topics

- Tenant dimension in all metrics
- Per-tenant SLO tracking
- Alert routing by tenant tier
- Per-tenant dashboards
- Anomaly detection per tenant

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Machine-readable skill definition |
| `prompt.md` | Agent prompt template |
| `checklist.md` | Design review checklist |
| `examples.md` | Reference examples |
| `EVALS.md` | Evaluation criteria |

## Cross-references

- `agents/personas/tenant-lifecycle-operator.md`
- `agents/knowledge/benchmarks/azure-multitenancy-checklist.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
