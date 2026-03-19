# Skill: Tenant Context Mapping

## Overview

Design how incoming requests are mapped to a tenant and how tenant context is propagated through the entire stack.

## Owner

- **Persona**: multitenancy-architect

## Classification

- **Type**: encoded_preference

## Purpose

Ensure every request, message, and background job is associated with exactly one tenant, and that tenant context flows through all middleware, services, and data access layers.

## Key Topics

- Request-to-tenant mapping strategies (subdomain, header, token claim, URL path)
- Middleware/gateway tenant resolution
- Tenant context propagation through service mesh
- Background job and async message tenant context
- Audit trail per tenant

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
