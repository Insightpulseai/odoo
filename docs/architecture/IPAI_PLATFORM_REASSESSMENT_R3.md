# IPAI Platform Re-Assessment (R3)

> **Revision:** R3 (prior: R2 2026-04-05)
> **Date:** 2026-04-05 (same-day re-assessment after board and artifact review)
> **Trigger:** Cross-reference all Azure Boards backlogs, go-live checklists, spec bundles, and recent commits against R2 scores
> **Method:** Evidence-grounded review of internal assessment artifacts vs. Microsoft WAF pillar structure

---

## Executive Summary

**Overall Maturity: 2.7 → 2.7 / 5.0 (UNCHANGED)**

The R2 score remains accurate. The re-assessment confirms no score-changing work has shipped since R2. What has changed is **program governance maturity** — 5 org-wide spec bundles, a sprint operating model, work-item templates, and a multi-team scaling model are now in the repo. These improve delivery confidence but do not change WAF pillar scores until the planned work items are executed.

**Verdict: CONDITIONALLY READY (unchanged)**

---

## Board Status Reconciliation

### IPAI Platform Backlog (6 Epics, 26 Features, 62+ PBIs)

#### Epic 1: Governance & Drift Remediation

| Feature | Board Status | Actual Status | Delta |
|---|---|---|---|
| 1.1 Reconcile IaC with Live Azure State | Sprint 1, HARD BLOCKER | **NOT STARTED** — 20+ resources still untracked | None |
| 1.2 Enable Azure Cost Management | Sprint 1 | **NOT STARTED** — no budget, no export | None |
| 1.3 Archive Deprecated Infra Configs | Sprint 1 | **NOT STARTED** — DO/Supabase/Mailgun still in `infra/` | None |

**Board update needed:** None — status matches.

#### Epic 2: Production Readiness & Resilience

| Feature | Board Status | Actual Status | Delta |
|---|---|---|---|
| 2.1 Set PG Backup Retention in Bicep | Sprint 1 | **NOT STARTED** | None |
| 2.2 Deploy Staging Environment | Sprint 2, HARD BLOCKER | **NOT STARTED** — all workloads still `*-dev` | None |
| 2.3 Test Backup Restore | Sprint 2, HARD BLOCKER | **NOT STARTED** | None |
| 2.4 Consolidate Go-Live Checklist | Sprint 2 | **OVERDUE** — 4 checklists still exist | **Flag** |
| 2.5 Define Production SLOs | Sprint 2 | **NOT STARTED** | None |
| 2.6 Solo Operator Mitigation | Sprint 2 | **NOT STARTED** | None |

**Board update needed:** Feature 2.4 should be flagged — 4 checklists confirmed, consolidation not started. Also, go-live checklist still says "Odoo19" in filename (`ODOO19_GO_LIVE_CHECKLIST.md`) despite Odoo 18 baseline.

#### Epic 3: Security & Network Hardening

| Feature | Board Status | Actual Status | Delta |
|---|---|---|---|
| 3.1 Enable Entra CA + MFA | Sprint 1, HARD BLOCKER | **PARTIAL** — `admin@` enrolled, `emergency-admin@` pending | **Update** |
| 3.2 Activate Entra OIDC for Odoo | Sprint 2, HARD BLOCKER | **PARTIAL** — `ipai_auth_oidc` module exists, Google OAuth added, not activated | **Update** |
| 3.3 Formalize NSG Rules in Bicep | Sprint 1 | **NOT STARTED** | None |
| 3.4 Deploy Private Endpoints (PG + KV) | Sprint 2, HARD BLOCKER | **PARTIAL** — PG PE exists (DNS zone confirmed), KV still default-allow | **Update** |
| 3.5 Enable CodeQL via GitHub Actions | Sprint 1 | **NOT STARTED** | None |

**Board updates needed:**
- 3.1: Move to **IN PROGRESS** — `admin@` MFA enrolled (CP-1a evidence 2026-03-20), `emergency-admin@` still pending
- 3.2: Move to **IN PROGRESS** — OIDC module deployed, Google OAuth added (commit `0c0d6a75`), Entra redirect not activated
- 3.4: Move to **IN PROGRESS** — PG PE confirmed via `privatelink.postgres.database.azure.com` DNS zone in Resource Graph; KV PE still needed

#### Epic 4: Observability & Operations

| Feature | Board Status | Actual Status | Delta |
|---|---|---|---|
| 4.1 Verify Alert Routing | Sprint 1, HARD BLOCKER | **PARTIAL** — 4 alert rules + 2 action groups deployed; routing unverified | **Update** |
| 4.2 Operational Runbooks | Sprint 2 | **NOT STARTED** | None |

**Board update needed:** 4.1 move to **IN PROGRESS** — alert rules confirmed deployed via Resource Graph, but test alert not triggered, notification targets not validated.

#### Epic 5: AI Platform Readiness

| Feature | Board Status | Actual Status | Delta |
|---|---|---|---|
| 5.1 Seed Knowledge Base Index | Sprint 1 | **PARTIAL** — 331 docs indexed (target: 7,000+) | **Update** |
| 5.2 Integrate Eval Gate in CI/CD | Sprint 2 | **NOT STARTED** — pipeline placeholder only | None |
| 5.3 Migrate AI API Key to Key Vault | Sprint 2 | **NOT STARTED** — API key still in Odoo `ir.config_parameter` | None |
| 5.4 Add Prompt Injection Detection | Sprint 2 | **NOT STARTED** | None |

**Board update needed:** 5.1 move to **IN PROGRESS** — 331/7000 chunks indexed, Foundry agent operational (gpt-4.1), retrieval chain unwired.

#### Epic 6: Platform Productization & Scale

All 6 Features **DEFERRED** as expected. No update needed.

---

### Go-Live Acceleration Plan (CP-1 through CP-8)

| Gate | Board Status | Actual Status (Evidence 2026-03-20) | Delta |
|---|---|---|---|
| CP-1 MFA | BLOCKED | **PARTIAL** — admin@ enrolled, emergency-admin@ pending | **Update** |
| CP-2 Azure Files | PARTIAL | **DONE** — share exists, mount configured, persistence tested | **Close candidate** |
| CP-3 AFD + WAF | BLOCKED | **PARTIAL** — AFD live on `erp.insightpulseai.com` (x-azure-ref), WAF deployed (Resource Graph), portal verification pending | **Update** |
| CP-4 Cron fix | PARTIAL | **PARTIAL** — config set, image redeploy needed | None |
| CP-5 Pipeline | BLOCKED | **PARTIAL** — Azure DevOps pipeline baseline shipped (commit `d8f8a6aa67`), ADO access unblocked status unknown | **Update** |
| CP-6 Tenancy | NOT STARTED | **PARTIAL** — `dbfilter=^odoo$` configured, hostname routing needs image redeploy | **Update** |
| CP-7 Smoke test | NOT STARTED | **DONE** — 10/10 checks passed (evidence 2026-03-20) | **Close candidate** |
| CP-8 Evidence pack | NOT STARTED | **PARTIAL** — pack at `docs/delivery/evidence/poc-pack/20260320-1257/` | **Update** |

**Significant finding:** CP-2 and CP-7 appear closeable based on 2026-03-20 evidence. Board status is stale.

---

### Documentation Program Backlog (5 Epics, 35+ Features)

| Epic | Board Status | Actual Status | Delta |
|---|---|---|---|
| 1. Workload Documentation | Foundation | **PARTIAL** — README exists, overview stubs empty, workload-center empty | **Update** |
| 2. AI Platform Documentation | Wave-2 | **PARTIAL** — index pages exist (3), full content pages empty | **Update** |
| 3. Engineering Documentation | Wave-2 | **PARTIAL** — index pages exist with traceability model patched | **Update** |
| 4. Data Intelligence Documentation | Wave-2 | **PARTIAL** — index page exists, data-intelligence/docs/index.md exists | **Update** |
| 5. Governance & Drift Documentation | Hardening | **NOT STARTED** | None |

**Key finding:** Foundation iteration items are lagging. README and doc-authority exist, but 10 planned doc sections in `docs/odoo-on-azure/` are empty directories.

---

## WAF Pillar Re-Score

### A. Well-Architected Review: 2.7 → **2.7** (UNCHANGED)

| Pillar | R2 Score | R3 Score | Change | Rationale |
|---|---|---|---|---|
| Reliability | 1.8 | **1.8** | — | No DR test, no staging, no multi-region |
| Security | 2.6 | **2.7** | +0.1 | Google OAuth added (commit `0c0d6a75`), but MFA not enforced, OIDC not activated |
| Cost Optimization | 1.5 | **1.5** | — | No Azure Cost Management, no budgets |
| Operational Excellence | 3.0 | **3.1** | +0.1 | ADO pipeline baseline shipped (commit `d8f8a6aa`), 5 spec bundles + sprint model created |
| Performance Efficiency | 2.8 | **2.8** | — | No load testing, cross-region latency unmitigated |
| **WAF Subtotal** | **2.4** | **2.4** | — | Marginal gains insufficient to change aggregate |

### B-K: Other Lenses

| Lens | R2 | R3 | Change | Rationale |
|---|---|---|---|---|
| B. Landing Zone / CAF | 2.5 | **2.5** | — | No NSGs, no Azure Policy |
| C. Platform Engineering | 2.8 | **2.9** | +0.1 | 5 spec bundles + sprint model + scaling model improve governance |
| D. DevOps Capability | 3.2 | **3.3** | +0.1 | ADO pipeline baseline shipped |
| E. FinOps | 1.2 | **1.2** | — | No change |
| F. CASA (Security) | 2.3 | **2.3** | — | No MFA enforcement, no Defender |
| G. GenAI Technical | 2.5 | **2.5** | — | KB still at 331 docs, eval gate still placeholder |
| H. Go-Live WAF | 1.5 | **1.7** | +0.2 | CP-2 closeable, CP-7 smoke passed, pipeline baseline shipped |
| I. Developer Velocity | 2.8 | **2.8** | — | Deferred |
| J. Mission Critical WAF | 0.8 | **0.8** | — | Deferred |
| K. SaaS Journey | 2.0 | **2.0** | — | Deferred |

**Aggregate: 2.5 → 2.5 / 5.0** (lens-level weighted — note: headline 2.7 is the WAF-specific score)

---

## Hard Blocker Status

| # | Hard Blocker | R2 Status | R3 Status | Change |
|---|---|---|---|---|
| 1 | Reconcile live Azure resources into IaC | NOT STARTED | **NOT STARTED** | — |
| 2 | Prove restore/recovery posture | NOT STARTED | **NOT STARTED** | — |
| 3 | Confirm private connectivity boundaries | PARTIAL (PG PE) | **PARTIAL** (PG PE confirmed, KV still open) | — |
| 4 | Verify alert routing and operational ownership | PARTIAL (4 rules deployed) | **PARTIAL** (routing still unverified) | — |
| 5 | Close identity gaps (Entra OIDC + MFA) | PARTIAL (admin@ enrolled) | **PARTIAL** (Google OAuth added, Entra OIDC not activated) | Marginal |

**All 5 hard blockers remain open.** No hard blocker has been fully resolved since R2.

---

## What Has Improved Since R2

| Category | Improvement | Evidence |
|---|---|---|
| **Program governance** | 5 org-wide spec bundles created (constitution + prd + plan + tasks) | `spec/{5 bundles}/` |
| **Sprint model** | Sprint cadence, ceremonies, DoD published | `docs/planning/DOC_PROGRAM_SPRINT_MODEL.md` |
| **Work-item discipline** | Templates, naming, PR keyword conventions published | `docs/planning/DOC_PROGRAM_WORK_ITEM_TEMPLATES.md` |
| **Multi-team scaling** | 7-team model with area paths and delivery plans | `docs/planning/DOC_PROGRAM_SCALING.md` |
| **Engineering traceability** | Azure Boards + GitHub traceability model documented | Engineering index pages patched |
| **ADO pipeline** | Azure DevOps pipeline baseline for Odoo 18 shipped | Commit `d8f8a6aa67` |
| **Identity expansion** | Google Workspace OAuth provider added | Commit `0c0d6a75d8` |
| **Odoo 18 baseline** | All stale Odoo 19 references corrected across 10 files | 22+ individual edits |

---

## What Has NOT Improved Since R2

| Category | Status | Board Feature |
|---|---|---|
| **IaC drift** | 20+ resources still untracked in Bicep | Feature 1.1 |
| **Cost visibility** | No Azure Cost Management, no budgets | Feature 1.2 |
| **MFA enforcement** | emergency-admin@ still not enrolled | Feature 3.1 |
| **Entra OIDC activation** | Module exists but not activated for Odoo login | Feature 3.2 |
| **Alert routing validation** | 4 rules deployed, routing unverified | Feature 4.1 |
| **KB seeding** | 331/7000+ chunks | Feature 5.1 |
| **Backup restore proof** | Not tested | Feature 2.3 |
| **Staging deployment** | All workloads still `*-dev` | Feature 2.2 |
| **CodeQL** | Not enabled | Feature 3.5 |
| **NSG formalization** | Not in Bicep | Feature 3.3 |
| **SLO definition** | No targets defined | Feature 2.5 |

---

## Board Items Needing Status Updates

| Board Item | Current State | Should Be | Action |
|---|---|---|---|
| Feature 3.1 (MFA) | New | **Active** | admin@ enrolled; emergency-admin@ pending |
| Feature 3.2 (OIDC) | New | **Active** | Module deployed, Google OAuth added, Entra not activated |
| Feature 3.4 (Private Endpoints) | New | **Active** | PG PE confirmed; KV PE needed |
| Feature 4.1 (Alert Routing) | New | **Active** | 4 rules + 2 action groups deployed; routing unverified |
| Feature 5.1 (KB Seeding) | New | **Active** | 331 docs indexed; 7000+ target |
| CP-2 (Azure Files) | Partial | **Resolved** | Evidence exists 2026-03-20 |
| CP-5 (Pipeline) | Blocked | **Active** | ADO baseline shipped |
| CP-7 (Smoke Test) | Not Started | **Resolved** | 10/10 passed 2026-03-20 |
| Feature 2.4 (Go-Live Consolidation) | Sprint 2 | **Flagged** | 4 checklists still exist; `ODOO19_GO_LIVE_CHECKLIST.md` filename stale |

---

## Gap to Official Microsoft Assessment

The internal R2/R3 assessment was structured to approximate the Microsoft WAF lenses, but it was not conducted through the official Microsoft Assessments portal (`learn.microsoft.com/assessments/azure-architecture-review/`).

### What the official assessment would add

| Capability | Internal (current) | Official Microsoft |
|---|---|---|
| Scoring methodology | Custom 0-5 scale, self-calibrated | Normalized Microsoft scoring, comparable across customers |
| Recommendations | Hand-written roadmap | Auto-generated per-pillar guidance linked to Microsoft Learn |
| Benchmark comparability | Internal only | Comparable to other Azure customers |
| Exportable results | Markdown + YAML | CSV export + shareable results page |
| Credibility for stakeholders | Self-assessment | Microsoft-branded baseline |

### Recommended action

Run the official **Azure Well-Architected Review** at `learn.microsoft.com/assessments/azure-architecture-review/` using the internal R3 assessment as a **prep guide** to answer the questionnaire accurately. Then:

1. Export the CSV results
2. Save to `docs/evidence/<YYYYMMDD-HHMM>/waf-review/`
3. Cross-reference official scores against R3 internal scores
4. Update `IPAI_PLATFORM_ANALYSIS.md` with a reconciliation section
5. Create Azure Boards PBI under Feature 1.1 or new Feature for the official assessment

---

## Disposition

| Item | Decision |
|---|---|
| R2 aggregate score (2.7) | **Retained** — no score-changing work shipped |
| Hard blockers (5) | **All still open** — marginal progress on 3.1, 3.2, 3.4, 4.1, 5.1 |
| Board hygiene | **10 items need status updates** (listed above) |
| Program governance | **Significantly improved** — spec bundles, sprint model, templates, scaling model |
| Next action | Complete CP-1 (emergency-admin MFA) → validates Feature 3.1 → unblocks CP-3/CP-5 sequence |

---

*Assessment: R3 | Date: 2026-04-05 | Assessor: Claude Code (internal, evidence-grounded) | Source: R2 platform analysis + all Azure Boards backlogs + recent commits + go-live checklists*
