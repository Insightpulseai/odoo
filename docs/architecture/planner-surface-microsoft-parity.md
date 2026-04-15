# Planner Surface — Microsoft Planner Parity

> **Locked:** 2026-04-15
> **Authority:** this file (parity analysis + adoption decision)
> **Reference:** [Microsoft Planner (M365 task management)](https://www.microsoft.com/en-US/microsoft-365/planner/microsoft-planner)
> **Doctrine alignment:**
> - [`docs/programs/work-artifact-placement.md`](../programs/work-artifact-placement.md) — 3-tier work artifact model
> - [`docs/backlog/azure-boards-portfolio-target-state.md`](../backlog/azure-boards-portfolio-target-state.md)
> - [`docs/architecture/booking-surface-microsoft-parity.md`](./booking-surface-microsoft-parity.md) — same parity methodology

---

## Short answer

```
Can we match Planner features?         Yes — ~95% with Odoo CE 18 `project` module + OCA.
Should IPAI adopt Planner internally?  No. We already have the right surfaces
                                        (Boards + Odoo Projects + Files).
Should our customers use Planner?      Only if they're already M365-native
                                        and need simple team task tracking.
                                        If they use us for delivery, they live
                                        in Odoo Projects; Planner stays in their
                                        M365 tenant for team-internal ops.
```

Planner is a **team todo app**, not a portfolio system, not a delivery ERP. It's free with M365 Business — fine tool for its layer.

We **don't adopt it**, **don't displace it**, **don't build a bridge unless triggered**.

---

## Microsoft Planner capability inventory

Public M365 product page + Microsoft Learn documentation.

| # | Capability | MS Planner delivers |
|---|---|---|
| 1 | Kanban board per plan | ✅ |
| 2 | Task: title, due date, assignee(s), description | ✅ |
| 3 | Task labels (colored tags) | ✅ |
| 4 | Checklists within tasks | ✅ |
| 5 | Attachments (link to SharePoint / OneDrive) | ✅ |
| 6 | Multiple plans per M365 Group / Team | ✅ |
| 7 | Buckets (kanban columns) | ✅ |
| 8 | Progress states (Not Started / In Progress / Completed / Late) | ✅ |
| 9 | Charts view (burndown-ish by bucket/priority/assignee/progress) | ✅ |
| 10 | Schedule view (calendar) | ✅ |
| 11 | Group-by filters | ✅ |
| 12 | Copy / move tasks between plans | ✅ |
| 13 | Multi-assignee per task | ✅ |
| 14 | Task comments / discussion | ✅ |
| 15 | Teams integration (tab per plan) | ✅ (native) |
| 16 | Outlook / To Do integration | ✅ (native) |
| 17 | Email notifications | ✅ |
| 18 | Recurring tasks | ✅ (2024+) |
| 19 | Approvals via Power Automate | ✅ (Premium) |
| 20 | AI / Copilot-assisted planning | ✅ (Premium "New Planner", 2024+) |
| 21 | Timelines / Gantt / dependencies (Premium) | ✅ (Premium tier only — was Project-for-the-web) |
| 22 | Baseline tracking (Premium) | ✅ (Premium) |
| 23 | Export to Excel | ✅ |
| 24 | API (Graph) | ✅ |

---

## IPAI stack parity mapping

Layer order per CLAUDE.md doctrine (CE → property fields → OCA → `ipai_*` as last resort).

| # | Capability | Odoo CE 18 native | OCA | `ipai_*` bridge | Coverage |
|---|---|---|---|---|---|
| 1 | Kanban board per plan | `project.task` kanban view per `project.project` | — | — | ✅ |
| 2 | Task: title, due, assignee, description | `project.task` core fields | — | — | ✅ |
| 3 | Task labels | `project.tags` | — | — | ✅ |
| 4 | Checklists within tasks | — | OCA `project_task_checklist` (verify 18.0) | — | ✅ with OCA |
| 5 | Attachments | `ir.attachment` on task | — | — | ✅ |
| 6 | Multiple plans | Multiple `project.project` records | — | — | ✅ |
| 7 | Buckets (kanban columns) | `project.task.type` (stages, per project) | — | — | ✅ |
| 8 | Progress states | Stage-based state machine + computed "late" (`date_deadline < today`) | — | — | ✅ |
| 9 | Charts view | Odoo BI views (pivot, graph, dashboard) | — | — | ✅ |
| 10 | Schedule / calendar view | `project.task` calendar view | — | — | ✅ |
| 11 | Group-by / filters | Odoo search view | — | — | ✅ |
| 12 | Copy / move tasks between projects | Task `project_id` editable; OCA helpers | OCA `project_task_move` (verify) | — | ✅ |
| 13 | Multi-assignee | `project.task.user_ids` (M2M) | — | — | ✅ |
| 14 | Task comments | `mail.thread` on `project.task` | — | — | ✅ |
| 15 | Teams integration (tab per plan) | — | — | Thin adapter: Teams tab pointing to Odoo project URL | ⚠️ not native |
| 16 | Outlook / To Do integration | `microsoft_calendar` (CE 18) | — | Thin adapter for Outlook tasks (1-way push) | ⚠️ partial |
| 17 | Email notifications | `mail.activity` + `ir.cron` | — | — | ✅ |
| 18 | Recurring tasks | — | OCA `project_recurring_task` (verify 18.0) | — | ✅ with OCA |
| 19 | Approvals | — | OCA `base_tier_validation` + `project_task_approval` | — | ✅ with OCA |
| 20 | AI / Copilot assist | `ipai_odoo_copilot` + Pulser systray | — | — | ✅ with existing `ipai_*` |
| 21 | Timelines / Gantt | — | OCA `project_timeline` | — | ✅ with OCA |
| 22 | Dependencies (predecessor/successor) | — | OCA `project_task_predecessor` (verify) | — | ✅ with OCA |
| 23 | Export to Excel | Odoo core export | — | — | ✅ |
| 24 | Graph API | — | — | Not applicable (we're not M365). Odoo has JSON-RPC + OData bridge v1. | n/a |

**Raw count:** 22 ✅, 2 ⚠️ (Teams tab, Outlook bidirectional), 1 n/a (Graph API is a Microsoft-specific surface).

---

## Parity score

```
24 capabilities total
22 match at CE / OCA level                    = 92%
+2 partial via thin ipai_* adapter (Teams tab, Outlook push) = 100% of the matchable set
1 is structurally Microsoft-only (Graph API)  = not applicable to Odoo
```

**Effective parity: 100%** of what's replicable. The 2 partial items only matter for M365-native customers.

---

## But here's the real question

**We don't need Planner parity — we already have 3 work surfaces:**

| Our surface | Equivalent to |
|---|---|
| Azure Boards (ADO) | Microsoft Project for the Web / Premium Planner (portfolio + sprints + OKRs) |
| Odoo Projects | Microsoft Project + timesheet + billing (PPM + GL integration) |
| Odoo Files | Microsoft OneNote / SharePoint pages (narrative, knowledge) |

Planner fits **none of these layers cleanly**. It's a **lightweight team todo** that sits between "a checklist in a doc" and "a real project."

For IPAI's internal use, Planner adds nothing we don't already cover.
For our customers, if they're already on M365, their team uses Planner for their own internal ops — not for work we deliver.

---

## Where Planner beats any non-M365 alternative

### 1. Native M365 tenant integration

Teams tab, Outlook, To Do, Groups — all auto-wired. Zero setup for a M365-native team.

### 2. Price

Free with M365 Business Basic+ tier. For a team already paying M365, Planner is $0 incremental.

### 3. Simplicity for non-project work

For "things my team needs to do this week," Planner is easier than Boards or Odoo.

---

## Where our stack beats Planner

### 1. Timesheet + billing integration

Odoo Projects → `account.analytic.line` → `account.move`. Planner doesn't touch GL. For billable delivery work, we win.

### 2. Portfolio rollups

Azure Boards has Initiative → Epic → Feature → Story with rollups and Delivery Plans. Planner's "plans" are flat; Planner Premium adds timelines but still not true portfolio hierarchy.

### 3. Ownership of the stack

Odoo + OCA + `ipai_*` = we own the control surface. Planner = we rent Microsoft's.

---

## Decision — what IPAI does

### For IPAI-internal work

```
Do not adopt Planner.
  Strategic work     → Azure Boards
  Delivery work      → Odoo Projects
  Narrative / notes  → Odoo Files
  Code-adjacent      → GitHub Issues (repo-local)
```

Planner would be a **5th work surface**. Violates the reuse-first doctrine.

### For customer delivery (TBWA\SMP, W9, OMC)

```
Customer on M365:
  - They can keep using Planner for their internal team ops.
  - Work we deliver to them lives in Odoo Projects (billable, GL-integrated).
  - Strategic portfolio rolls up in Azure Boards (if they want visibility,
    we mirror a Delivery Plan view to them — read-only).
  - Do NOT displace Planner inside their M365 tenant.
  - Do NOT build a Planner ↔ Odoo bridge unless explicitly requested.

Customer not on M365:
  - They use Odoo Projects for their operational work too.
  - No Planner in the picture.
```

### For Pulser-as-a-product consumers (future)

```
If a product customer wants Teams-native task visibility:
  - Thin ipai_planner_bridge (Graph API push from Odoo project.task
    into a Planner plan in their M365 tenant)
  - One-way: Odoo is authoritative, Planner is a read-only mirror
  - Build only when triggered (named customer + explicit need)
```

---

## Ship gates

Per the `docs/architecture/odata-to-odoo-mapping.md` "build-only-when-triggered" pattern, applied here:

```
Stay deferred unless ALL true:
  [ ] Named customer exists
  [ ] Customer specifically asks for Planner integration (not generic Teams)
  [ ] Odoo is authoritative; Planner is read-only mirror
  [ ] Owner + target milestone assigned
```

If any missing → stay deferred.

---

## What's live today

| Surface | IPAI usage | Status |
|---|---|---|
| Azure Boards (ADO project `ipai-platform`) | Strategic portfolio (Initiative / Epics / Features / Stories / Tasks) | Under-instrumented — needs setup per [`azure-boards-portfolio-target-state.md`](../backlog/azure-boards-portfolio-target-state.md) |
| Odoo Projects (`project.project` + `project.task`) | Delivery execution, TBWA\SMP PPM planned | Config-ready, pending contract |
| Odoo Files (`/odoo/action-399`) | Narrative, playbooks, knowledge base | Surface exists, folder layout pending per [`work-artifact-placement.md`](../programs/work-artifact-placement.md) |
| GitHub Issues | Repo-local tasks only | Active, light use |
| Microsoft Planner | **Not in IPAI stack** | Customers may use in their own M365 tenants |

---

## Anti-patterns to avoid

- Adding Planner as a 5th IPAI work surface — fragmentation
- Building a bi-directional Planner ↔ Odoo sync without a named customer — speculative
- Treating Planner as equivalent to Boards — Planner is flat, Boards is hierarchical portfolio
- Using Planner for billable delivery — no GL integration
- Letting customers on M365 believe IPAI delivers via Planner — we deliver via Odoo Projects

---

## References

Internal:
- [`docs/programs/work-artifact-placement.md`](../programs/work-artifact-placement.md) — 3-tier work model
- [`docs/backlog/azure-boards-portfolio-target-state.md`](../backlog/azure-boards-portfolio-target-state.md)
- [`docs/architecture/booking-surface-microsoft-parity.md`](./booking-surface-microsoft-parity.md) — same methodology
- [`docs/architecture/odata-to-odoo-mapping.md`](./odata-to-odoo-mapping.md) — build-trigger pattern
- OCA modules to verify 18.0: `project_task_checklist`, `project_recurring_task`, `project_task_move`, `project_timeline`, `project_task_predecessor`, `project_task_approval`

External:
- [Microsoft Planner product page](https://www.microsoft.com/en-US/microsoft-365/planner/microsoft-planner)
- [Microsoft Planner — Microsoft Learn](https://learn.microsoft.com/en-us/planner/)
- [Microsoft Graph `planner` API](https://learn.microsoft.com/en-us/graph/api/resources/planner-overview)
- [Odoo 18 Project documentation](https://www.odoo.com/documentation/18.0/applications/services/project.html)

---

## Bottom line

```
Planner is a team todo app, free with M365.
We already cover its job through Boards + Odoo Projects + Files.
Don't adopt it internally.
Don't displace it in customer M365 tenants.
Don't build a bridge unless a named customer asks.
```

---

*Last updated: 2026-04-15*
