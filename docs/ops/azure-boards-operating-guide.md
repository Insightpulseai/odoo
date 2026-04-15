# Azure Boards Operating Guide — IPAI Platform

> **Locked:** 2026-04-15
> **Project:** `insightpulseai/ipai-platform` (per memory `reference_azdo_org_project.md`)
> **Paired with:** [`docs/backlog/az400-devops-platform-learning-board-pack.md`](../backlog/az400-devops-platform-learning-board-pack.md) (10 Epics / 110 Issues)
> **Source refs:**
> - [Work item quick reference](https://learn.microsoft.com/en-us/azure/devops/boards/work-items/quick-ref?view=azure-devops)
> - [Mobile work](https://learn.microsoft.com/en-us/azure/devops/project/navigation/mobile-work?toc=%2Fazure%2Fdevops%2Fboards%2Ftoc.json&view=azure-devops)

---

## 1. Work item taxonomy (IPAI-locked)

Agile process template. Hierarchy depth 4.

```
Initiative     → Epic → Feature → User Story / Task / Bug
```

| Type | IPAI usage | States (canonical) |
|---|---|---|
| **Initiative** | Program-level (e.g. "Azure-native delivery hardening") | Active → Closed |
| **Epic** | Cross-quarter outcome (1–3 Sprints cover it) | New → Active → Resolved → Closed |
| **Feature** | Deliverable inside an Epic | New → Active → Resolved → Closed |
| **User Story** | Functional slice shippable in a Sprint | New → Active → Resolved → Closed |
| **Task** | Sub-work inside a Story | To Do → Doing → Done |
| **Bug** | Defect; can live under Story or at Feature level | New → Active → Resolved → Closed |
| **Test Case** | Only for surfaces where Test Plans are on | Design → Ready → Closed |

---

## 2. Required fields (enforced on save)

Every work item must have:

| Field | Rule | Why |
|---|---|---|
| **Title** | ≤ 70 chars, imperative mood | Mobile cards truncate fast |
| **Assigned To** | Exactly one person; empty only if unscheduled | Single owner per item |
| **State** | See table above | Board column derivation |
| **Area Path** | IPAI-scoped, matches the plane (e.g. `\ipai-platform\agent`, `\odoo`, `\web`, `\data-intelligence`) | Policy scoping |
| **Iteration Path** | Matches active sprint or `Backlog` | Sprint capacity |
| **Tags** | Minimum: `{environment:dev\|staging\|prod}`, `{plane:transaction\|agent\|data-intelligence\|platform\|observability\|network\|shared}` — mirrors [`ssot/azure/tagging-standard.yaml`](../../ssot/azure/tagging-standard.yaml) | FinOps + plane routing |
| **Priority** | 1 (blocker) / 2 (P0) / 3 (P1) / 4 (P2) | Board ordering |
| **Story Points** (Story only) | Fibonacci: 1, 2, 3, 5, 8, 13 | Sprint capacity |

Optional but encouraged: **Acceptance Criteria** on every Story; **Repro Steps** on every Bug.

---

## 3. Iteration cadence

```
Sprint length:   2 weeks
Sprint starts:   Monday 00:00 Asia/Manila
Sprint ends:     Friday 23:59 Asia/Manila (week 2)

Cadence rituals:
  Sprint planning   — Monday week 1, 60 min
  Daily stand-up    — asynchronous in Azure Boards (update "What I did" field)
  Sprint review     — Friday week 2, 30 min
  Sprint retro      — Friday week 2, 30 min (immediately after review)
```

Active iteration is always visible on the mobile home screen.

---

## 4. Mobile work patterns

Per the [Mobile work](https://learn.microsoft.com/en-us/azure/devops/project/navigation/mobile-work?toc=%2Fazure%2Fdevops%2Fboards%2Ftoc.json&view=azure-devops) doc.

### Mobile is for:
- Triaging the day's active work items
- State transitions (New → Active → Resolved)
- Adding comments / attaching screenshots
- Approving PRs linked from work items
- Quick status checks on epics/features

### Mobile is NOT for:
- Sprint planning (use desktop web)
- Bulk operations (use desktop web or CLI)
- Query authoring (use desktop web)
- Rich-text editing with formatting (use desktop web)

### Mobile URL pattern:
```
https://dev.azure.com/insightpulseai/ipai-platform/_workitems
```

Opens the "My Work" view with: **My Activity**, **Following**, **Mentioned**.

### Mobile shortcuts:
- Tap an item → detail view with tabs: **Details / History / Links / Attachments**
- Swipe right on a card → state forward (To Do → Doing → Done)
- Swipe left on a card → state backward or Discard
- Pull down → refresh queries

---

## 5. Desktop work patterns (keyboard shortcuts)

| Shortcut | Action |
|---|---|
| `g, b` | Go to Backlogs |
| `g, w` | Go to Work Items |
| `g, q` | Go to Queries |
| `g, i` | Go to Iteration (sprint board) |
| `n` | New work item |
| `/` | Focus search |
| `.` | Open command palette |
| `Alt+Enter` | Save + close |
| `Alt+O` | Save |
| `Ctrl+S` | Save (in form) |

---

## 6. Standard queries (pinned)

Create these once in the "Shared Queries" folder. Every IPAI team member pins them.

| Query name | Definition |
|---|---|
| **My Active** | `AssignedTo = @Me AND State IN (Active, Doing)` |
| **My Sprint** | `AssignedTo = @Me AND IterationPath = @CurrentIteration` |
| **My Bugs** | `AssignedTo = @Me AND WorkItemType = Bug AND State <> Closed` |
| **Team Active** | `State IN (Active, Doing) AND IterationPath = @CurrentIteration` |
| **Blocked** | `Tags CONTAINS 'blocked' AND State <> Closed` |
| **Unassigned Active** | `AssignedTo IS EMPTY AND State = Active` |
| **This Week's Closed** | `State = Closed AND ChangedDate >= @Today - 7` |
| **Epic Progress** | `WorkItemType = Epic AND State <> Closed` (pivot by Feature child count) |

---

## 7. Bulk operations (from CLI)

Azure DevOps MCP + `az boards` CLI path for bulk work.

```bash
# List all active items assigned to me
az boards query --wiql "SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.AssignedTo] = @Me AND [System.State] = 'Active'"

# Bulk create 110 Issues from az400-devops-platform-learning-board-pack.md (future script)
scripts/azdo/bulk-create-from-backlog.sh docs/backlog/az400-devops-platform-learning-board-pack.md

# Bulk state transition (e.g., close all Issues in Feature-XYZ)
az boards work-item update --id <id> --state Closed
```

Future: wire this to `.github/prompts/` Copilot Coding Agent so issues can be drafted from user-story statements.

---

## 8. Tag hygiene (mirrors Azure tagging standard)

Every work item carries the 2 mandatory tags:
- `environment:<dev|staging|prod>`
- `plane:<transaction|agent|data-intelligence|platform|observability|network|shared>`

Plus context tags:
- `blocked` — when work is blocked (pair with a comment naming the blocker)
- `needs-review` — when waiting on PR review
- `waiting-on-customer` — when external action needed
- `policy-exception` — when requires an Azure Policy exemption
- `debt` — technical debt item

---

## 9. Link types (enforced)

Every work item should link:

| Link | When | Why |
|---|---|---|
| **Parent** | Always | Maintains hierarchy Initiative→Epic→Feature→Story |
| **Related** | Cross-cutting dependency | Shows dependencies on other items |
| **Blocks / Blocked by** | Hard dependency | Sprint planning awareness |
| **GitHub Pull Request** | When code ships | Closes item on merge |
| **GitHub Commit** | Mid-work | Traceability |
| **Azure Pipelines Build** | CI run | Evidence capture |

---

## 10. Mobile-first checklist (for every work item)

Before saving an item on desktop, ask: **Will this be usable on mobile?**

- [ ] Title ≤ 70 chars and stands alone
- [ ] Description has a 1-line summary on top (rest is detail)
- [ ] Acceptance Criteria is a bullet list (not prose)
- [ ] Attachments have alt text / captions
- [ ] Links use descriptive text (not "click here")
- [ ] Priority set (mobile orders by priority)

---

## 11. Pairing with the AZ-400 backlog

The [`docs/backlog/az400-devops-platform-learning-board-pack.md`](../backlog/az400-devops-platform-learning-board-pack.md) has 110 Issues. To actually execute:

1. **Create the Initiative** at the top level (manual, once).
2. **Bulk-create 10 Epics** under it.
3. **Bulk-create 26 Features** under the Epics.
4. **Bulk-create 110 Issues** under the Features.
5. **Assign Area Paths** per plane (most of Epic 3 → `\odoo`, Epic 5 → `\platform`, Epic 7 → `\observability`, etc.).
6. **Tag** each with `environment:dev` + `plane:<lane>`.
7. **Schedule** into 4 Sprints per the sprint cut in the backlog doc.

See recommended script at [`scripts/azdo/bulk-create-from-backlog.sh`](../../scripts/azdo/bulk-create-from-backlog.sh) (to be authored).

---

## 12. Anti-patterns

- **500-char titles** — unreadable on mobile
- **10-level nested parents** — hierarchy depth 4 is the limit
- **Multiple assignees** — one accountable owner only
- **Missing Iteration Path** — work evaporates into `Backlog` with no owner of timing
- **Bulk-closing without comment** — loses the "why"
- **State jumps backwards without a comment** — confuses history
- **Using Issues to track "ideas"** — use the Backlog explicitly, not a half-completed Issue

---

## References

- [Work items quick reference](https://learn.microsoft.com/en-us/azure/devops/boards/work-items/quick-ref?view=azure-devops)
- [Mobile work in Azure DevOps](https://learn.microsoft.com/en-us/azure/devops/project/navigation/mobile-work?toc=%2Fazure%2Fdevops%2Fboards%2Ftoc.json&view=azure-devops)
- [`docs/backlog/az400-devops-platform-learning-board-pack.md`](../backlog/az400-devops-platform-learning-board-pack.md) — canonical backlog pack
- [`ssot/governance/platform-authority-split.yaml`](../../ssot/governance/platform-authority-split.yaml) — ADO Boards = portfolio authority
- [`ssot/governance/ci-cd-authority-matrix.yaml`](../../ssot/governance/ci-cd-authority-matrix.yaml) — Azure Pipelines = delivery

---

*Last updated: 2026-04-15*
