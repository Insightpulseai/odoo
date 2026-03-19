# Skill: Control Plane Design

## Overview

Design the centralized control plane that manages tenant lifecycle, configuration, health, and administrative operations for a multi-tenant SaaS platform.

## Owner

- **Persona**: saas-platform-architect

## Classification

- **Type**: capability_uplift
- **Family**: azure-saas-mt

## Purpose

The control plane is the brain of a multi-tenant SaaS platform. It maintains the tenant catalog, orchestrates provisioning, monitors health, and provides the administrative interface. Without a well-designed control plane, tenant management becomes ad-hoc and error-prone.

## Canonical Fit

The canonical stack (Odoo CE + Azure Container Apps) needs a control plane to manage tenant databases, Container App configurations, DNS entries, and billing state. The control plane runs independently from tenant workloads, ensuring administrative access even when tenant stamps are degraded.

## Key Topics

- Tenant catalog: central database of all tenant metadata, state, and configuration
- Configuration management: tenant-specific settings, feature flags, limits
- Health monitoring: aggregated health status across all tenants and stamps
- Admin portal: web UI for platform operators to manage tenants
- Control plane API: RESTful API for automation and integration
- Audit logging: immutable record of all administrative operations

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
- `agents/skills/tenant-lifecycle-automation/`
- `agents/skills/saas-observability-design/`
- `agents/knowledge/benchmarks/azure-saas-well-architected.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
