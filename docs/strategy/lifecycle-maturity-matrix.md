# IPAI Lifecycle Maturity Matrix

> **Locked:** 2026-04-17
> **Authority:** this file is the canonical lifecycle position statement for IPAI.
> **Microsoft alignment:** [Financial Services industry guidance](https://learn.microsoft.com/industry/financial-services/)
> **One-line position:** Reference architecture + accelerator-proving phase, transitioning toward industry solution packaging.

---

## Lifecycle position statement

We are currently in the **reference architecture and accelerator-proving phase**: our landing-zone and platform foundation are in place, we are validating the target architecture with live operational telemetry in Databricks and Odoo-adjacent workflows, and we are now moving into industry solution packaging for repeatable, marketplace-ready vertical offers.

---

## Maturity matrix

| # | Stage | Microsoft concept | Our evidence | Gaps | Next milestone |
|---|---|---|---|---|---|
| 1 | **Landing zone / platform foundation** | Platform resources + application resources separated for workload scaling | Azure runtime (ACA, PG, AFD, KV), Databricks workspace (Premium+UC), repo separation by plane, canonical SSOT, 8-component architecture locked | Old-sub resources not fully decommissioned; Odoo PG auth gap; Foundry frontier models blocked (715) | Complete sub consolidation; resolve PG auth; file MS support for 715 |
| 2 | **Policy / governance** | Compliance, transparency, policy initiatives | Naming standards, repo ownership, authority model, SSOT direction, tag taxonomy (8 core tags), tag validator CI, security policy, 3-tier defense doctrine | Production guardrails not enforced; marketplace packaging not started; compliance evidence packs incomplete | Enforce tag policy via Azure Policy deny; build evidence packs per feature-ship-readiness checklist |
| 3 | **Modernization / architecture shaping** | Cloud Adoption Framework alignment, modernization guides | Target operating model defined, Odoo vs Databricks roles split, Pulser vs Genie roles clear, canonical entities/marts/serving surfaces, 7-layer model stack, MCP topology | Architecture docs are authored but not all IaC-enforced; some SSOT is aspirational | Convert architecture docs to Bicep modules + DLT pipelines; close gap between doc and runtime |
| 4 | **Reference architecture proof** | Diagrams + descriptions for common workloads with real data | ✅ **Current center of gravity.** Live ADO telemetry in Databricks, real finance workbook data modeled (10 team members, 9 task categories, 6-level approval chain), dual inference paths (Foundry gpt-4.1 + Databricks Llama 4/405B/Qwen3), Databricks One dashboard live, 11 model serving endpoints confirmed working | Gold marts not populated from live pipeline; Genie Space not yet created (portal action); Odoo not serving /web/health | Run DLT pipeline → populate gold → create Genie Space → demo end-to-end |
| 5 | **Industry solution packaging** | Industry-specific capabilities on Microsoft Cloud, transactable offers | Pulser branding defined, ISV Success enrolled (MpnId 7097325), Partner Center verified, TBWA\SMP program templated | No marketplace offer published; no repeatable install path; no demo script; no implementation boundary doc; no vertical bundle structure | Define offer shape (Finance Control Tower + Pulser for Odoo + Compliance & Close); build demo path; publish first marketplace listing |
| 6 | **Case study / success story** | Customer deployment evidence, measurable outcomes | None — no customer deployment yet | No before/after metrics; no external reference | First customer deployment (TBWA\SMP target); measure and document outcomes |

---

## Asset-to-stage mapping

| Asset | Lifecycle stage |
|---|---|
| Azure / Databricks / Odoo platform work | 1 — Landing zone |
| Tag taxonomy + validator + security policy | 2 — Policy / governance |
| Canonical entities / marts / SSOT / 7-layer model | 3 — Architecture shaping |
| ADO live telemetry in Databricks | 4 — Reference architecture proof |
| Finance workbook telemetry → dims + facts + control tower | 4 — Vertical accelerator seed |
| Databricks model serving (Llama 4, 405B, Qwen3 confirmed) | 4 — Reference architecture proof |
| Tax Guru fine-tuning pipeline | 4 — Accelerator |
| Pulser behavior profiles + branding | 5 — Solution packaging prep |
| ISV Success / Partner Center enrollment | 5 — Go-to-market packaging |
| MCP topology (3-phase) | 3–4 — Architecture + accelerator |
| Databricks One + Genie strategy | 4–5 — Proof + packaging |

---

## What "done" looks like for Stage 5 (industry solution packaging)

Four deliverables to exit Stage 5:

### 1. Repeatable vertical offer definition

```
Finance Control Tower          — BIR compliance + close workload + bottleneck analytics
Pulser for Odoo               — AI operating copilot for CE 18 ERP
Compliance & Close Automation  — tax workflow + month-end close + approval chains
```

### 2. Reference implementation bundle

```
Source contracts  → data-intelligence/contracts/finance/*
Gold marts        → ipai_dev.gold.* (populated via DLT)
Genie Spaces      → Finance Operations + Compliance & Tax
Dashboards        → BIR Control Tower + Close Workload + Automation Candidates
Pulser actions    → guided close tasks + tax review + approval routing
```

### 3. Marketplace-facing offer shape

```
Transactable:    Pulser for Odoo (per-user/month or per-tenant)
Service-attached: Finance Control Tower implementation (consulting)
Managed:         Hosted Databricks + Odoo runtime (optional)
```

### 4. Demo + evidence pack

```
Live scenario:      TBWA\SMP month-end close → BIR filing readiness
Sample workflow:    Pulser walks through close checklist → Genie answers "what's at risk?"
Value articulation: "Finance ops measurable before automated"
Architecture diagram: 8-component canonical diagram with real resource names
```

---

## Timeline alignment

| Release | Date | Lifecycle milestone |
|---|---|---|
| R1 Foundation | 2026-04-14 → 2026-05-14 | Stage 4 complete (reference architecture proven with live data) |
| R2 Core Execution | 2026-05-15 → 2026-07-14 | Stage 5 started (first vertical offer defined + demo-ready) |
| R3 PH Ops Hardening | 2026-07-15 → 2026-10-14 | Stage 5 complete (marketplace listing live + first customer onboarding) |
| R4 GA | 2026-10-15 → 2026-12-15 | Stage 6 started (first customer success evidence) |

---

## What NOT to do at this stage

- Do not over-invest in marketplace listing polish before the reference architecture is proven end-to-end
- Do not skip Genie Space creation — it's the fastest visible proof of "Databricks understands the business"
- Do not treat docs/SSOT as a substitute for running code — the gap between "authored" and "enforced" is the current risk
- Do not conflate Pulser (action copilot) with Databricks (understanding surface) — they complement, not compete
- Do not wait for Foundry frontier models to unblock (715) — Databricks model serving is the working path now

---

## Commercial framing (use in proposals / SoWs)

> We make finance operations measurable before we automate them.

> Databricks turns finance calendars, close steps, and approval chains into live operating intelligence. Pulser then acts on that intelligence inside Odoo.

> The architecture is proven with real operational data — Azure DevOps delivery telemetry and finance workbook data — not synthetic demos.

---

*Last updated: 2026-04-17*
