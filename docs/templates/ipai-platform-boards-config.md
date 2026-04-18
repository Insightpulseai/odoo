# `ipai-platform` — Azure Boards Configuration

> Concrete Boards configuration: teams, area paths, iterations, WIP limits, and
> backlog rules. Applies Microsoft's Agile product-management guidance to IPAI's
> lean operating model without forcing full Scrum ceremony.

---

## 1. Teams (5 delivery streams)

Organize by value stream, not by repo. One team = one autonomous delivery group.

| Team | Area path | Owns |
|---|---|---|
| `Pulser Runtime & Governance` | `ipai-platform\Runtime` | Agent platform, supervisor orchestration, Entra Agent ID, Content Safety, eval framework, deploy pipelines |
| `Finance Core` | `ipai-platform\Finance` | Pulser finance copilot, AP invoice agent, close orchestration, FP&A, tax strategist |
| `PH Compliance & Close` | `ipai-platform\Compliance` | BIR 2307/1601/1604, intercompany invoice readiness, compliance auditing, regulatory reporting |
| `Documents & Integrations` | `ipai-platform\Documents` | OCA DMS, Document Intelligence, document taxonomy, evidence retention, Azure AI Search grounding |
| `Payments & Launch` | `ipai-platform\Launch` | Marketplace GTM (Wave 1 SaaS), M365 declarative agent (Wave 2), Power BI App (Wave 3), payment integrations |

**Rationale:** 5 teams × 1-2 contributors each = 5-10 people. Fits current IPAI team size. Each team has a clear area path so work items inherit context on creation.

## 2. Area paths

```
ipai-platform                              (project root)
├── Runtime                                (Pulser Runtime & Governance team)
│   ├── AgentPlatform
│   ├── Foundry
│   ├── Supervisor
│   ├── EvalFramework
│   └── DeployPipelines
├── Finance                                (Finance Core team)
│   ├── PulserFinance
│   ├── APInvoice
│   ├── CloseOrchestration
│   └── FPA
├── Compliance                             (PH Compliance & Close team)
│   ├── BIR-2307
│   ├── BIR-1601
│   ├── Intercompany
│   └── RegReporting
├── Documents                              (Documents & Integrations team)
│   ├── DMS
│   ├── DocumentIntelligence
│   ├── Taxonomy
│   └── AISearch
└── Launch                                 (Payments & Launch team)
    ├── Marketplace-Wave1
    ├── M365Agent-Wave2
    ├── PowerBIApp-Wave3
    └── Payments
```

Use nested paths for filter granularity without creating more teams.

## 3. Iterations (rolling 180-day roadmap)

Start with 4 release windows aligned to marketplace publish target:

| Iteration | Dates | Focus |
|---|---|---|
| `R1-Foundation-30d` | 2026-04-18 → 2026-05-17 | ISV Success activation, Entra Agent ID, GitHub org move, secure score uplift, infra hardening |
| `R2-Core-Execution-60d` | 2026-05-18 → 2026-07-17 | SaaS fulfillment API, co-sell doc pack, Preview submit, BIR 2307 validator, PG MCP deploy |
| `R3-PH-Ops-Hardening-90d` | 2026-07-18 → 2026-10-17 | Marketplace Wave 1 publish, UAT pack, pilot readiness, app accelerate nomination |
| `R4-GA` | 2026-10-18 → 2027-01-17 | Wave 2 M365 agent publish, case studies, Marketplace Rewards tier 2, IP co-sell readiness |

Future iterations (R5, R6, R7) to be defined as R4 closes.

Each team works within these windows at its own cadence. No mandatory sprint ceremony — teams coordinate on releases, not sprints.

## 4. WIP limits

Apply WIP limits to the two most constrained columns: `In Progress` and `Review`.

| Team | Committed (WIP) | Review (WIP) | Rationale |
|---|---|---|---|
| Pulser Runtime & Governance | 3 | 2 | Heavy infra work; deep focus required |
| Finance Core | 2 | 2 | Business-logic heavy; limit context switching |
| PH Compliance & Close | 2 | 1 | Single-person team at start; prevent overload |
| Documents & Integrations | 2 | 2 | Integration work; needs uninterrupted runs |
| Payments & Launch | 3 | 2 | GTM work, parallel tracks |

Rules:
- If a column is at WIP limit, no new item enters it
- Work already in progress takes priority over new starts
- If WIP routinely hits limit, add capacity or reduce scope — don't raise the limit as a first response

## 5. Backlog rules

### 5.1 Epic-level (portfolio roadmap)
- Epics live in the Features board (Scrum: Epic → PBI; skip intermediate Feature unless genuinely needed)
- Product manager (Jake) orders Epics
- Each Epic MUST have: title, goal statement, target iteration window, success criteria, link to spec bundle
- Epics transitioning to Done require written retrospective in `docs/evidence/<stamp>/`

### 5.2 PBI-level (team backlog)
- PBIs sized to complete within ONE iteration (≤ 30 days for R1; ≤ 60 for R2)
- Clear acceptance criteria required before pulling into Committed
- Parent Epic required (no orphan PBIs)
- Target repo identified in description (single repo per PBI — see `docs/templates/ado-copilot-work-item.md`)
- Tags: `wave-1|wave-2|wave-3`, capability area, priority

### 5.3 Task-level (iteration execution)
- One PBI → multiple Tasks (≤ 8 hours each)
- Tasks assigned to specific team members
- Remaining Work updated daily when Task is Committed
- Task done = change merged + verified (not just pushed)

### 5.4 Bug-level
- Bugs logged against the module they affect (correct Area path)
- Severity: 1 (blocks users) · 2 (workaround exists) · 3 (cosmetic)
- Severity 1 bugs break into the current iteration even if it requires pushing a PBI back
- Bugs from pilot/UAT feed back into appropriate team's backlog

### 5.5 Impediment-level
- Cross-team blockers only (not general "to-do" items)
- Must have explicit owner + expected resolution date
- Escalate if impediment > 3 days
- Visible on dedicated impediments query + dashboard widget

## 6. Dependency links

Use Predecessor/Successor link types for formal dependencies:

| Common dependency pattern | Predecessor | Successor |
|---|---|---|
| Entra Agent ID before agent deployment | Entra registration PBI | Agent deploy PBI |
| PG MCP before agent grounding | `ISSUE-PH-045` (PG MCP) | `ISSUE-PH-046` (schema adapter) |
| Spec bundle approval before implementation | Spec review PBI | Implementation PBI |
| Tax profile validated before marketplace publish | Tax profile PBI | Preview submit PBI |
| Design partner LOI before case study | LOI PBI | Case study PBI |

Tag with `dependency` for cross-cutting blocker queries.

## 7. Rollup views

Create these dashboards for progress visibility:

| Dashboard | Audience | Widgets |
|---|---|---|
| Executive Roadmap | Jake, investors, MS sellers | Epic rollup, target dates, at-risk items |
| Team Sprint | Each team | Committed items, burndown, velocity, impediments |
| Release Gate | Jake + compliance | UAT scenarios complete, eval gates passed, blocking bugs |
| Microsoft Co-sell Pipeline | Jake, So Yeong Choi | Wave 1 Epic progress, co-sell doc pack status, App Accelerate submission state |

Dashboards auto-refresh from Analytics (available in cloud ADO only).

## 8. Implementation sequence

- [ ] Create 5 teams with area paths (ADO admin > Project settings > Teams)
- [ ] Define iterations R1-R4 (ADO admin > Project settings > Iterations)
- [ ] Assign default area/iteration to each team
- [ ] Configure WIP limits on each team's board (Team settings > Board > Columns)
- [ ] Seed 9 Epics (from `spec/microsoft-marketplace-gtm/tasks.md` + other spec bundles)
- [ ] Create dashboards (above)
- [ ] Add predecessor links for known dependency chains
- [ ] Document this config in `ipai-platform` project wiki (`Project settings > Wiki`)

## 9. Anti-patterns (Microsoft guidance — don't do)

- ❌ One team per repo (creates governance overhead without delivery benefit)
- ❌ Inconsistent iteration cadence across teams (breaks forecasting)
- ❌ Umbrella Epics that never close (Epics must have completion criteria)
- ❌ Raising WIP limits to keep flowing (solve bottleneck instead)
- ❌ Skipping daily updates (state charts go stale, decisions degrade)
- ❌ Tracking non-engineering items in Boards (see `docs/architecture/plane-separation.md`)

## 10. References

- `docs/architecture/plane-separation.md` — four-plane model
- `docs/architecture/oprg-plane-mapping.md` — OPRG scenario mapping
- `docs/templates/ado-copilot-work-item.md` — Copilot-ready work item template
- `docs/templates/repo-to-boards-contract.md` — AB# linking conventions
- `docs/templates/basic-vs-scrum-decision.md` — process choice
- [Microsoft — Agile best practices](https://learn.microsoft.com/en-us/azure/devops/boards/best-practices-agile-project-management)
