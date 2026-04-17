# <center>InsightPulseAI</center>
# <center>Pulser · Odoo on Azure Agentic ERP</center>

## <center>Platform Engineering Specification</center>
### <center>Version 0.6 · April 2026 · CONFIDENTIAL</center>

| Metadata | Value |
| :--- | :--- |
| **Product** | Pulser — Philippine SMB Agentic ERP |
| **Platform** | Odoo 18 CE on Azure Container Apps (SEA) |
| **ERP Domains** | Finance (R2R) · Project Operations (P2P) · Operations (S2P/O2C) |
| **Document type** | Unified Capability & Release Roadmap |
| **Owner** | Jake Tolentino — CTO, InsightPulseAI |
| **Status** | **Authoritative Roadmap (V0.6)** |

**Current state**: Azure-native dev/staging substrate established for Pulser/Odoo, including Odoo runtime, PostgreSQL, Databricks, storage, identities, and observability. Functional finance/project-operations parity, production release posture, and go-live readiness remain in progress. See [MATURITY_VS_D365_TAXONOMY](../docs/reports/MATURITY_VS_D365_TAXONOMY.md) for benchmark mapping.

---

# Roadmap — Unified Capability Target

This document provides the single, consolidated view of Pulser's functional targets across the Finance (R2R) and Project (P2P) domains. It aligns technical capability rollout with the [Microsoft Practice Build](file:///Users/tbwa/Documents/GitHub/Insightpulseai/spec/microsoft-practice-build/prd.md) 12-month phases.

## 1. Capability Taxonomy Mapping

Pulser capabilities are mapped by **Type**, **Domain**, and **Release Phase**.

| Capability | Type | Domain | Phase | Authority |
|:---|:---:|:---:|:---:|:---|
| **BIR 2307 Automation** | Tax | Finance | Phase 1 | [R2R PRD](file:///Users/tbwa/Documents/GitHub/Insightpulseai/spec/pulser-record-to-report/prd.md) |
| **Odoo View Deep-links** | Nav | Both | Phase 1 | [Umbrella PRD](file:///Users/tbwa/Documents/GitHub/Insightpulseai/spec/pulser-odoo/prd.md) |
| **AP Match/Recon** | Inf | Finance | Phase 2 | [R2R PRD](file:///Users/tbwa/Documents/GitHub/Insightpulseai/spec/pulser-record-to-report/prd.md) |
| **Billing Readiness Sig** | Nav | Project | Phase 2 | [P2P PRD](file:///Users/tbwa/Documents/GitHub/Insightpulseai/spec/pulser-project-to-profit/prd.md) |
| **SOW/Contract Parsing** | Inf | Project | Phase 2 | [P2P PRD](file:///Users/tbwa/Documents/GitHub/Insightpulseai/spec/pulser-project-to-profit/prd.md) |
| **Autonomous AP Posting**| Tax | Finance | Phase 3 | [R2R PRD](file:///Users/tbwa/Documents/GitHub/Insightpulseai/spec/pulser-record-to-report/prd.md) |
| **Autonomous Close** | Tax | Finance | Phase 3 | [R2R PRD](file:///Users/tbwa/Documents/GitHub/Insightpulseai/spec/pulser-record-to-report/prd.md) |
| **Cash Forecasting** | Inf | Finance | Phase 3 | [R2R PRD](file:///Users/tbwa/Documents/GitHub/Insightpulseai/spec/pulser-record-to-report/prd.md) |
| **Predictive Margin** | Inf | Project | Phase 3 | [P2P PRD](file:///Users/tbwa/Documents/GitHub/Insightpulseai/spec/pulser-project-to-profit/prd.md) |
| **Portfolio Health AI** | Inf | Project | Phase 3 | [P2P PRD](file:///Users/tbwa/Documents/GitHub/Insightpulseai/spec/pulser-project-to-profit/prd.md) |

> [!NOTE]
> **Type Key**: **Inf** (Informational), **Nav** (Navigational), **Tax** (Transactional). Transactional is the highest trust/risk class.

---

## 2. Azure Boards Mapping (Current Wave Rule)

For the current development wave, all capability work must be parented by exactly one of the **3 Canonical Epics**:
1. **Epic: D365 Finance Parity** — Covers BIR, AP/AR, GL, and core financial foundations.
2. **Epic: Finance Agents Parity** — Covers Plane B assistive agents, reconciliation agent, and collections bot.
3. **Epic: D365 Project Operations Parity** — Covers P2P, WBS, resource management, and margin intelligence.

Hierarchy is and **Epic → Issue → Task** (Basic process). No "Feature" layer is used for this wave.

---

## 3. Release Roadmap (12 Months)

### Phase 1: Seed / MVP (Months 1-3)
**Theme**: *Substrate & Agent Baseline*
- **Objective**: Establish the Azure-native dev/staging substrate & foundational Agent plane.
- **Key Targets**:
    - **Platform**: Odoo 18 Direct Ingress + Azure substrate established (PostgreSQL, identities, logs).
    - **Agent Plane**: Microsoft Foundry integration + M365 Specialist baseline (PFP, FCP, etc.).
    - **Finance (Hydration)**: Initial BIR 2307 assistance & evidence capture foundation.
- **Evidence Gate**: Platform readiness & Agent connectivity verified.

### Phase 2: Scale / Automated Ops (Months 4-8)
**Theme**: *Efficiency & Compliance Gating*
- **Objective**: Reduce operational friction with automated "Fail-Closed" suggestions.
- **Key Targets**:
    - **Finance**: AP Invoice Matching, Bank Rec Automation (80% target), BIR filing/payment assist (TX-01).
    - **Project**: Forecast vs. Budget Variance, Automated Billing-readiness signals.
    - **Platform**: Capability Package promoting (Preview → Prod), Runtime Safety Middleware.
- **Evidence Gate**: Structured TRN/Reference IDs, Artifact Evidence Packs.

### Phase 3: Mature / Agentic ERP (Months 9-12)
**Theme**: *Predictive Intelligence & Autonomy*
- **Objective**: Strategic transformation via autonomous reconciliation and predictive margin analysis.
- **Key Targets**:
    - **Finance**: Autonomous Month-end Close, Continuous Audit Trail, predictive cash flow.
    - **Project**: Portfolio Sentiment/Health, predictive margin risk, Autonomous Project Setup.
    - **Platform**: Multi-agent orchestration (Planner/Specialists), A2A Interoperability.
- **Evidence Gate**: Immutable Append-only Audit Vault, Multi-entity Consolidation Evidence.

---

## 3. Roadblock & Risks

| Risk | Mitigation |
|:---|:---|
| **Functional Drift** | Enforce [Domain Authority Table](file:///Users/tbwa/Documents/GitHub/Insightpulseai/spec/pulser-odoo/constitution.md) strictly during PR reviews. |
| **Evidence Gaps** | No "Transactional" capability promotion without evidence-linked audit trail. |
| **Market B Drift** | Review BIR compliance requirements quarterly against current issuances. |

---
*Last updated: 2026-04-13*
