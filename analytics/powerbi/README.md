# Azure Boards Power BI Dashboard

PBIP (Power BI Project) format — version-controlled, diffable, CI-ready.

## Data source

**Azure DevOps Analytics OData v4.0-preview**

```
https://analytics.dev.azure.com/insightpulseai/ipai-platform/_odata/v4.0-preview/
```

Entity sets:
- `WorkItems` — all work items with fields, state, iteration, tags
- `Iterations` — iteration paths with start/end dates

Auth: Entra ID (same as `az login` session). Power BI prompts for organizational account on first connect.

## Semantic model (TMDL)

| Table | Source | Key measures |
|---|---|---|
| `WorkItems` | OData `WorkItems` entity | Total Work Items, To Do / In Progress / Done counts, Completion Rate, Issue/Task/Epic counts |
| `Iterations` | OData `Iterations` entity | Days Remaining in Current Iteration |

Relationship: `WorkItems.Iteration` → `Iterations.IterationName` (bidirectional)

## How to open

1. Install [Power BI Desktop](https://powerbi.microsoft.com/desktop/) (free)
2. Open `azure-boards-dashboard.pbip`
3. Sign in with `admin@insightpulseai.com` when prompted for OData credentials
4. Data loads from ADO Analytics
5. Build visuals on the canvas

## Suggested visuals

| Visual | Measure / Field | Purpose |
|---|---|---|
| **Card** | Total Work Items | KPI header |
| **Card** | Completion Rate | Progress % |
| **Stacked bar** | Count by State × Iteration | Iteration burndown |
| **Donut** | Count by WorkItemType | Epic / Issue / Task split |
| **Matrix** | Iteration × State (count) | Pivot table of progress |
| **Slicer** | Tags | Filter by wave, domain, etc. |
| **Timeline** | Iteration StartDate → EndDate | Release timeline R1→R4 |

## Iterations (from live ADO data)

| Iteration | Start | End | Duration |
|---|---|---|---|
| R1-Foundation-30d | 2026-04-14 | 2026-05-14 | 30 days |
| R2-Core-Execution-60d | 2026-05-15 | 2026-07-14 | 60 days |
| R3-PH-Ops-Hardening-90d | 2026-07-15 | 2026-10-14 | 90 days |
| R4-GA | 2026-10-15 | 2026-12-15 | 60 days |

## Doctrine

- Power BI is the primary mandatory business-facing reporting surface (CLAUDE.md cross-repo invariant #12)
- ADO Analytics OData is the canonical query path for Boards data (not REST API scraping)
- PBIP format enables git version control + PR review of report changes
- Auth: Entra organizational account, not PAT
