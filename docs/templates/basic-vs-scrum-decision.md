# Azure Boards Process Decision — Basic vs Scrum for `ipai-platform`

> Which Azure Boards process fits IPAI's operating model? Short answer: **Basic
> is the right fit for a lean founder-led team; Scrum only if formal product-
> management ceremony is needed.** Current project state is Scrum — migration
> path optional, not required.

---

## Current state (2026-04-18)

- ADO project: `dev.azure.com/insightpulse/ipai-platform`
- Process: **Scrum** (per project settings screenshot)
- Backlog: effectively empty (no Epics seeded yet)
- Team size: 5-9 people, founder-led, repo/spec-driven execution

## Process comparison

| | **Basic** | **Scrum** (current) | **Agile** | **CMMI** |
|---|---|---|---|---|
| Hierarchy | Epic → Issue → Task | Epic → Feature → PBI → Task | Epic → Feature → User Story → Task | Epic → Feature → Requirement → Task |
| Requirement name | Issue | PBI | User Story | Requirement |
| Blocker name | Issue | Impediment | Issue | Issue |
| States | To Do → Doing → Done | New → Approved → Committed → Done → Removed | New → Active → Resolved → Closed → Removed | Proposed → Active → Resolved → Closed |
| Estimation | Remaining Work (hours) | Effort (story points relative) | Story Points | Size |
| Ceremony | Lowest | Medium | Medium-high | Highest |
| Best for | Small teams, lean execution | Scrum teams with sprints + velocity | Product teams with user stories | Regulated / audited environments |

## When Basic wins

Use **Basic** if:
- Team is small (≤10 people)
- Execution is founder-led, repo-first, spec-driven
- You don't run formal sprint ceremony (planning, review, retro)
- You want minimum overhead between idea → code → ship
- Your agents/copilots do the heavy lifting; humans orchestrate

This matches IPAI's current model:
- 5-9 people
- Single decision-maker (Jake)
- Spec bundles in `spec/` already define work scope
- Repo-level PRs and Azure Pipelines gate merges
- No formal sprint cadence — shipping on marketplace target dates

## When Scrum wins

Use **Scrum** if:
- Team is large enough for dedicated Scrum Master + Product Owner roles
- You run formal 2-week sprints with velocity tracking
- You need explicit Feature layer for cross-PBI capability rollup
- Multiple teams work in parallel and need portfolio-level views
- You want PBI-level estimation + burndown ceremony

IPAI isn't there yet. Team is too small for the ceremony to pay back the overhead.

## Recommendation — stay on Scrum, don't migrate

Even though Basic would be a cleaner fit for IPAI's current model, **migration
effort isn't worth the benefit** now. Reasons:

1. **No work items lost.** Current Scrum project has effectively empty backlog; switching processes would reset any existing items anyway.
2. **Scrum allows Basic-style discipline.** You can use only Epic + PBI + Task (ignore Features) and effectively operate as Basic-equivalent with extra PBI-state granularity.
3. **PBI is a more precise name than "Issue."** For Pulser's product focus, PBI reads better to Microsoft sellers ("backlog item") than "issue."
4. **Scrum's Effort field (relative points)** is more aligned with AI-assisted estimation than hour-counting.
5. **Marketplace ISV context** — Microsoft sellers expect to see Scrum or Agile semantics, not Basic (which signals "early stage / ad hoc").

## Operating rule for Scrum on `ipai-platform`

Keep Scrum, but operate with Basic-like discipline:

| Work item | Use | Don't use |
|---|---|---|
| Epic | Portfolio-level initiatives (9 capability areas) | Feature-level scope |
| Feature | **Skip at first.** Add later only if an Epic needs decomposition. | Every Epic (avoid the Feature tax) |
| PBI | Bounded backlog items, one deliverable each | Tasks-as-PBIs (too granular) |
| Task | Implementation work under a PBI | Everything (don't put Epics here) |
| Bug | Defects against existing behavior | Feature requests (those are PBIs) |
| Impediment | Hard blockers | Soft risks (comment on the PBI instead) |

Effective hierarchy: **Epic → PBI → Task** (Feature skipped unless needed).

## Mapping from Basic → Scrum (if you migrate another project)

If you ever create another ADO project on Basic and later migrate:

```
Basic              →  Scrum
─────────────────────────────────
Epic               →  Epic
Issue              →  Product Backlog Item (PBI)
Task               →  Task
(no equivalent)    →  Feature (optional, skip)
(no equivalent)    →  Impediment (use Bug for blockers instead)
(no equivalent)    →  Test Case / Test Plan (optional)

State mapping:
  To Do            →  New
  Doing            →  Committed
  Done             →  Done
  (no equivalent)  →  Approved (intermediate planning state)
  (no equivalent)  →  Removed (replaces delete)
```

Azure DevOps has an automated migration wizard but it's safer to export to CSV
and re-import once state transitions are explicit.

## Practical Pulser examples in Scrum

**Epic — Portfolio initiative:**
```
Title: Wave 1 — Pulser SaaS Marketplace GTM
Description: Transactable SaaS offer publish Aug-Sep 2026.
Spec bundle: spec/microsoft-marketplace-gtm/
Tags: marketplace, wave-1, gtm
Priority: 1
```

**PBI — Deliverable within Epic:**
```
Title: Implement SaaS fulfillment API subscribe webhook
Description: [business rule + acceptance criteria]
Parent Epic: AB#[Epic ID]
Spec bundle task: spec/microsoft-marketplace-gtm/tasks.md — EPIC 2.2
Tags: marketplace, saas-api, wave-1
Effort: 5 (relative)
Priority: 1
```

**Task — Implementation step:**
```
Title: Add webhook endpoint route in Odoo controller
Parent PBI: AB#[PBI ID]
Target repo: Insightpulseai/odoo
Branch: feature/ab<id>-webhook-route
Remaining Work: (optional, in hours if tracked)
```

## Decision summary

```
Stay on Scrum (current state).
Operate as Epic → PBI → Task (skip Features).
Add Features only when an Epic genuinely needs capability-level grouping.
Keep Basic in mind as fallback — but migration effort isn't worth the benefit.
```

## References

- `docs/templates/ado-copilot-work-item.md`
- `docs/templates/repo-to-boards-contract.md`
- `docs/architecture/plane-separation.md`
- [Microsoft — Choose a process](https://learn.microsoft.com/en-us/azure/devops/boards/work-items/guidance/choose-process)
- [Microsoft — Scrum process](https://learn.microsoft.com/en-us/azure/devops/boards/work-items/guidance/scrum-process)
