# Skill: Tenancy Model Selection

## Overview

Select the appropriate tenancy model (shared pool, dedicated silo, or hybrid) based on cost, isolation, performance, and compliance tradeoffs.

## Owner

- **Persona**: multitenancy-architect

## Classification

- **Type**: encoded_preference

## Purpose

Provide a structured decision framework for choosing between shared, dedicated, and hybrid tenancy models based on platform requirements.

## Key Topics

- Shared pool model: cost-efficient, lower isolation
- Dedicated silo model: high isolation, higher cost
- Hybrid model: tiered approach combining both
- Decision matrix covering cost, isolation, performance, compliance, and operational complexity
- Migration paths between models

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Machine-readable skill definition |
| `prompt.md` | Agent prompt template |
| `checklist.md` | Design review checklist |
| `examples.md` | Reference examples |
| `EVALS.md` | Evaluation criteria |

## Cross-references

- `agents/personas/multitenancy-architect.md`
- `agents/knowledge/benchmarks/azure-multitenancy-checklist.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
