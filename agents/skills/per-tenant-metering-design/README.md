# Skill: Per-Tenant Metering Design

## Overview

Design per-tenant consumption measurement, collection pipelines, and cost attribution mechanisms for accurate billing and resource management.

## Owner

- **Persona**: billing-metering-architect

## Classification

- **Type**: encoded_preference

## Purpose

Ensure every tenant's resource consumption is accurately measured, collected, aggregated, and correlated to billing, enabling fair and transparent pricing.

## Key Topics

- Metering points (API calls, storage, compute time, data transfer)
- Collection pipeline architecture
- Aggregation and rating engine
- Correlation to billing and invoicing
- Anti-fraud and anomaly detection on usage

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Machine-readable skill definition |
| `prompt.md` | Agent prompt template |
| `checklist.md` | Design review checklist |
| `examples.md` | Reference examples |
| `EVALS.md` | Evaluation criteria |

## Cross-references

- `agents/personas/billing-metering-architect.md`
- `agents/knowledge/benchmarks/azure-multitenancy-checklist.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
