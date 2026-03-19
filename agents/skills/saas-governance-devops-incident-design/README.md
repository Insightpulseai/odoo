# Skill: SaaS Governance, DevOps & Incident Design

## Overview

Design governance policies, CI/CD pipelines with tenant awareness, and incident management with tenant context for multi-tenant SaaS platforms.

## Owner

- **Persona**: saas-platform-architect

## Classification

- **Type**: encoded_preference

## Purpose

Ensure compliance policy enforcement, tenant-aware deployment pipelines, and incident management that includes tenant blast radius assessment.

## Key Topics

- Compliance policy enforcement via Azure Policy
- Deployment pipeline with tenant-aware rollout (ring, canary)
- Incident escalation with tenant context
- Audit logging with tenant dimension
- Change management for multi-tenant updates

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Machine-readable skill definition |
| `prompt.md` | Agent prompt template |
| `checklist.md` | Design review checklist |
| `examples.md` | Reference examples |
| `EVALS.md` | Evaluation criteria |

## Cross-references

- `agents/personas/saas-platform-architect.md`
- `agents/knowledge/benchmarks/azure-saas-well-architected.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
