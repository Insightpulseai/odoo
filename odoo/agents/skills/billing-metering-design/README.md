# Skill: Billing and Metering Design

## Overview

Design consumption metering, pricing models, and billing integration for multi-tenant SaaS platforms, including Azure Marketplace integration.

## Owner

- **Persona**: saas-platform-architect

## Classification

- **Type**: capability_uplift
- **Family**: azure-saas-mt

## Purpose

Billing accuracy directly impacts revenue and tenant trust. This skill ensures usage metering is reliable, pricing models are correctly implemented, and billing integrates cleanly with Azure Marketplace or custom payment systems.

## Canonical Fit

The canonical stack (Odoo CE + Azure) can leverage Odoo's native invoicing module for billing while this skill designs the metering layer that feeds usage data into Odoo for invoice generation. Azure Marketplace integration enables distribution through Microsoft's channel.

## Key Topics

- Meter definitions: what dimensions to bill (users, API calls, storage, compute)
- Usage event pipeline: collection, deduplication, aggregation
- Rating engine: converting raw usage to monetary amounts per pricing model
- Azure Marketplace: metering API integration for marketplace-listed SaaS
- Invoice generation: Odoo-integrated or standalone billing
- Tenant billing dashboard: self-service usage visibility

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
- `agents/skills/saas-observability-design/`
- `agents/skills/tenant-provisioning-design/`
- `agents/knowledge/benchmarks/azure-saas-well-architected.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
