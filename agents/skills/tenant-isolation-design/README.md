# Skill: Tenant Isolation Design

## Overview

Design tenant isolation boundaries and enforcement mechanisms across compute, data, network, and key management layers.

## Owner

- **Persona**: multitenancy-architect

## Classification

- **Type**: encoded_preference

## Purpose

Define how tenants are isolated from each other at every layer of the stack, ensuring that a compromise or failure in one tenant cannot affect another.

## Key Topics

- Compute isolation: shared app, shared container, dedicated container, dedicated VM
- Data isolation: row-level security, schema-per-tenant, database-per-tenant
- Network isolation: shared VNet, subnet-per-tenant, VNet-per-tenant
- Key/secret isolation: shared Key Vault with access policies vs dedicated Key Vault
- Isolation enforcement and testing

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
