# Azure Boards Normalization Matrix — `insightpulseai/ipai-platform`

> **Purpose.** Reconcile the 5 backlog packs (`epic-01` through `epic-05`) against the **23 existing epics** already in Azure Boards. Boards are populated, not empty — the next move is **consolidation**, not duplication.
>
> **Audit snapshot:** 2026-04-14. 23 Epics, 120+ Issues, 250+ Tasks, 5 Iterations.
> **Active iteration:** `R1-Foundation-30d` (2026-04-14 → 2026-05-14).
> **Stale:** project description still says "Odoo CE 19 + Azure infra" — should be Odoo 18 per CLAUDE.md.

---

## Rule

**Do NOT create new epics.** Map the 5 backlog packs onto existing epics. New epic creation only where no suitable parent exists.

## Doctrine plane legend

- **T** = Transaction (Odoo+OCA)
- **D** = Data intelligence (Databricks+Fabric)
- **A** = Agent (Foundry+MAF)
- **L** = Delivery (GitHub+Azure)
- **G** = Governance / cross-cutting (Security, Schema, Tenancy)

---

## Existing epics vs doctrine + backlog packs

| ID | Existing Epic Title | State | Plane | Matches my pack | Action | Target iteration |
|---|---|---|---|---|---|---|
| **1** | [OBJ-001] Identity Baseline & Platform Foundation | Doing | G | epic-02 Feature 1 (arch) + epic-03 Feature 1 (PG arch) | **Keep** — slot features from epic-02/03 here | R1 (active) |
| **2** | [OBJ-002] ERP Enterprise Parity (CE + OCA + ipai_*) | Doing | T | epic-02 Feature 3 (AOT-equiv) | **Keep** — primary container for parity_matrix.yaml work | R2 |
| **3** | [OBJ-003] Foundry Agent Runtime & Copilot | Doing | A | Finance agent Pulser sub-agents (parity_matrix Plane B) | **Keep** — primary container for Pulser agents | R2 |
| **4** | [OBJ-004] Data Intelligence & OLTP/OLAP Separation | To Do | D | **epic-03 Azure PostgreSQL Foundation** (all 6 features) | **Keep** — slot epic-03 features directly | R1 |
| **5** | [OBJ-005] Developer Experience & Automation Consolidation | To Do | L | epic-02 Feature 2 (dev tools) + epic-05 (admin tooling + UI test) + epic-04 partial | **Keep** — slot epic-02 F2 + epic-05 + some epic-04 | R1–R2 |
| **6** | [OBJ-006] Security, Compliance & BIR | To Do | G | epic-02 Feature 7 (security/perf) + BIR work | **Keep** | R2 |
| **7** | [OBJ-007] Revenue-Ready Product Portfolio | Doing | G | #480 EPIC-PH-11 Solution Kit | **Keep** — product packaging home | R3 |
| **63** | Execute Odoo 18 Go-Live Critical Path | Doing | T/L | **epic-01 Migration/UAT/Go-Live** (all 5 features) | **Keep** — slot epic-01 features directly | R1 |
| **106** | Schema Governance | Doing | G | Tenancy SSOT + parity matrix | **Keep** | R1 |
| **238** | Odoo on Azure Operating Model | To Do | T | Tenancy + runtime overlaps #1/#63 | **MERGE into #1** | — |
| **239** | AI Platform Operating Model | To Do | A | Overlaps #3 | **MERGE into #3** | — |
| **240** | AI-Led Engineering Model | To Do | L | epic-04 Azure Pipelines + GitHub partial | **RENAME → "Delivery Plane — AI-Led SDLC"** + slot epic-04 partial | R2 |
| **241** | Data Intelligence Operating Model | To Do | D | Overlaps #4 | **MERGE into #4** | — |
| **242** | Governance Drift Closure | To Do | G | Overlaps #106 + Deprecated-stack cleanup | **Keep** — includes Superset/DO/nginx drift guard work | R1 |
| **243** | Azure Assessment Harness | To Do | G | Overlaps #106 + Well-Architected reviews from PRD §0.3 | **RENAME → "Well-Architected Assessment Harness"** | R2 |
| **244** | Odoo SDK | To Do | T | Overlaps #2; `addons/ipai/_template/` already lands here | **Keep** — home for module template + introspection contract | R1 |
| **341** | Production Agent Runtime Hardening | To Do (deferred) | A | Overlaps #3 | **Keep deferred** — post-R1 | R3 |
| **358** | Financial Reports Intelligence | To Do | D/A | Fabric + Power BI semantic model (parity_matrix Finance.Reporting) | **Keep** | R2 |
| **480** | EPIC-PH-11 — Solution Kit packaging and enablement | To Do | G | Partner-ready packaging per PRD + `reference_partner_center_*` | **Keep** | R3 |
| **502** | Hardening — operational trust and security recovery | To Do | G | Overlaps #1 + #6 + deprecated-stack cleanup | **Keep** — Superset/DO/nginx removal goes here | R1 |
| **503** | Proving — measurable runtime, platform, and AI evidence | To Do | G | Overlaps #243 (Well-Architected) | **Keep** — pairs with #243 | R2 |
| **504** | Codifying — convert manual proof into enforced controls | To Do | G | Release gates, policy enforcement | **Keep** — gating belongs here | R3 |
| **521** | **Pulser for Odoo — GitHub + Azure Pipelines Delivery Governance** | To Do | L | **epic-04 Azure Pipelines + GitHub** (direct title match) | **Keep** — slot all 21 epic-04 stories | R2 |

---

## 5 pack → epic routing (detail)

### epic-01 Migration/UAT/Go-Live → **#63 Execute Odoo 18 Go-Live Critical Path**
- Feature 1 Migration Strategy → Features 1.1-1.4 under #63
- Feature 2 Data Management Framework → Features 2.1-2.4 under #63
- Feature 3 UAT + Automation → Features 3.1-3.4 under #63 (also touches #5 for tooling)
- Feature 4 Go-Live/Cutover/Rollback → Features 4.1-4.4 under #63
- Feature 5 Benchmark + Agent Governance → split: 5.1 under #63, 5.2 under **#3** (agent-aware go-live)

### epic-02 Architecture/Dev/Hardening → **split across #1, #2, #5, #6, #244**
- F1 Plan Architecture → **#1** (platform foundation)
- F2 Apply Developer Tools → **#5** (DevEx)
- F3 AOT-Equivalent Elements → **#244** (Odoo SDK) — this IS the SDK work
- F4 Develop and Test Code → **#5**
- F5 Reporting → **#358** (Financial Reports Intelligence) + **#4** (data)
- F6 Integrate and Manage Data → **#4**
- F7 Security + Performance → **#6**
- F8 Benchmark and Readiness → **#243** (Assessment Harness) or new Feature under #106

### epic-03 Azure PostgreSQL → **#4 Data Intelligence & OLTP/OLAP Separation**
- All 6 features slot as Features 1-6 under #4. OLTP plane = Azure PG; analytics plane = Databricks/Fabric. The epic already owns both.

### epic-04 Azure Pipelines + GitHub → **#521 (direct title match)**
- All 7 features slot as Features 1-7 under #521
- Partial overlap with **#240** (AI-Led Engineering Model, after rename) for story 2.3 AI-assisted workflows

### epic-05 Admin Tooling + UI Test → **#5 Developer Experience & Automation Consolidation**
- All 3 features slot as Features under #5
- Feature 2 UI Test Automation also links to #63 Feature 3 (UAT)

---

## Net epic actions

| Action | Count | Epics |
|---|---|---|
| **Keep** | 17 | #1, #2, #3, #4, #5, #6, #7, #63, #106, #242, #244, #341, #358, #480, #502, #503, #504, #521 |
| **Rename** | 2 | #240 → "Delivery Plane — AI-Led SDLC"; #243 → "Well-Architected Assessment Harness" |
| **Merge/retire** | 3 | #238 → #1; #239 → #3; #241 → #4 |
| **Create new** | 0 | — |

## Critical-path before any Boards population work

1. **Update project description** — ADO project metadata still says "Odoo CE 19 + Azure infra". Must be "Odoo CE 18 + Azure infra" per CLAUDE.md (can't update via available MCP tools — needs `az devops project update` or portal).
2. **Update memory** — `project_azdo_project_state.md` says boards are empty; actually 23 epics + 400+ work items. Memory drift to correct.
3. **Merge #738 first** — doctrine PR lands `ssot/benchmarks/parity_matrix.yaml` which this matrix references. Then #739 cleanup → #502 Hardening epic alignment.
4. **Assign owners** — "Assigned to me" query returns empty. Ownership not consistently set on existing work items.

## R1-Foundation-30d (active iteration) priority picks

Given R1 runs **2026-04-14 → 2026-05-14** (started TODAY), these should be the R1 landing targets:

- **#1** Identity Baseline + tenancy SSOT onboarding smoke test
- **#4** OLTP/OLAP extract pipeline scaffold (epic-03 Features 1-3)
- **#5** Module scaffold template enforcement + CI gates (epic-02 F2)
- **#63** Migration strategy + canonical entity inventory (epic-01 F1)
- **#106** Parity matrix publication + drift-guard test activation
- **#242** Deprecated-stack removal (Superset+DO+nginx) — PR #739 lands here
- **#244** Odoo SDK — `addons/ipai/_template/` + MODULE_INTROSPECTION enforcement
- **#502** Security/identity recovery baseline

## Template for per-epic Feature decomposition

When populating Features under existing Epics, use this structure (Azure Boards-native):

```
Epic: #NNN [Existing title]
  Feature: [Pack name — e.g., "Epic-01 F1: Migration Strategy and Data Readiness"]
    Description: one-paragraph scope + cross-link to docs/backlog/epic-NN-*.md
    Story: [Story 1.1 title]
      Description: from pack
      Acceptance: from pack
      Tags: per pack + `pulser-odoo`
      Iteration: R1/R2/R3/R4 per P0/P1/P2
```

## Changelog

- **2026-04-14** — Initial matrix. 23 epics audited. 5 packs mapped. 3 merges + 2 renames + 0 new epics.
