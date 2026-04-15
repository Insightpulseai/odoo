# Azure Boards Delivery Plans

> **Locked:** 2026-04-15
> **Project:** `insightpulseai/ipai-platform`
> **Companions:** [`azure-boards-portfolio-target-state.md`](./azure-boards-portfolio-target-state.md), [`azure-boards-area-iteration-map.md`](./azure-boards-area-iteration-map.md)

---

## Why Delivery Plans

Microsoft's intended cross-team visibility surface for work across Iterations and Areas. **3 plans** for IPAI, each scoped to a different audience.

---

## Plan 1 — Executive Portfolio Plan

**Audience:** stakeholders, leadership, board reviews
**Cadence:** monthly review
**Granularity:** Epic + major Feature only

```
Plan name:            Executive Portfolio Plan
Time horizon:         Current quarter + next quarter
Work item types:      Epic, Feature
Teams included:       all 6 area paths
Filter:               Priority ≤ 2 (P0–P1) only
Show dependencies:    yes (Predecessor / Successor + Related)
```

What it shows:
- All 7 canonical Epics
- Major Features within Epics
- R2 / R3 / R4 ship sprints highlighted
- Cross-Epic dependencies
- Slip-risk indicators

---

## Plan 2 — Product Delivery Plan

**Audience:** product team leads, engineering managers
**Cadence:** weekly review
**Granularity:** Feature + Story

```
Plan name:            Product Delivery Plan
Time horizon:         Current sprint + next 4 sprints
Work item types:      Feature, User Story
Teams included:       CoreOps, AdsIntel, Research, DataIntel
Filter:               State IN (New, Active, Resolved)
Show dependencies:    yes
```

What it shows:
- Active product Features
- Stories under each Feature
- Sprint commitments and slips
- Per-team velocity context
- Dependencies that affect product ship

---

## Plan 3 — Platform / Release Plan

**Audience:** platform engineering + release ops
**Cadence:** bi-weekly review (sprint cadence)
**Granularity:** Feature + Story + Task

```
Plan name:            Platform / Release Plan
Time horizon:         Current sprint + next 6 sprints
Work item types:      Feature, User Story, Task, Bug
Teams included:       Platform, ReleaseOps
Filter:               State <> Closed
Show dependencies:    yes
```

What it shows:
- Infra / IaC / pipelines / observability work
- Identity hardening
- Release cuts + canary / blue-green rollouts
- Bug backlog tied to release readiness
- Cross-team prerequisites for product features

---

## Setup checklist

1. **Boards → Delivery Plans → New Plan**
2. Create the 3 plans per the specs above.
3. For each plan, configure:
   - Time horizon (start month + duration)
   - Teams (multi-select from area path tree)
   - Work item type filters
   - Field criteria (Priority, Tags, etc.)
4. Set rollup style (default: progress bar from descendants)
5. Pin the plan to the project navigation
6. Document plan owner + review cadence in `ssot/governance/delivery-plan-raci.yaml`

---

## Audience-split principle

Each plan answers **one question** for **one audience**. Do not build a single mega-plan for all audiences — Microsoft's pattern is multiple narrow plans.

| Plan | Question it answers | Audience |
|---|---|---|
| Executive Portfolio Plan | "Are we shipping the right Epics on time?" | leadership |
| Product Delivery Plan | "Is the product team on track sprint-by-sprint?" | product + eng leads |
| Platform / Release Plan | "Is the platform stable enough to ship?" | platform + release ops |

---

## Anti-patterns

- One plan with all teams + all work item types — unreadable
- Filtering to single-team scope (defeats cross-team visibility — that's what the team backlog is for)
- Pinning Stories to the Executive plan (too granular for that audience)
- Skipping dependency display (dependencies are the **point** of Delivery Plans)
- Time horizon > 2 quarters (becomes vague speculation)

---

## SMART success criteria

- 100% of P0/P1 Epics visible in Executive Portfolio Plan
- 100% of active Stories visible in Product Delivery Plan
- 100% of release-blocking Tasks visible in Platform / Release Plan
- Each plan reviewed on its declared cadence (logged in `ssot/governance/delivery-plan-raci.yaml`)
- 0 cross-team dependencies tracked outside Delivery Plan visualization

---

*Last updated: 2026-04-15*
