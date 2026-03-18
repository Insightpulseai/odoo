# Skill: Tenant Lifecycle Automation

## Overview

Automate the full tenant lifecycle: onboarding, provisioning, configuration, updates, and offboarding.

## Owner

- **Persona**: tenant-lifecycle-operator

## Classification

- **Type**: encoded_preference

## Purpose

Ensure tenant provisioning and management is fully automated, eliminating manual steps that limit scale and introduce errors.

## Key Topics

- Tenant provisioning workflow (create resources, configure, seed data)
- Onboarding automation (signup to first login)
- Configuration management per tenant
- Offboarding (data retention, resource cleanup, account deactivation)
- Self-service tenant management portal

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
