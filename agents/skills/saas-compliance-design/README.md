# Skill: SaaS Compliance Design

## Overview

Design compliance controls for multi-tenant SaaS platforms, ensuring regulatory requirements (GDPR, SOC2, data residency) are met through technical architecture.

## Owner

- **Persona**: saas-platform-architect

## Classification

- **Type**: encoded_preference
- **Family**: azure-saas-mt

## Purpose

Compliance is not optional for SaaS platforms handling personal or financial data. This skill translates regulatory requirements into enforceable technical controls — data residency via stamp placement, GDPR rights via automated workflows, and audit logging via immutable event stores.

## Canonical Fit

The canonical stack (Odoo CE + Azure Container Apps) processes business data including PII (contacts, invoices). This skill ensures data residency enforcement via Azure Policy, GDPR data subject rights via Odoo export/delete workflows, and SOC2 audit logging via Azure Monitor and tenant audit trails.

## Key Topics

- Data residency: enforcing regional data placement via Azure Policy and stamp assignment
- GDPR data subject rights: export (right of access), delete (right to erasure), portability
- SOC2 controls: access logging, change management, incident response
- Data classification: PII, financial, confidential, public — handling rules per class
- Audit logging: immutable, timestamped, actor-attributed event records
- Compliance reporting: automated evidence collection for auditors

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Machine-readable skill definition |
| `prompt.md` | Agent prompt template |
| `checklist.md` | Design review checklist |
| `examples.md` | Reference examples |
| `EVALS.md` | Evaluation criteria |

## Cross-references

- `agents/skills/data-isolation-pattern-design/`
- `agents/skills/tenant-lifecycle-automation/`
- `agents/skills/saas-observability-design/`
- `agents/knowledge/benchmarks/azure-saas-well-architected.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
