# Skill: Tenant Provisioning Design

## Overview

Design automated tenant provisioning workflows that take a new tenant from registration to fully operational state within a defined SLA.

## Owner

- **Persona**: saas-platform-architect

## Classification

- **Type**: capability_uplift
- **Family**: azure-saas-mt

## Purpose

Ensure tenant provisioning is automated, idempotent, and observable. Manual provisioning does not scale and introduces inconsistency. This skill codifies the provisioning workflow from registration through resource allocation to onboarding completion.

## Canonical Fit

The canonical stack (Odoo CE + Azure Container Apps) uses this skill to design tenant onboarding for multi-tenant Odoo deployments. Provisioning may include database creation (Azure PostgreSQL), Container App configuration, Entra ID app registration, and Odoo database initialization.

## Key Topics

- Tenant registration flow: intake, validation, approval (if required)
- Resource allocation: ARM/Bicep templates parameterized per tenant tier
- Configuration templates: tenant-specific settings applied post-provisioning
- Onboarding automation: Azure Durable Functions or Logic Apps orchestration
- Provisioning SLA: target time, monitoring, alerting on breach
- Rollback: cleanup of partial provisioning on failure

## Inputs / Outputs

See `skill-contract.yaml` for full specification.

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
- `agents/skills/tenant-identity-isolation/`
- `agents/skills/tenant-lifecycle-automation/`
- `agents/knowledge/benchmarks/azure-saas-well-architected.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
