# Skill: Tenant Deployment & Update Strategy

## Overview

Design tenant-aware deployment and update rollout strategies that minimize risk and maximize control over which tenants receive changes and when.

## Owner

- **Persona**: tenant-lifecycle-operator

## Classification

- **Type**: encoded_preference

## Purpose

Ensure platform updates reach tenants in a controlled, observable manner with the ability to halt, roll back, or skip specific tenants.

## Key Topics

- Ring deployment with tenant grouping
- Canary deployment per tenant subset
- Blue-green with tenant routing
- Update compatibility and versioning
- Per-tenant rollback capability

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
