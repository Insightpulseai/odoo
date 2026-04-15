# Common Data Model ↔ Azure DevOps Analytics — Bridge Position

> **Locked:** 2026-04-15
> **Authority:** this file (IPAI position on CDM and ADO Analytics relationship)
> **Source refs:**
> - [Common Data Model — creating schemas](https://learn.microsoft.com/en-us/common-data-model/creating-schemas)
> - [ADO Analytics query parts](https://learn.microsoft.com/en-us/azure/devops/report/analytics/analytics-query-parts?view=azure-devops)
> - [ADO Analytics what-is](https://learn.microsoft.com/en-us/azure/devops/report/powerbi/what-is-analytics?view=azure-devops)

---

## TL;DR

```
ADO Analytics   = ADO's own OData feed for work-tracking events.
                  Schema designed for ADO concepts (WorkItems, Snapshots, Iterations).
                  NOT CDM-native.

CDM             = Microsoft's standardized business-entity schema
                  (Dataverse / D365 / Power Platform / Fabric).
                  Defines canonical entities like Project, Task, WorkOrder, Account.

Relationship    = Indirect. Both are OData-accessible. No native bridge.
                  Manual mapping required if you want ADO Work Items to appear
                  AS CDM "ProjectTask" entities in OneLake or Dataverse.

IPAI position   = Don't bridge yet. Direct ADO Analytics → Power BI is the
                  default. Bridge to CDM only when a CDM consumer materializes
                  (e.g. shared semantic model with Pulser-displaced D365 data).
```

---

## 1. What is CDM

Common Data Model is Microsoft's **standardized schema layer** for business entities. Defines:

- Entities (e.g. `Account`, `Contact`, `Opportunity`, `Project`, `ProjectTask`, `WorkOrder`, `Invoice`)
- Attributes per entity (data types, constraints)
- Relationships (one-to-many, many-to-many)
- Partitioning conventions (folders + manifests in ADLS)
- Metadata in `manifest.cdm.json` files

It powers:
- **Dataverse** (Power Platform / D365 backend)
- **Microsoft Fabric** OneLake CDM mirroring
- **D365 ERP/CRM** entity model
- **Power BI** semantic models that read CDM-shaped folders

---

## 2. What is ADO Analytics

Azure DevOps Analytics is the **dimensional model** layered over the work-tracking event store.

```
Source events (work item revisions, builds, test runs)
        ↓
Analytics service materializes them into:
        ↓
OData entity sets exposed at:
  https://analytics.dev.azure.com/{org}/{project}/_odata/v4.0-preview/

Tables:
  WorkItems              — current state of every work item
  WorkItemRevisions      — full revision history
  WorkItemSnapshot       — point-in-time snapshots (daily)
  WorkItemBoardSnapshot  — kanban board state over time
  Areas, Iterations, Teams, Users
  Pipelines, PipelineRuns, PipelineTasks
  TestRuns, TestPoints, TestResultsDaily
```

**Schema is ADO-specific.** Field names like `WorkItemType`, `IterationPath`, `AreaPath`, `StoryPoints` exist nowhere in CDM.

---

## 3. How they relate (and don't)

### Shared:
- Both are **OData v4** accessible
- Both can land in **Power BI** as data sources
- Both can appear in **Fabric OneLake** as ingestable feeds
- Both support **DAX / M / Power Query** transformations downstream

### Different:
| | ADO Analytics | CDM |
|---|---|---|
| Schema authority | ADO product team | Microsoft Cloud / Dataverse team |
| Native consumers | Power BI ADO connector, ADO dashboards | Dataverse, D365, Fabric, Power Apps |
| Entity model | `WorkItems`, `WorkItemRevisions`, etc. | `Project`, `ProjectTask`, `WorkOrder`, `Account`, etc. |
| Format on disk | OData service | `manifest.cdm.json` + Parquet / CSV in ADLS |
| Refresh model | Service-managed, hourly | Source-defined |
| Cross-system queries | ADO scope only | Designed for cross-system federation |

### No native bridge

There is **no out-of-box mapping** that says "ADO `WorkItem` → CDM `ProjectTask`." You build that mapping yourself if you need it.

---

## 4. When you would bridge them

Bridge ADO Analytics → CDM **only when** at least one of these is true:

| Trigger | Why bridge |
|---|---|
| You have D365 Project Operations data in CDM and want unified PM reporting | One semantic model |
| You're shipping to Azure Marketplace and a customer needs CDM-shaped delivery data | Partner contract requirement |
| Fabric OneLake is your federated lake and ADO data must appear alongside Dataverse data | OneLake federation pattern |
| You're building a CDM-native PMO solution (e.g. Pulser PPM with CDM consumers) | Cross-system semantic |

For IPAI today: **none of these are true yet**. Keep ADO Analytics direct in Power BI; revisit when D365 displacement (Pulser PPM) actually has paying CDM-consuming customers.

---

## 5. The technical bridge (when needed)

### Path A — Power BI semantic model (lightweight)

Easiest: do the mapping **in Power BI**, not in storage.

```
1. Get Data → ADO OData feed → load WorkItems table
2. Get Data → Dataverse → load Project / ProjectTask entities
3. Power Query / DAX:
   - Rename ADO columns to CDM-aligned names
     (WorkItemType → TaskType, AssignedTo → ResourceName, ...)
   - Add derived columns matching CDM (e.g. msdyn_subject, msdyn_actualstart)
   - Join on a unifying key (manual cross-reference table)
4. Build a single semantic model with both sources
```

No CDM file structure. Just naming alignment in the Power BI model. Fast, throwaway, easy to revise.

### Path B — Fabric OneLake CDM landing (heavier)

When you want ADO data persisted as CDM in storage.

```
1. Set up Azure Data Factory pipeline:
   Source: ADO Analytics OData feed
   Sink:   ADLS Gen2 location (CDM-format)

2. Generate CDM manifest:
   manifest.cdm.json describing the WorkItem entity mapped as a CDM ProjectTask
   Include attribute mapping (WorkItemId → msdyn_projecttaskid, etc.)

3. Schedule daily/hourly refresh

4. Mount the CDM folder in Fabric OneLake

5. Power BI reads the OneLake CDM folder; Dataverse can also reference it
```

Requires Fabric capacity. More moving parts. Use only when you have multiple CDM consumers.

### Path C — Dataverse virtual table (advanced)

Pull ADO data **as a Dataverse virtual entity** — appears live in Power Platform without persisting.

```
1. Build a Dataverse virtual entity provider that wraps ADO Analytics OData
2. Map the ADO schema to a custom Dataverse entity definition
3. Power Apps / Dynamics surfaces the data as if it were native
```

Not free. Requires a Power Platform connector and ongoing maintenance. Only use when Power Apps is the consumer.

---

## 6. IPAI canonical position

```
Today:         ADO Analytics → Power BI directly. No CDM mapping.
                Lives in: docs/ops/azure-boards-reporting.md (locked)

Trigger to add bridge:
                When a Pulser PPM customer needs cross-system reporting
                that combines ADO project data + their own Dataverse/D365 data.

If trigger fires:
                Use Path A (Power BI semantic model) first.
                Path B (Fabric CDM landing) only if multiple consumers.
                Path C (Dataverse virtual entity) only if Power Apps is consumer.

Anti-pattern:
                Building CDM-format ADO storage "in case we need it later."
                It's a maintenance tax with no current consumer.
```

---

## 7. Doctrine alignment

| Question | Answer |
|---|---|
| Is ADO Analytics a CDM source? | No. ADO has its own dimensional model. |
| Should we mirror ADO data into CDM-format storage by default? | No. Defer until a real CDM consumer exists. |
| What if a customer asks for CDM-shaped delivery data? | Use Power BI semantic model alignment first (Path A); only escalate to Fabric CDM landing (Path B) for multi-consumer scenarios. |
| What's our current Tier 2 reporting target? | Power BI on direct OData per [`docs/ops/azure-boards-reporting.md`](../ops/azure-boards-reporting.md). |
| When does this position revisit? | Quarterly review aligned with Pulser displacement milestones (per `project_acceleration_plan_20260414.md`). |

---

## 8. CDM aspects worth tracking even without bridging

Even when you don't bridge, watch:

- **Naming conventions** — when we name our own entities (`ipai_finance_*` modules, agent state tables), align field names with CDM where natural so future bridging is cheap. E.g. use `subject` not `title`, `regarding_object_id` not `linked_to`.
- **Date/time semantics** — CDM uses UTC + user-tz separation. Match this in Pulser/Odoo agent state.
- **Identifier patterns** — CDM uses GUIDs. Our agent identifiers should be GUIDs too.

This is **schema hygiene** that costs nothing today and saves rework later.

---

## 9. Practical: ADO Analytics OData query parts

Per [analytics-query-parts](https://learn.microsoft.com/en-us/azure/devops/report/analytics/analytics-query-parts?view=azure-devops):

```
URL pattern:
  https://analytics.dev.azure.com/{org}/{project}/_odata/{version}/{EntitySet}?{query}

Example: All active Stories assigned to a user in current iteration
  https://analytics.dev.azure.com/insightpulseai/ipai-platform/_odata/v4.0-preview/WorkItems
    ?$filter=WorkItemType eq 'User Story'
       and State eq 'Active'
       and AssignedTo/UserEmail eq 'admin@insightpulseai.com'
       and Iteration/IterationName eq @CurrentIteration
    &$select=WorkItemId,Title,StoryPoints,State

Example: Daily snapshot of New/Active/Resolved/Closed counts last 30 days
  https://.../WorkItemSnapshot
    ?$apply=filter(DateValue ge 2026-03-15)
      /groupby((DateValue,State),aggregate($count as Count))
```

These are the building blocks for both Tier 1 widgets (Chart for work items widget query) AND Tier 2 Power BI datasets.

---

## References

- [Common Data Model — overview](https://learn.microsoft.com/en-us/common-data-model/)
- [CDM — creating schemas](https://learn.microsoft.com/en-us/common-data-model/creating-schemas)
- [ADO Analytics what-is](https://learn.microsoft.com/en-us/azure/devops/report/powerbi/what-is-analytics?view=azure-devops)
- [ADO Analytics query parts](https://learn.microsoft.com/en-us/azure/devops/report/analytics/analytics-query-parts?view=azure-devops)
- [ADO Analytics data model](https://learn.microsoft.com/en-us/azure/devops/report/extend-analytics/data-model-analytics-service?view=azure-devops)
- Companions: [`docs/ops/azure-boards-reporting.md`](../ops/azure-boards-reporting.md), [`docs/architecture/domain-and-web-bom-target-state.md`](./domain-and-web-bom-target-state.md)

---

*Last updated: 2026-04-15*
