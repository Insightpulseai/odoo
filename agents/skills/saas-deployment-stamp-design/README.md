# Skill: SaaS Deployment Stamp Design

## Overview

Design deployment stamp patterns for horizontally scaling multi-tenant SaaS platforms across regions and capacity boundaries.

## Owner

- **Persona**: saas-platform-architect

## Classification

- **Type**: capability_uplift
- **Family**: azure-saas-mt

## Purpose

A deployment stamp is a self-contained unit of infrastructure that serves a subset of tenants. Stamps enable horizontal scaling, blast radius reduction, and geo-distribution. This skill designs the stamp topology, tenant assignment, and lifecycle management.

## Canonical Fit

The canonical stack (Odoo CE + Azure Container Apps) can use stamps to scale beyond single-environment limits. Each stamp contains a Container Apps Environment, PostgreSQL Flexible Server, and Front Door backend. Stamps can be regional (Southeast Asia, East US) or capacity-based.

## Key Topics

- Stamp composition: which Azure resources form one stamp
- Capacity planning: max tenants per stamp based on resource limits
- Tenant-to-stamp assignment: placement algorithm and rebalancing
- Stamp lifecycle: creation from IaC, scaling, draining, decommission
- Geo-distribution: regional stamps for data residency and latency
- Traffic routing: Azure Front Door backend pools per stamp

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
- `agents/skills/saas-networking-design/`
- `agents/skills/tenant-provisioning-design/`
- `agents/knowledge/benchmarks/azure-saas-well-architected.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
