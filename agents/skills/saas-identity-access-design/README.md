# Skill: SaaS Identity & Access Design

## Overview

Design the tenant/user identity model, authorization framework, and zero trust posture for multi-tenant SaaS platforms on Azure.

## Owner

- **Persona**: saas-platform-architect

## Classification

- **Type**: encoded_preference

## Purpose

Establish clear separation between tenant identity and user identity, enforce tenant context in all authorization decisions, and implement zero trust principles.

## Key Topics

- Tenant identity vs user identity distinction
- Token claims for tenant context propagation
- RBAC per tenant with role hierarchy
- Zero trust principles applied to multi-tenant
- Entra ID integration for tenant federation

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
