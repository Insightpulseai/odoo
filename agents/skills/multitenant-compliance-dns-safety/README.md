# Skill: Multitenant Compliance & DNS Safety

## Overview

Verify per-tenant compliance requirements, manage custom domain lifecycle, prevent subdomain takeover, and ensure data residency.

## Owner

- **Persona**: tenant-isolation-judge

## Classification

- **Type**: encoded_preference

## Purpose

Ensure that each tenant's compliance, data residency, and DNS requirements are met, and that domain management does not create security vulnerabilities.

## Key Topics

- Per-tenant compliance mapping (HIPAA, SOC 2, GDPR, etc.)
- Custom domain management and certificate lifecycle
- Subdomain takeover prevention
- Data residency enforcement
- Certificate management automation

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Machine-readable skill definition |
| `prompt.md` | Agent prompt template |
| `checklist.md` | Design review checklist |
| `examples.md` | Reference examples |
| `EVALS.md` | Evaluation criteria |

## Cross-references

- `agents/personas/tenant-isolation-judge.md`
- `agents/knowledge/benchmarks/azure-multitenancy-checklist.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
