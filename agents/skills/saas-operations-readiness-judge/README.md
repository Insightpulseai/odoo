# Skill: SaaS Operations Readiness Judge

## Overview

Judge skill that assesses overall SaaS operations readiness by evaluating six operational domains and returning a structured verdict: READY, NOT_READY, or CONDITIONAL.

## Owner

- **Persona**: saas-operations-judge

## Classification

- **Type**: encoded_preference (judge pattern)
- **Family**: azure-saas-mt

## Purpose

This is a **judge skill** — it evaluates operational readiness rather than building systems. It assesses six operational domains (provisioning, monitoring, incident response, scaling, billing, compliance) and produces a go/no-go verdict for production launches, new tier introductions, or regional expansions.

## Canonical Fit

The canonical stack (Odoo CE + Azure Container Apps) needs operational readiness validation before launching multi-tenant services. This skill ensures provisioning is automated, monitoring covers all tenants, incident response is defined, scaling handles growth, billing is accurate, and compliance is maintained.

## Verdict Definitions

| Verdict | Meaning | Action |
|---------|---------|--------|
| **READY** | All six domains at acceptable maturity | Proceed to launch |
| **CONDITIONAL** | Most domains ready, specific conditions must be met | Meet conditions, then launch |
| **NOT_READY** | Critical gaps in one or more domains | Stop: resolve blockers first |

## Key Topics

- Provisioning: automation coverage, success rate, SLA compliance
- Monitoring: per-tenant metrics, alerting, SLA dashboards
- Incident response: runbooks, escalation, on-call schedule, post-incident reviews
- Scaling: auto-scaling rules, capacity planning, load testing
- Billing: metering accuracy, invoice correctness, dispute handling
- Compliance: certifications, audit posture, data residency enforcement

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Machine-readable skill definition |
| `prompt.md` | Agent prompt template |
| `checklist.md` | Assessment checklist |
| `examples.md` | Reference examples |
| `EVALS.md` | Evaluation criteria |

## Cross-references

- `agents/skills/tenant-provisioning-design/`
- `agents/skills/saas-observability-design/`
- `agents/skills/billing-metering-design/`
- `agents/skills/saas-compliance-design/`
- `agents/skills/tenant-isolation-assessment/`
- `agents/knowledge/benchmarks/azure-saas-well-architected.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
