# Platform Engineering — Canonical Benchmark

## Overview

The ERP-on-Azure platform is also an internal developer platform. Platform engineering
improves security, compliance, costs, and time-to-business value through better developer
experiences and self-service inside a secure governed framework.

---

## Operating principles

- Each customer (internal team) is important
- Adopt a product mindset
- Empower with self-service
- Use inventories to manage assets
- Measure and refine continuously

---

## Capability model

The platform should be assessed and evolved across:

| Capability | Description |
|-----------|-------------|
| **Investment** | Resources, staffing, and organizational commitment to platform |
| **Adoption** | How widely and effectively teams use the platform |
| **Governance** | Policy enforcement, compliance, and security controls |
| **Provisioning and management** | Self-service infrastructure, environment, and service lifecycle |
| **Interfaces** | How teams interact with the platform (API, CLI, IDE, portal) |
| **Measurement and feedback** | Metrics, feedback loops, and continuous improvement |

---

## Preferred delivery pattern

1. Start with a **thinnest viable platform**
2. Extend existing engineering surfaces first (GitHub, Azure DevOps, CLI, IDE)
3. Encode best practices into templates and paved paths
4. Use everything-as-code to drive repeatable fulfillment
5. Add portal layers only when they clearly simplify fragmented workflows

---

## Interface priority

1. **Existing engineering tools** — GitHub, Azure DevOps, CLI, IDE extensions
2. **APIs and automation entrypoints** — REST, CLI, pipeline triggers
3. **Portal experiences** — only for aggregation and friction reduction

---

## Paved paths

High-value paved paths for the ERP-on-Azure platform:

| Path | Description |
|------|-------------|
| New module | Scaffold, test, deploy a new `ipai_*` module |
| New environment | Bootstrap dev/staging/prod with DB, secrets, ingress |
| Deploy revision | Build → test → stage → promote via YAML pipeline |
| Add AI capability | Wire Pulser skill/tool through Foundry |
| Add integration | Connect external service via approved pattern |
| Observability | Access logs, traces, metrics for any workload |

---

## Self-service with guardrails

Each self-service workflow must:

- Follow an approved automation path
- Enforce policy (security, compliance, cost) automatically
- Be documented in the platform catalog
- Be measurable (adoption, success rate, time-to-complete)

---

*Last updated: 2026-04-10*
