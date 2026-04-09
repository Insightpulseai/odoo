# Benchmark Model

## Purpose

Define the canonical benchmark model for building and operating Odoo on Azure.

This document exists to prevent benchmark drift and to keep architecture discussions aligned to the actual target stack.

---

## 1. Canonical benchmark statement

We are building an **Azure-native Odoo operating model**.

This is **not** benchmarked against SAP on Azure as the primary application or runtime architecture.

The primary benchmark is:

- **Odoo CE 18 + OCA + thin `ipai_*` bridges** for ERP/application architecture
- **Azure Container Apps + Azure Front Door + Azure Key Vault + Managed Identity + PostgreSQL** for runtime architecture
- **Microsoft Foundry** for AI/copilot architecture
- **AvaTax-style capability** for tax/compliance product ambition

SAP on Azure may be used only as a **reference for enterprise operating discipline**, not as the primary application/runtime benchmark.

---

## 2. Why SAP on Azure is not the primary benchmark

SAP on Azure is the wrong primary benchmark for this workload because it assumes a different application and infrastructure shape:

- different compute expectations
- different database expectations
- different landscape/networking assumptions
- different team and operating-scale assumptions

For this stack, SAP landing-zone guidance is mostly non-applicable as the main architecture benchmark.

Use it only for:
- governance rigor
- observability discipline
- release safety
- operational maturity
- enterprise deployment seriousness

Do **not** use it to define:
- Odoo runtime topology
- addon/module architecture
- repo structure
- AI/copilot design
- deployment unit boundaries

---

## 3. Primary benchmark hierarchy

### 3.1 ERP / application benchmark
**Odoo CE 18 + OCA + thin bridge doctrine**

Use this layer to decide:
- what belongs in Odoo
- what should be solved with OCA first
- what should become a thin `ipai_*` bridge
- what should stay outside Odoo

### 3.2 Runtime benchmark
**Azure Container Apps + Azure-native platform services**

Use this layer to decide:
- runtime hosting model
- ingress / edge model
- identity and secrets pattern
- health probes
- revision/cutover/rollback model
- PostgreSQL connectivity and hardening
- observability and diagnostics

### 3.3 AI / copilot benchmark
**Microsoft Foundry**

Use this layer to decide:
- model and agent orchestration pattern
- project/client integration model
- AI service boundaries
- extraction/explanation workflow
- external AI execution plane

### 3.4 Tax / compliance product benchmark
**AvaTax-style capability benchmark**

Use this layer to decide:
- automation quality expectations
- integration depth expectations
- tax/compliance product maturity targets

This is a capability benchmark, not a localization or direct deployment benchmark.

### 3.5 Enterprise ops maturity reference
**SAP on Azure**

Use this layer only to borrow:
- operational seriousness
- landing-zone discipline
- governance patterns
- monitoring and support posture

Do not use it as the primary design source for the actual Odoo runtime.

---

## 4. Benchmark-to-repo mapping

| Benchmark layer | Primary repo(s) |
|---|---|
| Odoo CE 18 + OCA + thin bridge doctrine | `odoo` |
| Azure Container Apps + platform services | `infra`, `platform` |
| Microsoft Foundry | `agent-platform`, `platform` |
| AvaTax-style capability benchmark | `odoo`, `agent-platform`, `docs` |
| SAP-on-Azure operational discipline | `docs`, `infra`, `.github` |

---

## 5. Benchmark implications for architecture decisions

### Use Odoo/OCA benchmark when deciding:
- addon design
- module boundaries
- OCA-first reuse
- thin bridge doctrine
- posting blockers
- workflow state ownership

### Use Azure runtime benchmark when deciding:
- ACA topology
- Front Door/WAF posture
- Key Vault / Managed Identity patterns
- revision strategy
- runtime diagnostics
- PostgreSQL hardening

### Use Foundry benchmark when deciding:
- AI service integration
- agent orchestration
- chat/retrieval/extraction boundaries
- external AI runtime ownership

### Use AvaTax-style benchmark when deciding:
- product ambition for tax/compliance automation
- explainability expectations
- review workflow quality
- integration depth

### Use SAP discipline benchmark only when deciding:
- enterprise governance posture
- release discipline
- operational maturity
- cross-environment rigor

---

## 6. Current-state validation

This benchmark model is consistent with the current Azure posture and recent infrastructure work:

- PostgreSQL ZoneRedundant HA enabled
- managed identity enabled across all apps
- diagnostic settings completed
- remaining hardening items focused on:
  - ACA VNet injection
  - ACA zone redundancy
  - Azure Policy baseline
  - closing public PostgreSQL access
  - geo-redundant backup handled through future server recreation/migration

These are Azure-native runtime concerns, not SAP landscape concerns.

---

## 7. Canonical wording to use

### Preferred wording
- "Azure-native Odoo operating model"
- "Odoo on Azure using Azure Container Apps as the runtime benchmark"
- "SAP on Azure as an operational-discipline reference only"
- "Foundry as the AI/copilot benchmark"
- "AvaTax-style capability benchmark for tax/compliance product quality"

### Wording to avoid
- "SAP on Azure with Odoo"
- "Odoo is our SAP landscape equivalent"
- "SAP landing zone is the main deployment benchmark"
- "We are using SAP architecture as the primary model for Odoo runtime"

---

## 8. Final doctrine

The canonical benchmark doctrine is:

1. **Odoo + OCA** defines the ERP/application architecture.
2. **Azure Container Apps + Azure-native services** define the runtime architecture.
3. **Microsoft Foundry** defines the AI/copilot architecture.
4. **AvaTax-style product capability** defines tax/compliance ambition.
5. **SAP on Azure** informs enterprise operating discipline only.

Any document that contradicts this benchmark model should be updated.

---

*Created: 2026-04-09*
