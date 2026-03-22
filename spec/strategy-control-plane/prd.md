# PRD — Strategy Control Plane

## Status

Draft

## Document Info

| Field | Value |
|-------|-------|
| Spec bundle | `spec/strategy-control-plane/` |
| Constitution | `constitution.md` |
| Owner | Platform team |
| Stakeholders | CEO, Strategy owners, PMO, Engineering, Finance |
| Created | 2026-03-23 |

---

## 1. Overview

Strategy Control Plane is the system that connects strategic intent to execution evidence across the InsightPulse AI platform. It replaces the retired Microsoft Viva Goals and fills the gap between high-level strategy documents and the operational systems that execute against them.

The product is not a dashboard. It is a strategy-to-runtime traceability engine with a review-first UX, evidence-backed progress computation, and an agent layer for narrative drafting and risk summarization.

---

## 2. Problem Statement

Today, strategic alignment is maintained through a combination of spreadsheets, slide decks, Notion pages, and ad-hoc status meetings. This creates several systemic problems:

1. **No single graph connects strategy to execution.** Objectives live in documents, work items live in Azure Boards, code lives in GitHub, deployments live in Azure, metrics live in Databricks. There is no traversable link between them.

2. **Progress is self-reported.** Team leads manually update percentage-complete fields in review meetings. These numbers are optimistic, inconsistent, and stale by the time they are reviewed.

3. **Review preparation is manual and expensive.** PMO spends 2-3 days before each monthly business review assembling status from multiple systems into a slide deck. The deck is outdated before it is presented.

4. **Strategic drift is invisible.** When execution diverges from strategic intent, the divergence is only discovered during quarterly reviews — too late to course-correct.

5. **No institutional memory.** Past decisions, rationale, and context are trapped in meeting notes. New team members cannot reconstruct why a goal was set, modified, or abandoned.

6. **Agent integration is ad-hoc.** AI agents that could assist with summarization, forecasting, and corrective proposals have no structured access to strategic context.

---

## 3. Goals

| # | Goal | Measure |
|---|------|---------|
| G1 | Establish a single strategic hierarchy from themes to work items | All active objectives traceable to at least one work-item source within 30 days of launch |
| G2 | Replace self-reported progress with evidence-derived confidence scores | >= 70% of KR progress derived from connected systems by Phase 2 completion |
| G3 | Automate review packet generation for monthly business reviews | MBR packet generation time reduced from 2-3 days to < 2 hours |
| G4 | Surface strategic drift within one review cycle (monthly) | Drift alerts generated for any objective with > 15% deviation from forecast |
| G5 | Provide agents with structured strategic context for narrative and proposal generation | Agent-generated review narratives available for all objectives with sufficient evidence |
| G6 | Maintain full audit trail of strategic decisions and status changes | Every status mutation, approval, and narrative revision traceable to actor and timestamp |

---

## 4. Non-Goals

| # | Non-Goal | Rationale |
|---|----------|-----------|
| NG1 | Replace Azure Boards, GitHub, Databricks, or Odoo | Constitution principle 2: open system boundaries. We integrate, not replace. |
| NG2 | Build a general-purpose BI tool or dashboard builder | The product is review-first, not visualization-first. Power BI handles BI. |
| NG3 | Provide HR engagement, pulse surveys, or employee experience features | Out of scope per constitution. This is strategy execution, not people analytics. |
| NG4 | Allow agents to autonomously change executive-visible status | Constitution principle 4: human approval over autonomous truth mutation. |
| NG5 | Support arbitrary goal framework semantics beyond OKR/KPI/initiative/milestone | The hybrid model is intentionally bounded. We do not build a meta-framework engine. |
| NG6 | Enforce a single planning cadence (quarterly, monthly, etc.) | Organizations operate on mixed cadences. The system must accommodate, not prescribe. |

---

## 5. Users

### 5.1 Primary Users

| Role | Description | Key need |
|------|-------------|----------|
| CEO / Executive sponsor | Sets strategic themes and reviews progress at MBR/QBR | Confidence that reported progress reflects reality |
| Strategy owner | Owns one or more objectives and their KR/KPI decomposition | Single view of objective health with drill-down to evidence |
| PMO / Chief of Staff | Prepares review packets, tracks cross-cutting risks, manages cadence | Automated packet generation, exception surfacing |
| Engineering manager | Owns delivery of initiatives linked to strategic objectives | Clear line-of-sight from their team's work to strategic impact |
| Product manager | Defines and prioritizes initiatives, manages scope trade-offs | Initiative-to-objective linkage, progress visibility |
| Finance lead | Tracks budget alignment, cost-to-complete, and ROI evidence | Financial evidence integrated into strategic progress |

### 5.2 Secondary Users

| Role | Description | Key need |
|------|-------------|----------|
| Team lead | Contributes check-ins and narrative context | Low-friction check-in experience, no duplicate data entry |
| Data analyst | Builds and validates evidence computation logic | Transparent derivation methods, debuggable confidence scores |
| Solution architect | Reviews technical alignment of initiatives to platform strategy | Architecture decision traceability |
| Platform operator | Monitors runtime health evidence feeding into KPIs | Operational metrics flowing into strategic context |
| AI agent | Consumes strategic graph for narrative generation and risk analysis | Structured, versioned, API-accessible strategic data |

---

## 6. Jobs to Be Done

### 6.1 CEO

> "When I walk into the monthly review, I want to know which objectives are truly on track versus which ones are being optimistically reported. I need confidence backed by evidence, not slides."

### 6.2 Strategy Owner

> "I own three objectives across two themes. I need one place where I can see the health of each, drill into the evidence, and write my narrative update without assembling data from five systems."

### 6.3 PMO / Chief of Staff

> "Every month I spend two days pulling data from Boards, GitHub, and Databricks into a deck. By the time it is presented, half the numbers are stale. I need the review packet to generate itself."

### 6.4 Engineering Manager

> "My team ships features and closes work items, but I cannot show how our work connects to the company's strategic objectives. I need that linkage to be automatic and visible."

### 6.5 Product Manager

> "I prioritize initiatives based on strategic alignment, but the alignment is informal. I need a system where I can link an initiative to an objective and track whether the initiative is actually moving the needle."

---

## 7. Product Principles

| # | Principle | Implication |
|---|-----------|-------------|
| P1 | Evidence over self-report | Default to system-derived progress. Manual entry is the fallback, not the primary input. |
| P2 | Review-first UX | The primary interaction is preparing for and conducting a review, not browsing dashboards. |
| P3 | Open integration model | Adapters connect to source systems. No single-vendor lock-in. New adapters can be added without core changes. |
| P4 | Hybrid outcome model | OKRs, KPIs, initiatives, and milestones coexist in one graph. The system does not force a single framework. |
| P5 | Human-in-the-loop governance | Agents propose; humans approve. No autonomous mutation of executive-visible state. |
| P6 | Machine-readable by default | Every object, relationship, and evidence link is API-accessible. The UI is one consumer, not the only consumer. |
| P7 | Incremental value delivery | Each phase delivers usable capability. The system is useful from Phase 1 (manual check-ins) and grows more automated over time. |

---

## 8. Solution Overview

The Strategy Control Plane consists of five layers, each building on the one below it.

### 8.1 Layer 1 — Strategic Model

The data model that represents the strategic hierarchy and relationships.

- **Themes**: Top-level strategic pillars (e.g., "Platform Maturity", "Revenue Growth")
- **Objectives**: Time-bound goals within a theme (e.g., "Achieve 80% EE parity by Q2")
- **Key Results (KRs)**: Measurable outcomes that indicate objective progress (quantitative, with target/actual)
- **KPIs**: Standing metrics that are monitored continuously (not time-bound like KRs)
- **Initiatives**: Scoped bodies of work that drive KR/KPI progress (linked to work items)
- **Milestones**: Binary gates within initiatives (done/not-done)

Relationships: Theme 1:N Objective 1:N KR|KPI. Initiative N:M KR|KPI. Initiative 1:N Milestone. Initiative 1:N WorkItem (via adapter).

### 8.2 Layer 2 — Execution Graph

The linkage between strategic objects and source-system artifacts.

- Work items (Azure Boards) linked to initiatives
- Repositories and PRs (GitHub) linked to initiatives
- Deployments and releases linked to milestones
- Runtime telemetry (App Insights, Databricks) linked to KPIs
- Financial records (Odoo) linked to budget KPIs
- Analytics outputs (Databricks, Power BI) linked to KRs

### 8.3 Layer 3 — Evidence Engine

The computation layer that derives progress confidence from connected systems.

- **Confidence score**: 0.0 to 1.0 per KR/KPI, computed from evidence freshness, completeness, and derivation method
- **Derivation methods**: work-item completion ratio, metric threshold attainment, milestone gate status, manual override with decay
- **Freshness tracking**: Evidence older than the review cadence is flagged as stale
- **Conflict detection**: When system-derived and manual-reported values diverge, surface the discrepancy

### 8.4 Layer 4 — Review Engine

The generation layer that produces review artifacts from the evidence engine.

- **MBR packet**: Monthly business review document with objective status, KR progress, exceptions, and narratives
- **Exception view**: Objectives or KRs with confidence below threshold, stale evidence, or forecast drift
- **Forecast/drift**: Projected completion based on current velocity versus plan
- **Comparison view**: Period-over-period progress with delta highlighting

### 8.5 Layer 5 — Agent Layer

AI agents that consume the strategic graph and evidence engine to produce drafts and proposals.

- **Narrative drafter**: Generates objective status narratives from evidence for human review
- **Risk summarizer**: Identifies cross-cutting risks from exception patterns
- **Corrective proposal generator**: Suggests re-scoping, re-prioritization, or escalation based on drift
- **Goal hygiene agent**: Flags objectives with no linked initiatives, KRs with no evidence sources, stale items

All agent outputs are proposals. They enter the system as drafts requiring human approval before becoming visible in review packets.

---

## 9. Functional Requirements

### 9.1 Strategic Hierarchy Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Create, read, update, archive themes | P0 |
| FR-1.2 | Create, read, update, archive objectives within themes | P0 |
| FR-1.3 | Create, read, update, archive KRs within objectives | P0 |
| FR-1.4 | Create, read, update, archive KPIs within objectives | P0 |
| FR-1.5 | Create, read, update, archive initiatives linked to KRs/KPIs | P0 |
| FR-1.6 | Create, read, update, archive milestones within initiatives | P0 |
| FR-1.7 | Define ownership (person or team) for every strategic object | P0 |
| FR-1.8 | Support time-bound periods (quarters, halves, custom) for objectives and KRs | P0 |
| FR-1.9 | Visualize the full hierarchy as a navigable tree or graph | P1 |

### 9.2 Hybrid Outcome Model

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | KRs have: description, metric type, start value, target value, current value, unit, cadence | P0 |
| FR-2.2 | KPIs have: description, metric type, threshold (red/yellow/green), current value, unit, cadence | P0 |
| FR-2.3 | Initiatives have: description, status (planned/active/completed/cancelled), owner, linked KRs/KPIs | P0 |
| FR-2.4 | Milestones have: description, target date, actual date, status (pending/done/missed) | P0 |
| FR-2.5 | Support N:M relationship between initiatives and KRs/KPIs (one initiative can drive multiple KRs) | P0 |
| FR-2.6 | Support weighting of KR contribution to objective progress | P1 |

### 9.3 Evidence-Backed Progress

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Compute KR progress from linked evidence sources (work-item completion, metric values, milestone gates) | P0 |
| FR-3.2 | Assign confidence score (0.0-1.0) to each KR based on evidence quality | P0 |
| FR-3.3 | Track evidence freshness and flag stale evidence (older than review cadence) | P0 |
| FR-3.4 | Support multiple derivation methods per KR (e.g., 60% from work-item completion + 40% from metric) | P1 |
| FR-3.5 | Detect and surface conflicts between system-derived and manually-reported progress | P1 |
| FR-3.6 | Roll up KR confidence to objective-level confidence (weighted average) | P0 |

### 9.4 Check-ins and Narratives

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Manual check-in: owner submits narrative text + optional metric update for a KR or objective | P0 |
| FR-4.2 | Check-in cadence enforcement: remind owners when a check-in is overdue | P1 |
| FR-4.3 | Check-in history: full timeline of all check-ins for any strategic object | P0 |
| FR-4.4 | Support structured check-in fields: status (on-track/at-risk/off-track), blocker description, help needed | P0 |
| FR-4.5 | Agent-drafted check-ins: agent proposes narrative from evidence, owner reviews and submits | P2 |

### 9.5 Portfolio Reviews

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Generate MBR packet: objective status summary, KR progress table, exception list, narratives | P0 |
| FR-5.2 | Exception view: filter to objectives/KRs below confidence threshold or with stale evidence | P0 |
| FR-5.3 | Forecast view: projected KR completion based on current trajectory | P1 |
| FR-5.4 | Drift view: delta between planned and actual progress with trend | P1 |
| FR-5.5 | Period comparison: side-by-side view of current vs. previous review period | P1 |
| FR-5.6 | Export review packet to PDF, Markdown, or structured JSON | P0 |

### 9.6 Initiative Linkage

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1 | Link initiative to one or more Azure Boards work items (epics, features, stories) | P0 |
| FR-6.2 | Link initiative to one or more GitHub repositories | P1 |
| FR-6.3 | Link initiative to spec bundles (`spec/<slug>/`) | P1 |
| FR-6.4 | Derive initiative progress from linked work-item completion percentage | P0 |
| FR-6.5 | Surface unlinked initiatives (initiatives with no work-item or evidence source) | P1 |
| FR-6.6 | Surface orphan work items (high-effort items not linked to any initiative) | P2 |

### 9.7 Open Integration Model

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-7.1 | Adapter interface: standard contract for connecting a source system to the evidence engine | P0 |
| FR-7.2 | Azure Boards adapter: sync work items, states, completion percentages | P0 |
| FR-7.3 | GitHub adapter: sync repositories, PRs, releases, deployment status | P1 |
| FR-7.4 | Databricks adapter: query metrics tables for KPI/KR evidence | P1 |
| FR-7.5 | Odoo adapter: query financial records for budget KPIs | P2 |
| FR-7.6 | Telemetry adapter: query Application Insights for runtime KPIs | P2 |
| FR-7.7 | Manual adapter: structured form for evidence not available from any connected system | P0 |
| FR-7.8 | Adapter health dashboard: show last sync time, error count, record count per adapter | P1 |

### 9.8 Governance and Audit

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8.1 | RBAC: define roles (viewer, contributor, owner, admin) with scoped permissions | P0 |
| FR-8.2 | Audit trail: every create, update, delete, status change, approval logged with actor and timestamp | P0 |
| FR-8.3 | Locked snapshots: freeze a review period so historical data cannot be retroactively modified | P1 |
| FR-8.4 | Approval workflows: status changes on objectives require owner or admin approval | P1 |
| FR-8.5 | Change history diff: show what changed between two snapshots of any strategic object | P2 |

### 9.9 Agent-Safe Operation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-9.1 | Agent actions are logged with agent identity (not attributed to a human) | P0 |
| FR-9.2 | Agent outputs enter as drafts; they are not visible in review packets until human-approved | P0 |
| FR-9.3 | Agent access is scoped: read strategic graph, read evidence, write drafts. No direct status mutation. | P0 |
| FR-9.4 | Agent rate limiting: maximum operations per minute per agent identity | P1 |
| FR-9.5 | Agent output versioning: every agent draft is versioned, previous versions retained | P1 |

### 9.10 Knowledge and Guidance

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-10.1 | Goal-setting guidance: surface best practices when creating objectives or KRs | P2 |
| FR-10.2 | Historical context: show past objectives in the same theme for reference | P1 |
| FR-10.3 | Decision log: record rationale for goal changes, re-scoping, or cancellation | P1 |
| FR-10.4 | Glossary: define terms (OKR, KPI, KR, initiative, etc.) accessible in-context | P2 |

---

## 10. Non-Functional Requirements

### 10.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1.1 | Strategic hierarchy load (full tree for one theme) | < 2 seconds |
| NFR-1.2 | Evidence computation for one objective (all KRs) | < 5 seconds |
| NFR-1.3 | MBR packet generation (all objectives) | < 60 seconds |
| NFR-1.4 | Adapter sync latency (time from source change to evidence update) | < 15 minutes |

### 10.2 Scalability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-2.1 | Support up to 50 themes, 500 objectives, 5000 KRs/KPIs | Phase 3 |
| NFR-2.2 | Support up to 20 concurrent review sessions | Phase 2 |
| NFR-2.3 | Evidence store: retain 24 months of historical evidence | Phase 3 |

### 10.3 Reliability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-3.1 | Adapter failure must not block manual check-ins or review generation | Always |
| NFR-3.2 | Evidence computation must be idempotent (re-running produces same result) | Always |
| NFR-3.3 | Review packet generation must complete even if some adapters are unavailable (with staleness flags) | Always |

### 10.4 Security

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-4.1 | All API access authenticated via Entra ID or service principal | Always |
| NFR-4.2 | RBAC enforced at API layer, not just UI | Always |
| NFR-4.3 | Audit log immutable and retained for 12 months minimum | Always |
| NFR-4.4 | Agent credentials scoped to minimum necessary permissions | Always |

### 10.5 Portability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-5.1 | Strategic data exportable as structured JSON or YAML | Phase 1 |
| NFR-5.2 | No proprietary data format for strategic objects | Always |
| NFR-5.3 | Adapter interface documented as an open contract | Phase 2 |

---

## 11. UX Requirements

### 11.1 Strategy Map

A navigable visualization of the full strategic hierarchy (themes -> objectives -> KRs/KPIs -> initiatives). Color-coded by confidence/status. Drill-down from any node to its detail view.

### 11.2 Objective Detail View

Single-page view for an objective showing: description, owner, period, KR progress bars with confidence indicators, linked initiatives, recent check-ins, evidence timeline, agent-drafted narrative (if available).

### 11.3 Review Workspace

The primary surface for review preparation. Shows: all objectives for the review period, exception filter, narrative editor (with agent-draft pre-fill), export controls. Designed for the PMO preparing an MBR.

### 11.4 Check-in Form

Minimal-friction form for submitting a check-in. Pre-populated with latest evidence summary. Fields: status selector, narrative text, optional metric override, blocker flag. Accessible from Slack, email, or web.

### 11.5 Admin Console

Configuration surface for: adapter connections, sync schedules, RBAC roles, review cadence settings, agent permissions, audit log viewer.

---

## 12. Success Metrics

### 12.1 Product Metrics

| Metric | Baseline | Target | Timeframe |
|--------|----------|--------|-----------|
| % of KRs with system-derived evidence | 0% | >= 70% | Phase 2 + 30 days |
| MBR packet preparation time | 2-3 days | < 2 hours | Phase 3 + 30 days |
| Strategic objects with no linked evidence source | 100% | < 20% | Phase 2 + 60 days |
| Review packets generated on time | 0% (manual) | >= 90% | Phase 3 + 30 days |
| Agent-drafted narratives accepted without major edits | N/A | >= 60% | Phase 4 + 60 days |

### 12.2 User Metrics

| Metric | Baseline | Target | Timeframe |
|--------|----------|--------|-----------|
| Weekly active strategy owners | 0 | >= 80% of owners | Phase 1 + 60 days |
| Check-in completion rate (per cadence) | 0% | >= 75% | Phase 1 + 90 days |
| Time spent in review workspace per MBR | N/A | < 30 min per reviewer | Phase 3 + 60 days |
| NPS from review participants | N/A | >= 40 | Phase 3 + 90 days |

---

## 13. Rollout Phases

### Phase 1 — Core Strategy Graph

**Duration**: 4 weeks
**Deliverables**: Strategic hierarchy (themes, objectives, KRs, KPIs, initiatives, milestones), ownership assignment, manual check-ins, basic review views, JSON/YAML export.
**Value**: Replaces spreadsheet-based OKR tracking with a structured, navigable graph.

### Phase 2 — Evidence Connectors

**Duration**: 6 weeks
**Deliverables**: Adapter framework, Azure Boards adapter, GitHub adapter, Databricks adapter, evidence computation engine, confidence scoring, freshness tracking.
**Value**: Progress is now derived from connected systems. Self-report becomes the exception.

### Phase 3 — Review Engine

**Duration**: 4 weeks
**Deliverables**: Automated MBR packet generation, exception views, forecast/drift analysis, period comparison, PDF/Markdown export.
**Value**: PMO no longer manually assembles review packets. Reviews are evidence-backed.

### Phase 4 — Agent Layer

**Duration**: 4 weeks
**Deliverables**: Foundry-backed agents for narrative drafting, evidence summarization, risk identification, corrective proposals, goal hygiene checks.
**Value**: Review preparation is augmented by AI. Owners receive pre-drafted narratives. Risks are surfaced proactively.

### Phase 5 — Governance Hardening

**Duration**: 3 weeks
**Deliverables**: Approval workflows, locked snapshots, full audit trail, policy automation (e.g., auto-flag objectives without linked initiatives after N days).
**Value**: Strategic data has enterprise-grade governance. Historical periods are immutable. Compliance and audit requirements are met.

---

## 14. Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|------------|--------|------------|
| R1 | Source system adapters are brittle and break on API changes | Medium | High | Adapter versioning, health monitoring, graceful degradation (stale flags instead of failures) |
| R2 | Users revert to spreadsheets if the system is harder to use | Medium | High | Phase 1 must be simpler than the spreadsheet it replaces. Invest in check-in UX. |
| R3 | Agent-generated narratives are low quality or misleading | Medium | Medium | All agent outputs are drafts requiring human approval. Quality feedback loop. |
| R4 | Evidence computation logic is opaque and users distrust confidence scores | Low | High | Transparent derivation: every confidence score links to its evidence sources and computation method. |
| R5 | Scope creep toward general BI or project management | Medium | Medium | Constitution explicitly excludes these. Product principles enforce review-first UX. |

---

## 15. Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| OQ1 | Should the strategic model support cross-theme objectives (one objective contributing to multiple themes)? | Strategy owner | Open |
| OQ2 | What is the minimum adapter set for Phase 2 (Azure Boards + GitHub, or also Databricks)? | Platform team | Open |
| OQ3 | Should review packets be generated as static documents or as live interactive views? | PMO | Open |
| OQ4 | How should the system handle strategic objects inherited from a parent organization or business unit? | CEO | Open |
| OQ5 | What is the retention policy for evidence data after a review period is locked? | Platform team | Open |

---

## 16. Reverse Summary

**Strategy Control Plane** connects strategic themes, objectives, KRs, KPIs, and initiatives into a single traversable graph. It derives progress from connected systems (Azure Boards, GitHub, Databricks, Odoo) instead of self-report. It generates review packets automatically. It uses Foundry-backed agents to draft narratives and surface risks. It enforces governance through RBAC, audit trails, and locked snapshots. It is not a BI tool, not a project manager, and not an autonomous strategy executor. Every agent output requires human approval before it becomes visible in review context.
