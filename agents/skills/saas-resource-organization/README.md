# Skill: SaaS Resource Organization

## Overview

Design subscription topology, resource group structure, naming conventions, and tagging policies for multi-tenant SaaS platforms on Azure.

## Owner

- **Persona**: saas-platform-architect

## Classification

- **Type**: encoded_preference

## Purpose

Ensure Azure resources are organized to support multi-tenant operations with clear cost attribution, access boundaries, and operational clarity.

## Key Topics

- Subscription strategy: single vs multiple subscriptions per environment/tenant
- Resource group topology: per-tenant, per-service, or hybrid grouping
- Naming conventions with tenant identifiers embedded
- Tagging policy for cost attribution, environment, and ownership
- RBAC scoping at subscription, resource group, and resource levels

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
