# Skill: Data Isolation Pattern Design

## Overview

Select and implement the correct data isolation pattern for multi-tenant SaaS, balancing security, compliance, performance, and cost.

## Owner

- **Persona**: saas-platform-architect

## Classification

- **Type**: capability_uplift
- **Family**: azure-saas-mt

## Purpose

Data isolation is the most consequential architectural decision in multi-tenant SaaS. The wrong choice leads to data leakage, compliance failures, or unsustainable costs. This skill provides a structured decision framework and implementation guidance for each isolation pattern.

## Canonical Fit

The canonical stack uses PostgreSQL on Azure Flexible Server. Odoo CE natively supports database-per-tenant (`--database` flag). This skill helps decide between database-per-tenant (Odoo's default), schema-per-tenant, or row-level isolation for different tenant tiers, and how to implement hybrid patterns.

## Key Topics

- Database-per-tenant: maximum isolation, higher cost, simpler queries
- Schema-per-tenant: good isolation, moderate cost, PostgreSQL schema support
- Row-level isolation: shared tables with RLS policies, lowest cost, highest complexity
- Hybrid patterns: different isolation per tenant tier
- Per-tenant encryption: customer-managed keys, key rotation
- Tenant data lifecycle: backup, restore, export, deletion scoped to tenant

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
- `agents/skills/tenant-provisioning-design/`
- `agents/knowledge/benchmarks/azure-saas-well-architected.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
