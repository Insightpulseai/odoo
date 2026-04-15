# Azure Boards Reporting & Analytics — IPAI Platform

> **Locked:** 2026-04-15
> **Project:** `insightpulseai/ipai-platform`
> **Pairs with:** [`docs/ops/azure-boards-operating-guide.md`](./azure-boards-operating-guide.md)
> **Source refs:**
> - [Widget catalog](https://learn.microsoft.com/en-us/azure/devops/report/dashboards/widget-catalog?view=azure-devops)
> - [Analytics for Power BI](https://learn.microsoft.com/en-us/azure/devops/report/powerbi/what-is-analytics?view=azure-devops)

---

## Two reporting tiers

```
Tier 1: Built-in dashboard widgets   ← daily ops, free, in ADO
Tier 2: Power BI + Analytics views   ← exec/board reports, needs PBI Pro
```

Use **Tier 1** for sprint mechanics, daily standup, blocked-item visibility.
Use **Tier 2** for cross-quarter trends, FinOps overlays, multi-team rollups.

---

## Tier 1 — IPAI canonical dashboards (built-in widgets)

3 dashboards. Mobile-friendly. Pin to project home.

### Dashboard A — "Active Sprint" (one per sprint)

For day-to-day execution. Refreshes live.

| Widget | What it shows | Why |
|---|---|---|
| **Sprint burndown** | Story points remaining vs ideal line | Sprint health |
| **Sprint capacity** | Capacity vs assigned work per person | Overallocation alarm |
| **Sprint overview** | All items in active sprint, grouped by State | Standup view |
| **Cumulative flow diagram** | New / Active / Resolved / Closed over sprint | Bottleneck detection |
| **Chart for work items** (Bugs by Priority) | Bug Priority distribution | Quality signal |
| **Query tile: Blocked** | Count + click-through to Blocked query | Daily unblock surface |
| **Query tile: My Sprint** | Personal active items | Per-user view |

### Dashboard B — "Quarterly Initiative Roll-up"

For monthly business reviews. Refreshed weekly.

| Widget | What it shows | Why |
|---|---|---|
| **Chart for work items** (Epic State) | Pivot Epic by State, count of Features | Initiative progress |
| **Cycle time** widget | Story cycle time avg by Area Path | Plane velocity |
| **Lead time** widget | Time from creation → Closed by WorkItemType | Bottleneck detection |
| **Velocity** | Story Points completed per sprint, trailing 6 sprints | Capacity planning |
| **Test results trend** | Pass rate over time (when Test Plans on) | Quality trend |
| **Markdown** widget | Initiative narrative + risks + asks | Exec context |
| **Query tile: This Month's Closed** | Closed items count | Throughput evidence |

### Dashboard C — "Plane Health" (one per major plane)

For technical leads. One dashboard per plane: `transaction`, `agent`, `data-intelligence`, `web`, `observability`.

| Widget | What it shows | Why |
|---|---|---|
| **Chart for work items** (Tags filter `plane:agent`) | Active items by State | Plane utilization |
| **Build history** | Recent Azure Pipelines runs for plane | CI health |
| **Deployment status** | Recent ACA deploys for plane | Runtime health |
| **Pull request** widget | Open PRs touching plane area path | Code review queue |
| **Code tile** | Repo activity for plane folders | Dev velocity |
| **Query tile: Plane Bugs** | Open bugs scoped to plane | Defect surface |

---

## Widget recipe — "Chart for work items"

The most-used widget. Per [widget catalog](https://learn.microsoft.com/en-us/azure/devops/report/dashboards/widget-catalog?view=azure-devops#chart-wit-widget).

```
Widget: Chart for work items
  Query: <one of the 8 pinned queries from Boards Operating Guide>
  Chart type: Stacked bar | Pie | Pivot | Trend (last 30 days)
  Group by: State | AssignedTo | Tags | Priority | AreaPath
  Aggregate: Count | Sum (Story Points) | Avg (Cycle Time)
  Color: Auto | Custom palette
  Size: 2x2 (small) | 4x4 (large)
```

Example for IPAI "Blocked Items" tile:

```yaml
Widget:    Chart for work items
Query:     Shared Queries / Blocked
Chart:     Stacked bar
Group by:  AreaPath
Aggregate: Count
Size:      2x2
Position:  Top-right of Active Sprint dashboard
```

---

## Tier 2 — Power BI + Analytics

ADO Analytics is a BI-friendly model layered over the work-tracking event store. Two access modes:

### Mode A — Power BI views (single-team, simple)

```
Power BI → Get Data → Online Services → Azure DevOps (Beta)
  Account:  insightpulseai
  Project:  ipai-platform
  View:     Work items - Today | Velocity | Cycle Time | Lead Time
```

Pre-built views. No DAX needed. Data refreshes hourly.

### Mode B — OData feed (multi-team, custom dashboards)

```
Power BI → Get Data → OData feed
  URL: https://analytics.dev.azure.com/insightpulseai/ipai-platform/_odata/v4.0-preview/

Tables:
  - WorkItems
  - WorkItemRevisions   (history)
  - WorkItemSnapshot    (point-in-time)
  - WorkItemBoardSnapshot
  - Pipelines (when CI gates configured)
  - PipelineRuns
  - TestRuns
  - Areas, Iterations, Teams, Users
```

Use OData when you need:
- Cross-team rollups
- Joins with non-ADO data (FinOps cost data, deploy data, customer signal)
- Custom DAX measures (e.g. "P0 bug-fix lead time per plane")
- Snapshot reports ("how many Stories were Active on the 1st of each month")

### IPAI canonical Power BI workspace structure

```
Power BI Workspace: "IPAI Delivery"
├── Datasets:
│   ├── ADO Work Items (OData feed, hourly refresh)
│   ├── Azure Pipelines (OData feed, hourly refresh)
│   ├── Azure FinOps (Cost Mgmt API, daily refresh)
│   └── Azure Resource Inventory (Resource Graph daily)
├── Reports:
│   ├── Initiative Health
│   ├── Sprint Velocity Trend (rolling 12 sprints)
│   ├── Plane-by-Plane Throughput
│   ├── Bug Lead Time / MTTR
│   ├── Pipeline Success Rate
│   └── FinOps × Throughput overlay (cost per shipped Story)
└── Dashboards:
    ├── Exec — IPAI Quarterly Health (monthly review)
    ├── Eng Lead — Plane Health
    └── Team — Sprint Operations
```

---

## ⚠ Power BI procurement note

Per memory `project_powerbi_trial_expiry.md`:

```
Power BI Pro trial expires ~2026-05-20.
Procurement needed before then or all Tier 2 reports go dark.
```

Tier 1 (built-in widgets) does NOT require Power BI and continues to work.

---

## Refresh / latency expectations

| Surface | Latency |
|---|---|
| ADO dashboard widgets | Real-time on view |
| ADO query results | Real-time |
| ADO Analytics views (PBI) | ~hourly |
| ADO OData feed (PBI) | ~hourly (longer for heavy snapshot tables) |
| Test results trend | After test run completes |
| Velocity widget | After sprint close + a few minutes |

If a stakeholder needs minute-level freshness, use Tier 1 widgets, not Power BI.

---

## What lives in dashboards vs Power BI

| Need | Tier 1 widget | Tier 2 Power BI |
|---|---|---|
| Daily standup view | ✅ | — |
| "How's this sprint going?" | ✅ | — |
| Per-person sprint capacity | ✅ | — |
| Blocked items count | ✅ | — |
| "How are we trending across 6 sprints?" | — | ✅ |
| "Cost per shipped Story by plane" | — | ✅ |
| "P0 bug-fix MTTR last 90 days" | — | ✅ |
| "Initiative-level rollup for board meeting" | partial | ✅ (preferred) |
| "Cross-team comparison" | — | ✅ |

---

## Setup checklist

- [ ] Open `https://dev.azure.com/insightpulseai/ipai-platform/_dashboards`
- [ ] Create 3 dashboards: `Active Sprint`, `Quarterly Initiative Roll-up`, `Plane Health — <plane>` × 5
- [ ] Add the widgets per the tables above
- [ ] Pin all 3 to project home
- [ ] (Tier 2) Confirm Power BI Pro is licensed before 2026-05-20
- [ ] (Tier 2) Connect Power BI Desktop to OData feed `https://analytics.dev.azure.com/insightpulseai/ipai-platform/_odata/v4.0-preview/`
- [ ] (Tier 2) Publish reports to "IPAI Delivery" workspace
- [ ] (Tier 2) Set datasets to refresh hourly
- [ ] Document RACI: who owns each dashboard / report

---

## Anti-patterns

- Building a dashboard with **15+ widgets** — use multiple dashboards, not one mega-board
- Using Power BI for what built-in widgets do natively (cost without value)
- Skipping refresh schedule setup (reports go stale, exec loses trust)
- One dashboard for "everything" — split by audience (exec vs lead vs team)
- Using ADO charts as primary authority for FinOps — Power BI is required for the cost overlay

---

## References

- [Widget catalog](https://learn.microsoft.com/en-us/azure/devops/report/dashboards/widget-catalog?view=azure-devops)
- [Chart for work items widget](https://learn.microsoft.com/en-us/azure/devops/report/dashboards/widget-catalog?view=azure-devops#chart-wit-widget)
- [Analytics for Power BI](https://learn.microsoft.com/en-us/azure/devops/report/powerbi/what-is-analytics?view=azure-devops)
- [OData query reference](https://learn.microsoft.com/en-us/azure/devops/report/extend-analytics/data-model-analytics-service?view=azure-devops)
- Companions: [`docs/ops/azure-boards-operating-guide.md`](./azure-boards-operating-guide.md), [`docs/backlog/az400-devops-platform-learning-board-pack.md`](../backlog/az400-devops-platform-learning-board-pack.md)

---

*Last updated: 2026-04-15*
