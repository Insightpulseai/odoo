# Skill: SaaS Migration Design

## Overview

Design zero-downtime tenant migration between stamps, tiers, or regions with data integrity verification and tested rollback procedures.

## Owner

- **Persona**: saas-platform-architect

## Classification

- **Type**: capability_uplift
- **Family**: azure-saas-mt

## Purpose

Tenant migration is one of the most complex operational tasks in multi-tenant SaaS. It involves coordinated data movement, service cutover, and DNS changes while maintaining availability. This skill provides proven migration patterns with rollback safety nets.

## Canonical Fit

The canonical stack (Odoo CE + Azure Container Apps) may need to migrate tenants between PostgreSQL servers (stamp migration), upgrade from shared to dedicated database (tier change), or move to a different region (data residency). Each requires coordinated Odoo database migration, Container App reconfiguration, and Front Door routing updates.

## Key Topics

- Migration types: intra-stamp, inter-stamp, cross-region, tier change
- Data migration: PostgreSQL logical replication, pg_dump/restore, online migration
- Service cutover: Container App routing, Front Door backend change
- DNS cutover: subdomain re-pointing with TTL management
- Verification: data checksums, row counts, application smoke tests
- Rollback: restoration procedure with defined time window

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Machine-readable skill definition |
| `prompt.md` | Agent prompt template |
| `checklist.md` | Design review checklist |
| `examples.md` | Reference examples |
| `EVALS.md` | Evaluation criteria |

## Cross-references

- `agents/skills/saas-deployment-stamp-design/`
- `agents/skills/data-isolation-pattern-design/`
- `agents/skills/saas-networking-design/`
- `agents/knowledge/benchmarks/azure-saas-well-architected.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
