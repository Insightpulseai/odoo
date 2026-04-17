# MATURITY_CHECKPOINT

> **Locked:** 2026-04-17
> **Authority:** Architecture decision checkpoint validated against live Azure + Databricks state.
> **Companions:** [`lifecycle-maturity-matrix.md`](../strategy/lifecycle-maturity-matrix.md) · [`d365-fo-parity-matrix.md`](../strategy/d365-fo-parity-matrix.md)

---

## Purpose

Single decision-point document for internal and external use. Answers: *where are we in the Microsoft industry solution lifecycle, how do we compare against D365 F&O, and what do we do next?* Validated against live runtime state 2026-04-17 — not aspirational.

---

## Executive summary

IPAI is in the **reference architecture and accelerator-proving phase** of the Microsoft Cloud for Financial Services lifecycle. Platform substrate is live (ACA + Databricks + AFD + KV + UC), dual inference is confirmed (Foundry gpt-4.1 + Databricks Llama 4/405B/Qwen3), and ADO delivery telemetry is flowing into Databricks. The intelligence layer is the differentiator and it is working. The ERP layer (Odoo CE + OCA) is operational. The packaging layer — repeatable vertical offers, marketplace listing, demo-ready bundle — is what we are building now.

**Lifecycle position:** Reference architecture proven with live telemetry, moving into industry solution packaging.
**First vertical candidate:** Finance Operations / Compliance Control Tower.

---

## Benchmark lens 1 — Microsoft Cloud for Financial Services

| # | Stage | Microsoft concept | Our evidence | Gaps | Status |
|---|---|---|---|---|---|
| 1 | **Platform foundation** | Landing zone + application resources separated | ACA, PG (`pg-ipai-odoo`), AFD, KV, Databricks Premium+UC, canonical SSOT, 8-component architecture locked, Azure Pipelines as sole CI/CD | Old-sub resources scaling down (3 still up due to DNS dependency); Foundry frontier models blocked (715-123420) | ✅ Done (in cleanup) |
| 2 | **Policy / governance** | Compliance, transparency, policy initiatives | Naming standards, authority model, SSOT direction, 8-tag taxonomy, tag validator CI, security policy, 3-tier defense doctrine, no-custom-identity doctrine | Production Azure Policy deny not yet enforced; compliance evidence packs incomplete for marketplace | ⚠️ Partial |
| 3 | **Architecture shaping** | CAF alignment, modernization guides | Target operating model defined, Odoo vs Databricks roles split, Pulser vs Genie roles clear, canonical entities/marts/serving surfaces, 7-layer model stack, MCP topology (3-phase) | Architecture docs authored; not all IaC-enforced; some SSOT is aspirational | ⚠️ Partial |
| 4 | **Reference architecture proof** | Diagrams + real data for common workloads | ✅ **Current center of gravity.** ADO telemetry live in Databricks, finance workbook modeled (10 team members, 9 task categories, 6-level approval chain), dual inference confirmed (11 model serving endpoints READY), 7 UC catalogs including `odoo_erp` foreign catalog (federation live), Odoo HTTP 200 on `/web/health`, 30+ Azure Pipelines YAML files | Gold marts not populated from live DLT pipeline; Genie Space not yet created (portal action blocked by gold gap) | ✅ Architecture proven · ⚠️ Data gap |
| 5 | **Industry solution packaging** | Industry-specific capabilities, transactable offers | Pulser branding defined, ISV Success enrolled (MpnId 7097325), Partner Center verified, TBWA\SMP program templated | No marketplace offer published; no repeatable install path; no demo script; no implementation boundary doc | 🔴 Not started |
| 6 | **Case study / success story** | Customer deployment evidence, measurable outcomes | None — no customer deployment yet | No before/after metrics; no external reference | 🔴 Not started |

---

## Interpretation

We are solidly at the top of Stage 4, with Stage 5 work required before any external claim of "industry solution" is valid. The intelligence layer (Databricks, Genie, Pulser) is our differentiator and the part that is most proven. The ERP layer (Odoo CE + OCA) is operational. The gap is in packaging, not in capability.

---

## Benchmark lens 2 — Dynamics 365 Finance & Operations

### 1. Implementation lifecycle

| D365 F&O category | Our equivalent | Maturity | Gap | Next milestone |
|---|---|---|---|---|
| FastTrack onboarding | ISV Success enrollment (MpnId 7097325) | Medium | No structured onboarding playbook for customers | Build customer onboarding checklist |
| Implementation lifecycle | Architecture shaping + reference proving | Strong | Not yet a repeatable rollout motion | Package into vertical offer bundle |
| Preparing for go-live | Feature Ship-Readiness Checklist (5 gates) | Defined | Not executed against live deployment | Execute checklist for R2 first-slice |
| Go-live readiness review | No external reviewer yet | Gap | No FastTrack equivalent | Partner with MS ISV Success for review |

### 2. Integrations

| D365 F&O category | Our equivalent | Maturity | Gap | Next milestone |
|---|---|---|---|---|
| Business events | Odoo webhooks + `ipai-odoo-mcp` (P0 gap) | Emerging | `ipai-odoo-mcp` not yet built | Build the MCP server (Phase 2 per MCP topology) |
| Data entities / OData | OData entity map (`ssot/semantic/odata-entity-map.yaml`) | Strong | OData not yet served (contract only) | Implement OData serving layer |
| Power Automate integration | Azure Functions + Logic Apps (Foundry tools) | Medium | No customer-facing workflow automation yet | Wire Pulser → Foundry → Odoo action loop |
| Dual-write / virtual entities | Lakehouse Federation (`odoo_erp` foreign catalog) | Strong | Zero-copy read works; no write-back | Keep read-only per doctrine |

### 3. Finance domain

| D365 F&O category | Our equivalent | Maturity | Gap | Next milestone |
|---|---|---|---|---|
| General ledger | Odoo CE `account.move` + `account.move.line` | Strong (CE) | No advanced consolidation yet | Add OCA `account_consolidation` when multi-entity |
| Accounts payable | Odoo CE AP + OCA `account_payment_order` | Strong | AP aging mart planned but not populated | Populate `gold_finance_ap_aging` |
| Accounts receivable | Odoo CE AR + `ipai_ar_collections` (planned) | Emerging | AR collections overlay not built | Build `ipai_ar_collections` thin delta |
| Cash and bank management | Odoo CE bank + OCA `account_reconcile_oca` | Medium | Cash position mart not populated | Populate `gold_finance_cash_position` |
| Compliance / regulatory | `ipai_bir_tax_compliance` + `ipai_bir_2307` | Emerging | BIR modules partially built; control tower = contract only | Populate `gold_finance_bir_deadline_control` |
| Financial reporting | Databricks gold marts + Genie + dashboards | Strong (architecture) | Gold marts not populated yet | Run DLT → populate gold → create Genie Space |
| Budgets / FP&A | OCA `account_budget_oca` + `ipai_finance_ppm` | Emerging | PPM overlay in dev_ppm catalog | Wire PPM data into gold marts |
| Fixed assets | OCA `account_asset_management` | Available | Not installed/tested | Install when asset management use case materializes |
| Expense management | Odoo CE `hr.expense` + `ipai_expense_liquidation` (planned) | Emerging | PH expense liquidation bridge planned | Build `ipai_expense_liquidation` |

### 4. Intelligence layer (IPAI differentiator)

| D365 F&O category | Our equivalent | Maturity | Gap | Next milestone |
|---|---|---|---|---|
| Analytics | Databricks gold marts + dashboards + Databricks One | **Strong** | Gold tables not populated from live pipeline | Run DLT pipeline |
| Business documents | Evidence packs + workbook-driven workflow data | Medium | No DMS integration yet | Build evidence-pack MCP (Phase 3) |
| Financial reporting | Semantic layer (46 metrics, 16 dims, OData entity map) | **Strong** (architecture) | Not yet materialized as running views | Create UC views from semantic definitions |
| Regulatory reporting | BIR control tower (4 modules, 16 business questions) | **Strong** (model) | Contract-only; not yet live data | Ingest BIR calendar → populate facts |

### 5. Development / administration

| D365 F&O category | Our equivalent | Maturity | Gap | Next milestone |
|---|---|---|---|---|
| Extensibility | `ipai_*` module doctrine (CE → OCA → thin delta) | **Strong** | Module introspection docs incomplete for some modules | Complete `MODULE_INTROSPECTION.md` per module |
| Continuous delivery | Azure Pipelines (sole CI/CD authority) | **Strong** | 30+ pipeline files defined; not all wired to ADO environments | Wire environment gates |
| Cloud deployment | ACA + Databricks + Foundry on Sponsored sub | **Strong** | Old-sub resources scaling down (3 still up, DNS-dependent); 13 apps at min=0 | Complete decom after DNS migration |
| Lifecycle services | SSOT YAML + architecture docs + memory system | Medium | No customer-facing lifecycle portal equivalent | Build demo path for customer onboarding |
| Organization admin | Entra + UC + tag governance + RBAC | Medium | Tag policy not enforced via Azure Policy deny yet | Enable Policy deny for untagged resources |

### 6. Supply chain / HR / other domains

| D365 F&O category | Our equivalent | Maturity | Gap | Next milestone |
|---|---|---|---|---|
| Supply chain management | Odoo CE `stock.*` + `purchase.*` + `mrp.*` | Available (CE) | Not the current vertical focus | Defer until customer demand |
| Human resources | Odoo CE `hr.*` + OCA payroll | Available (CE) | Not the current vertical focus | Defer |
| Commerce / retail | Not in scope | N/A | Not competing on retail | N/A |
| Project management | Odoo CE `project.*` + `ipai_finance_ppm` | Emerging | PPM bridge in progress | Complete `ipai_ppm_bridge` |

---

## What is already proven

### 1. Platform substrate (live, confirmed 2026-04-17)

- Odoo on Sponsored sub: HTTP 200 on `/web/health` (confirmed live)
- PG server `pg-ipai-odoo` on Sponsored sub: Ready state
- 13 old-sub ACA apps scaled to min=0; 3 still running due to DNS dependency (not a risk, managed decom)
- Azure Pipelines: 30+ YAML files (exceeds prior "26" claim)
- ACA environment `ipai-odoo-dev-env-v2`: active, DNS-bound, AFD in front

### 2. Intelligence layer (live, confirmed 2026-04-17)

- 11 Databricks model serving endpoints: READY (dual inference confirmed)
  - Foundry path: `gpt-4.1` via `services.ai.azure.com`
  - Databricks path: Llama 4 Scout, Llama 3.1 405B, Qwen3-235B
- 7 UC catalogs including `odoo_erp` foreign catalog (federation live; zero-copy read from PG)
- ADO delivery telemetry flowing into Databricks bronze layer
- Finance workbook modeled: 10 team members, 9 task categories, 6-level approval chain
- Semantic layer: 46 metrics, 16 dimensions, OData entity map authored

### 3. Governance + doctrine

- No-custom-identity doctrine enforced: `ipai_auth_oidc` sunsetted, Odoo ↔ Entra via standard OCA OIDC
- 3-tier defense pattern documented for Pulser mutating agents (substrate / configuration / planning)
- Feature Ship-Readiness Checklist (5 gates: Product, Correctness, Runtime, Safety, Evidence) in place
- Azure Pipelines as sole CI/CD authority (GitHub Actions removed 2026-04-14)
- ISV Success enrolled (MpnId 7097325), Partner Center verified

### 4. Finance domain models (authored, not yet live-data)

- BIR control tower: 4 modules, 16 business questions, contract authored
- Finance marts: AP aging, cash position, BIR deadlines — gold schema defined in DLT notebooks
- CDM export pipeline: `ipai-odoo-cdm-export` created on `dbw-ipai-dev` (6 Phase-1 CDM entities)
- `ipai_finance_fpa`, `ipai_finance_cash`, `ipai_finance_ap_ar` modules present in `addons/ipai/`

---

## What is not yet finished

### 1. Gold layer not populated

- DLT pipeline `ipai-odoo-cdm-export` created but first run not triggered
- Known blocker: `path=` argument conflict on Gold tables (fix required before first run)
- Gold marts empty: `gold_finance_ap_aging`, `gold_finance_cash_position`, `gold_finance_bir_deadline_control`
- Genie Space not yet created (blocked on gold mart population)

### 2. Marketplace packaging not done

- No transactable marketplace offer published
- No repeatable customer install path
- No demo script or demo environment
- No implementation boundary document for SI partners
- First vertical bundle (Finance Control Tower) defined as target but not packaged

### 3. OData / MCP serving not live

- `ipai-odoo-mcp` (P0 gap): not yet built — business events from Odoo have no MCP exposure
- OData entity map authored in SSOT but not yet served as a running endpoint
- Pulser → Foundry → Odoo action loop not wired for customer-facing workflows

### 4. Compliance evidence incomplete

- Azure Policy deny rules not yet enforced for untagged resources
- Compliance evidence packs not assembled per Feature Ship-Readiness Checklist
- Module introspection docs (`MODULE_INTROSPECTION.md`) incomplete for several `ipai_*` modules
- ADO environment gates not yet wired to all Azure Pipelines

---

## Current conclusion

**Lifecycle position:** Reference architecture + accelerator proving, moving into industry solution packaging.

**Strongest layer:** Intelligence (Databricks + UC + Genie + dual inference) — this is the differentiator.

**Operational layer:** ERP core (Odoo CE + OCA) — live, confirmed HTTP 200, BIR modules partially built.

**Gap layer:** Packaging — no repeatable offer, no demo, no marketplace listing.

**What is NOT the bottleneck:** Platform infrastructure. The substrate is sound.

**What IS the bottleneck:** Gold mart population → Genie Space → first packaged vertical demo → marketplace listing.

---

## Recommended next milestone

**R1 Foundation exit (target 2026-05-14):** Reference architecture proven end-to-end with live data.

Four actions in order:

1. Fix `path=` conflict in DLT Gold tables → trigger first DLT run → populate `gold_finance_*` marts
2. Create Genie Space `Finance Operations` in Databricks portal → wire to `ipai_dev.gold.*`
3. Create Genie Space `Compliance & Tax` → wire to `gold_finance_bir_deadline_control`
4. Package finance workbook telemetry and current ADO telemetry into one packaged reference vertical bundle with contracts, marts, Genie surfaces, dashboards, and a Pulser interaction boundary

---

## Short answer for internal and external use

**Internal (architecture):**
> We are at Stage 4 of the Microsoft Cloud for Financial Services lifecycle — reference architecture proven with live operational telemetry — and beginning Stage 5 (industry solution packaging). The intelligence layer is live and working. The packaging layer is next.

**External (prospect / partner):**
> We make finance operations measurable before we automate them. Our architecture is validated with real Azure + Databricks infrastructure and live delivery telemetry. The first vertical product — Finance Operations Control Tower — is being packaged now.

**Commercial (proposals / SoWs):**
> The architecture is proven with real operational data — Azure DevOps delivery telemetry and finance workbook data — not synthetic demos. Databricks turns finance calendars, close steps, and approval chains into live operating intelligence. Pulser then acts on that intelligence inside Odoo.

---

## Decision checkpoint

### Continue doing

- Dual inference (Foundry gpt-4.1 + Databricks) — working, keep both paths
- `ipai_*` thin delta doctrine — no-custom default is holding; `ipai_auth_oidc` sunset proves it
- Azure Pipelines as sole CI/CD — enforced, not reverting
- UC federation (`odoo_erp` foreign catalog) for zero-copy reads — working, keep read-only
- Memory / SSOT system (this file, `lifecycle-maturity-matrix.md`, `d365-fo-parity-matrix.md`) — canonical and operational

### Avoid

- Do not build new `ipai_*` modules before checking CE 18 + OCA coverage
- Do not invest in marketplace listing polish before reference architecture is proven end-to-end (gold not populated = not proven)
- Do not pursue Foundry frontier model unblocking (715-123420) — Databricks model serving is the working path
- Do not treat SSOT docs as a substitute for running pipelines — the authored/enforced gap is the current risk
- Do not add GitHub Actions workflows — Azure Pipelines is sole CI/CD authority
- Do not conflate Pulser (action copilot) with Genie (understanding surface) — complementary roles, not competing

---

## Immediate next action

Fix DLT Gold path conflict → run pipeline → populate gold marts → create Genie Space → package finance workbook telemetry and current ADO telemetry into one packaged reference vertical bundle with contracts, marts, Genie surfaces, dashboards, and a Pulser interaction boundary.

---

### Odoo-only Azure codification

The Azure footprint for Odoo is codified as a small Bicep stack (`infra/azure/odoo/`) that adopts existing canonical resource names and enforces a single shared tag contract across all runtime resources. Scope is Odoo-only: ACA web/worker/cron, PostgreSQL reference, Key Vault reference, managed identity, Log Analytics. Databricks, AI, and shared platform resources are out of scope. SSOT: `ssot/azure/odoo-footprint.yaml`.

---

*Last updated: 2026-04-17*
