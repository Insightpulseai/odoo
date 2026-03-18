# Skill: SaaS Billing & Cost Management

## Overview

Design pricing models, cost management strategies, and billing infrastructure for multi-tenant SaaS platforms on Azure.

## Owner

- **Persona**: saas-platform-architect

## Classification

- **Type**: encoded_preference

## Purpose

Ensure pricing models are sustainable, costs are attributable to tenants, and billing infrastructure is designed into the platform from the start.

## Key Topics

- Pricing model design (per-seat, per-usage, tiered, hybrid)
- Tier definition and feature gating
- Azure Cost Management integration for per-tenant cost tracking
- Budget alerts and cost anomaly detection
- Billing pipeline architecture

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Machine-readable skill definition |
| `prompt.md` | Agent prompt template |
| `checklist.md` | Design review checklist |
| `examples.md` | Reference examples |
| `EVALS.md` | Evaluation criteria |

## Cross-references

- `agents/personas/saas-platform-architect.md`
- `agents/knowledge/benchmarks/azure-saas-well-architected.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
