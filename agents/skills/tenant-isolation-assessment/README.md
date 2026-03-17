# Skill: Tenant Isolation Assessment

## Overview

Judge skill that assesses whether a multi-tenant platform's tenant isolation meets the security and compliance bar. Returns a structured verdict with evidence.

## Owner

- **Persona**: saas-security-judge

## Classification

- **Type**: encoded_preference (judge pattern)
- **Family**: azure-saas-mt

## Purpose

This is a **judge skill** — it evaluates rather than builds. Given the current architecture and configuration, it produces a structured assessment of tenant isolation across four domains (identity, data, network, encryption) and returns a verdict: ISOLATED, PARTIAL, or NOT_ISOLATED.

## Canonical Fit

The canonical stack (Odoo CE + Azure Container Apps) needs regular isolation assessments as the platform evolves. This skill validates that identity boundaries (Entra ID), data isolation (PostgreSQL per-tenant or RLS), network segmentation (VNET, private endpoints), and encryption (TDE, per-tenant keys) meet the required bar.

## Verdict Definitions

| Verdict | Meaning | Action |
|---------|---------|--------|
| **ISOLATED** | All four domains meet isolation requirements | Continue monitoring |
| **PARTIAL** | Some domains have gaps with documented severity | Remediate gaps per priority |
| **NOT_ISOLATED** | Critical gaps allow cross-tenant access | Stop: remediate before production |

## Key Topics

- Identity boundary verification: token validation, RBAC scoping
- Data access path audit: query paths, RLS effectiveness, backup isolation
- Network segmentation check: VNET isolation, private endpoints, NSG rules
- Encryption verification: TDE, per-tenant keys, key rotation

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Machine-readable skill definition |
| `prompt.md` | Agent prompt template |
| `checklist.md` | Assessment checklist |
| `examples.md` | Reference examples |
| `EVALS.md` | Evaluation criteria |

## Cross-references

- `agents/skills/tenant-identity-isolation/`
- `agents/skills/data-isolation-pattern-design/`
- `agents/skills/saas-networking-design/`
- `agents/knowledge/benchmarks/azure-multitenancy-checklist.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
