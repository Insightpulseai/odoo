# Azure Boards Portfolio Target State

> **Locked:** 2026-04-15
> **Project:** `insightpulseai/ipai-platform`
> **Authority:** this file (Boards hierarchy + portfolio model)
> **Companions:**
> [`azure-boards-area-iteration-map.md`](./azure-boards-area-iteration-map.md),
> [`azure-boards-delivery-plans.md`](./azure-boards-delivery-plans.md),
> [`azure-boards-github-traceability.md`](./azure-boards-github-traceability.md),
> [`docs/ops/azure-boards-operating-guide.md`](../ops/azure-boards-operating-guide.md)
> **Microsoft refs:**
> - [Manage product and portfolio backlogs](https://learn.microsoft.com/en-us/azure/devops/boards/plans/portfolio-management?view=azure-devops)
> - [Define features and epics](https://learn.microsoft.com/en-us/azure/devops/boards/backlogs/define-features-epics?tabs=agile-process&view=azure-devops)

---

## Current state (2026-04-15)

ADO project `ipai-platform` is **under-instrumented**:
- Pipelines exist; several runs red
- Team dashboard empty
- Test Plans: only 2
- Analytics Views: not yet wired (and limited to flat work-item lists)

Boards is currently acting like a **flat issue list**, not a portfolio.

---

## Target hierarchy (canonical Agile)

```
Initiative / Program
  Epic
    Feature
      User Story / Backlog Item
        Task
        Bug
```

Microsoft Agile process. Depth 5. Hierarchy enforced via parent links.

---

## The Initiative

```
Initiative: InsightPulseAI — Multitenant SaaS Platform Buildout
```

Container for ALL platform work. One Initiative. New Initiatives only when a genuinely new program starts (e.g., a new acquired product line).

---

## Canonical Epic set (7)

| # | Epic | Owning area path | Plane |
|---|---|---|---|
| 1 | Core Operations Plane | `\InsightPulseAI\CoreOps` | transaction |
| 2 | Ads / Customer Intelligence Plane | `\InsightPulseAI\AdsIntel` | agent + data-intelligence |
| 3 | Research / PrismaLab Plane | `\InsightPulseAI\Research` | research |
| 4 | Data-Intelligence Plane | `\InsightPulseAI\DataIntel` | data-intelligence |
| 5 | Shared SaaS Control Plane | `\InsightPulseAI\Platform` | shared |
| 6 | Delivery / Platform Engineering | `\InsightPulseAI\ReleaseOps` | platform |
| 7 | FinOps / Governance | `\InsightPulseAI\Platform` | observability |

These 7 Epics map 1:1 to the 4 product planes + 3 cross-cutting concerns from [`docs/architecture/revised-bom-target-state.md`](../architecture/revised-bom-target-state.md).

---

## Example Feature layout per Epic

### Epic 1 — Core Operations Plane

- Feature: Odoo runtime
- Feature: Finance parity (Accounting + Close + Cash + FP&A)
- Feature: Project Operations parity (PPM)
- Feature: Pulser advisory workflows
- Feature: BIR compliance (per [`docs/backlog/ph-close-bir-compliance-board-pack.md`](./ph-close-bir-compliance-board-pack.md))

### Epic 2 — Ads / Customer Intelligence Plane

- Feature: Ad activation workflows
- Feature: Customer profile unification
- Feature: Segmentation
- Feature: Journeys / lead handoff
- Feature: Campaign analytics

### Epic 3 — Research / PrismaLab Plane

- Feature: Free tools (Clarify Question, Search PubMed, PRISMA diagram, Review type)
- Feature: PRISMA assistant (grounded RAG)
- Feature: Export and artifacts
- Feature: Research telemetry
- Feature: Regulated-scope governance gate

### Epic 4 — Data-Intelligence Plane

- Feature: Bronze / Silver / Gold lakehouse
- Feature: Audience clustering (Quilt-like)
- Feature: PH-localized data wedge (per [`docs/strategy/data-intelligence-vertical-target-state.md`](../strategy/data-intelligence-vertical-target-state.md))
- Feature: Power BI semantic model
- Feature: Fabric mirroring

### Epic 5 — Shared SaaS Control Plane

- Feature: Tenant model + pricing
- Feature: Identity and access (Entra apps, MIs)
- Feature: Metering and billing events
- Feature: Shared edge / domains (AFD + WAF)
- Feature: Control-plane APIs

### Epic 6 — Delivery / Platform Engineering

- Feature: Bicep / IaC baseline
- Feature: Azure Pipelines hardening (10 Epics in [`az400-devops-platform-learning-board-pack.md`](./az400-devops-platform-learning-board-pack.md))
- Feature: Observability baseline
- Feature: Release strategies (blue-green, canary, ring)

### Epic 7 — FinOps / Governance

- Feature: Tag enforcement (per [`ssot/azure/tagging-standard.yaml`](../../ssot/azure/tagging-standard.yaml))
- Feature: Budget + anomaly + alerting
- Feature: BOM compliance gate
- Feature: Naming-standard enforcement
- Feature: Regulated-scope escalation workflow

---

## Use area paths as team ownership (NOT labels)

Microsoft's portfolio guidance: assign work to teams via **area paths**, not tags or labels. Shared/management teams keep parent Epics and Features on a common backlog; child items get pushed down to feature teams via area path assignment.

Mapping rule:
- **Epics** → owned by the management/shared portfolio team
- **Features** → owned by the domain team (assigned via area path)
- **Stories / Tasks** → owned by the delivery team (assigned via area path + area sub-path if needed)

See [`azure-boards-area-iteration-map.md`](./azure-boards-area-iteration-map.md) for the full area path tree.

---

## Rollups, not manual status prose

Stop writing "% complete" by hand on Epics/Features. Use Boards' **rollup columns**:
- `Descendant count` (how many child items)
- `Effort rollup` (sum of Story Points)
- `Remaining work rollup`
- `Progress bar` (Closed vs total descendants)

Every Epic and every Feature must show:
- Rollup progress column
- Descendant count
- Target Iteration
- Owning Area Path
- Dependency indicator

---

## Dependency links (standardized)

Use the right link type — not just "Related" for everything.

| Link type | When |
|---|---|
| **Predecessor / Successor** | Time-based, hard dependency (X must finish before Y starts) |
| **Related** | Informational coupling, no hard ordering |
| **Parent / Child** | Always — maintains hierarchy |
| **Tested By / Tests** | Story ↔ Test Case |
| **Affects / Affected By** | Bug ↔ another work item |

Rule for IPAI:
```
Identity / networking / CI prerequisites = Predecessor
Informational or coordination coupling   = Related
```

---

## Required fields on every work item

Per [`azure-boards-operating-guide.md`](../ops/azure-boards-operating-guide.md):
- Title (≤ 70 chars)
- Assigned To (single owner)
- State (per type)
- Area Path (canonical from area-iteration-map)
- Iteration Path (current sprint or Backlog)
- Tags (`environment`, `plane`, `cadence` if recurring, `compliance_scope` if compliance)
- Priority (1–4)
- Story Points (Stories only; Fibonacci)
- Acceptance Criteria (Stories only; bullet list)
- Repro Steps (Bugs only)

---

## Anti-patterns

- **Boards as a flat issue list** — broken; portfolio hierarchy is the point
- **Manual % complete on Epics** — use rollups
- **Cross-team blockers tracked in comments only** — must use Predecessor/Related links
- **Skipping area path** — orphans work from team ownership
- **One mega-Epic per repo** — Epics are multi-sprint outcomes, not repo containers
- **One mega-Feature per deliverable** — split into Features per slice
- **Issues with no Iteration Path** — work evaporates into Backlog with no timing owner

---

## SMART success criteria

- 100% of active work items have an owning area path
- 100% of Stories have a parent Feature
- 100% of Features have a parent Epic
- 100% of code-delivery PRs link to a Boards work item
- 90%+ of active Features show rollup progress from linked child work
- 0 cross-team blockers tracked only in comments (must use links)
- 0 "orphan" implementation PRs without a Feature/Story parent

---

## Migration from current state

| Current | Target | Action |
|---|---|---|
| Flat issue list | 7 Epics + Features + Stories | Reparent existing items into the canonical 7 Epics |
| No area paths | 6 area paths per [`azure-boards-area-iteration-map.md`](./azure-boards-area-iteration-map.md) | Create area path tree; assign all items |
| No iteration paths | Iteration paths per sprint (2-week cadence) | Create rolling 6-month iteration tree; reassign items |
| No Delivery Plans | 3 Delivery Plans per [`azure-boards-delivery-plans.md`](./azure-boards-delivery-plans.md) | Create plans; populate from Epics |
| No GitHub traceability | Per [`azure-boards-github-traceability.md`](./azure-boards-github-traceability.md) | Wire AB# linking; enforce via PR templates |
| Empty dashboards | 3 dashboards per [`docs/ops/azure-boards-reporting.md`](../ops/azure-boards-reporting.md) | Create + pin |
| 2 Test Plans | 5 Test Plans (one per major plane + 1 release gate) | See [`azure-boards-area-iteration-map.md`](./azure-boards-area-iteration-map.md) §Test Plans |

---

*Last updated: 2026-04-15*
