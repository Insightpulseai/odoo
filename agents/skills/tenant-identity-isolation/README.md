# Skill: Tenant Identity Isolation

## Overview

Design tenant identity boundaries using Microsoft Entra ID to ensure authentication and authorization are scoped per tenant with no cross-tenant access.

## Owner

- **Persona**: saas-platform-architect

## Classification

- **Type**: capability_uplift
- **Family**: azure-saas-mt

## Purpose

Identity isolation is the foundation of multi-tenant security. Without proper tenant context in tokens and strict boundary enforcement, data leakage between tenants becomes possible. This skill ensures identity boundaries are correctly designed from app registration through token validation to RBAC enforcement.

## Canonical Fit

The canonical stack (Odoo CE + Azure Container Apps) transitions from Keycloak to Entra ID. This skill informs the identity architecture for multi-tenant Odoo, ensuring each tenant's users, roles, and service identities are properly isolated.

## Key Topics

- App registration model: single multi-tenant app vs per-tenant app registrations
- Custom token claims: embedding tenant_id, tier, and roles in JWT
- Per-tenant RBAC: role definitions scoped to tenant resources
- Cross-tenant prevention: middleware validation, policy enforcement
- Managed identities: service-to-service auth within tenant boundary
- Token validation: claim verification at API gateway and application layers

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Machine-readable skill definition |
| `prompt.md` | Agent prompt template |
| `checklist.md` | Design review checklist |
| `examples.md` | Reference examples |
| `EVALS.md` | Evaluation criteria |

## Cross-references

- `agents/skills/saas-resource-organization/`
- `agents/skills/tenant-provisioning-design/`
- `agents/skills/data-isolation-pattern-design/`
- `agents/knowledge/benchmarks/azure-saas-well-architected.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
