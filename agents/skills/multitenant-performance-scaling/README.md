# Skill: Multitenant Performance & Scaling

## Overview

Design and validate multi-tenant performance and scaling strategies covering compute, database, storage, CDN, and load testing.

## Owner

- **Persona**: saas-operations-judge

## Classification

- **Type**: capability_uplift

## Purpose

Ensure the platform scales efficiently under multi-tenant load, with per-tenant performance predictability and cost-effective resource utilization.

## Key Topics

- Compute auto-scaling per tenant load
- Database connection pool sizing and scaling
- Storage tier selection per tenant tier
- CDN configuration for multi-tenant content delivery
- Load testing with multi-tenant workload profiles

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Machine-readable skill definition |
| `prompt.md` | Agent prompt template |
| `checklist.md` | Design review checklist |
| `examples.md` | Reference examples |
| `EVALS.md` | Evaluation criteria |

## Cross-references

- `agents/personas/saas-operations-judge.md`
- `agents/knowledge/benchmarks/azure-saas-well-architected.md`
- `agents/knowledge/benchmarks/azure-multitenancy-checklist.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
