# Skill: Multitenancy Readiness Judge

## Overview

Judge whether a SaaS platform is operationally ready for multi-tenant production use by verifying isolation, SLOs, testing evidence, and operational clarity.

## Owner

- **Persona**: saas-operations-judge

## Classification

- **Type**: encoded_preference

## Purpose

Provide a structured go/no-go assessment for multi-tenant readiness, ensuring all architectural, operational, and testing requirements are met before tenants are onboarded.

## Key Topics

- SLO/SLA verification per tier
- Isolation test evidence review
- Scale test evidence review
- Chaos test evidence review
- Control plane vs data plane clarity
- Deployment strategy validation

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
