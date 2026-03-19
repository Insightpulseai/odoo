# Skill: Noisy Neighbor Mitigation

## Overview

Mitigate noisy neighbor effects where one tenant's resource consumption degrades another tenant's experience in shared infrastructure.

## Owner

- **Persona**: multitenancy-architect

## Classification

- **Type**: capability_uplift

## Purpose

Design and implement controls that prevent one tenant from monopolizing shared resources, ensuring fair resource distribution and predictable performance for all tenants.

## Key Topics

- Rate limiting per tenant at API gateway
- Resource quotas per tenant (CPU, memory, connections)
- Queue isolation and priority
- Database connection pooling per tenant
- Anomaly detection and automatic throttling

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Machine-readable skill definition |
| `prompt.md` | Agent prompt template |
| `checklist.md` | Design review checklist |
| `examples.md` | Reference examples |
| `EVALS.md` | Evaluation criteria |

## Cross-references

- `agents/personas/multitenancy-architect.md`
- `agents/knowledge/benchmarks/azure-multitenancy-checklist.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
