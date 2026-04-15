# Work Artifact Placement — Where Does What Go

> **Locked:** 2026-04-15
> **Doctrine:** Not every artifact needs to be a project. Page surfaces (wiki-like) exist for a reason.
> **Anchors:**
> - Azure Boards: [`docs/backlog/azure-boards-portfolio-target-state.md`](../backlog/azure-boards-portfolio-target-state.md)
> - Odoo Projects: OCA `project-*` + core CE 18
> - Odoo Files / pages: `/odoo/action-399` (Files app — notion-like page surface)

---

## Three-tier placement model

```
Tier 1: Azure Boards (ADO)       → portfolio, OKRs, sprints, dependencies, reporting
Tier 2: Odoo Projects + Tasks    → delivery execution, PPM, time tracking, billing
Tier 3: Odoo Files / pages       → knowledge, meeting notes, wikis, program charters
```

**Not everything goes in Tier 1 or Tier 2.** Much lives in Tier 3.

---

## Decision rule (what lives where)

| Artifact | Tier | Why |
|---|---|---|
| Program charter (1 page narrative) | **Tier 3** (Odoo Files) | It's a document, not a deliverable |
| OKR source of truth (the plan) | **Tier 3** (Odoo Files) or git | Narrative + long-lived |
| OKR scoring log (monthly entries) | **Tier 3** (Odoo Files appended) | Append-only log |
| Epic / Feature / Story / Task work | **Tier 1** (Boards) | Has state, sprint, owner, deps |
| Project delivery work (who does what by when, billable) | **Tier 2** (Odoo Projects) | PPM + timesheet + GL |
| Recurring compliance tasks (monthly BIR, close) | **Tier 2** (Odoo Projects, instantiated from template) | Has real task execution |
| Milestones | **Tier 1** (Boards Feature with `milestone_id:` tag) | Schedule control authority |
| Risks register | **Tier 3** (Odoo Files, with cross-link to Boards Stories) | Mostly narrative, some linked |
| Meeting notes | **Tier 3** (Odoo Files) | Narrative; not trackable work |
| Architecture / doctrine docs | **git repo** (`docs/`) | Version-controlled, reviewed via PR |
| SSOT configs (BOM, tagging, tenants) | **git repo** (`ssot/`) | Code-reviewed truth |
| Seed data specs | **git repo** (`ssot/tenants/*/seed/`) | Committed before population |
| Knowledge base / FAQ / playbooks | **Tier 3** (Odoo Files) | Living pages, not sprints |
| Customer-facing runbooks / handoff docs | **Tier 3** (Odoo Files) | Delivered as attachments |

---

## Tier 3 — Odoo Files (the notion-like surface)

Accessed at `/odoo/action-399` in the Odoo UI. Module: `documents` (CE 18) + OCA extensions.

**Use for:**
- Long-lived narrative (charters, OKRs-as-document, operating playbooks)
- Per-client working binder (TBWA\SMP, OMC, W9 each get a folder)
- Per-program knowledge (lessons learned, retros, post-mortems)
- Meeting notes, whiteboard snapshots, brief decks
- Appended logs (monthly OKR scoring, weekly status reports)
- Templates that get instantiated (BIR filing templates, close checklists)

**Do NOT use for:**
- Anything with state transitions (that's Boards or Odoo Projects)
- Anything with sprint planning (Boards)
- Anything with a billable timesheet line (Odoo Projects)
- Code / configuration (git repo)

---

## Tier 3 — folder layout (recommended)

```
Odoo Files (/odoo/action-399)
├── Programs/
│   ├── TBWA\SMP Finance Transformation/
│   │   ├── Charter.md         ← text version of program charter
│   │   ├── OKR Plan.md         ← living narrative (mirrors git doc)
│   │   ├── Scoring Log.md      ← appended monthly
│   │   ├── Meeting Notes/
│   │   │   ├── 2026-04-15 kickoff.md
│   │   │   └── ...
│   │   ├── Retros/
│   │   └── Handoff Docs/
│   ├── W9 Studio — Booking Launch/
│   └── Internal — IPAI Platform Buildout/
├── Playbooks/
│   ├── Monthly Close Playbook.md
│   ├── BIR Filing Playbook — 1601-C.md
│   ├── BIR Filing Playbook — 2550-M.md
│   └── ...
├── Knowledge Base/
│   ├── PH Tax / BIR Reference.md
│   ├── Odoo Configuration Notes.md
│   ├── OCA Module Evaluations.md
│   └── ...
└── Client Binders/
    ├── TBWA\SMP/        ← scoped to company_id=4 access
    ├── OMC/
    └── W9/
```

---

## The cross-link discipline

Every Tier 3 document that matters carries:
- **Link to its Tier 1 equivalent** (if a Boards Epic/Feature exists)
- **Link to its Tier 2 equivalent** (if an Odoo Project exists)
- **Link to its git source** (if the narrative originates in `docs/`)

Tier 3 is not a silo. It's the narrative + knowledge surface that points at the trackable work.

Example (TBWA\SMP):
```
Odoo Files: Programs/TBWA\SMP Finance Transformation/Charter.md
  ↘ links to Boards: Epic "Core Operations Plane" + Feature "TBWA\SMP ERP Displacement"
  ↘ links to Odoo Project: project.project "TBWA\SMP — FY2026"
  ↘ links to git: docs/programs/tbwa-smp-finance-program.md
```

---

## Who edits what

| Surface | Primary editors |
|---|---|
| Tier 1 (Boards) | Delivery team; PMs update state, engineers update tasks |
| Tier 2 (Odoo Projects) | Delivery team; finance updates billables |
| Tier 3 (Odoo Files) | Anyone with scope — CFO writes OKRs, eng writes playbooks, client reads handoffs |
| git repo | Engineering + architects; PR-reviewed |

Tier 3 is the **most permissive surface**. That's the point — it's the notion-equivalent where people write instead of fighting Boards fields.

---

## Anti-patterns

- Forcing a 1-page program charter into a Boards Epic — loses the narrative
- Making every meeting note into a Boards Issue — pollutes the backlog
- Storing a recurring playbook as a git doc only — finance team never looks at git
- Keeping OKRs only in a Boards custom field — no narrative history
- Letting Tier 3 (Files) become the source of truth for state-ful work — use Boards / Odoo Projects instead

---

## Migration note — for existing docs

Some things I've written as full git docs should probably live as Tier 3 (Files) copies for the finance/client audience:

| Git doc (stays) | Also publish to Tier 3? |
|---|---|
| `docs/programs/tbwa-smp-finance-program.md` | Yes — as "TBWA\SMP OKR Plan" in Files (narrative copy) |
| `docs/programs/_PROGRAM_OKR_TEMPLATE.md` | Yes — as "Program OKR Template" playbook |
| `docs/backlog/ph-close-bir-compliance-board-pack.md` | Partial — each Feature's playbook as a Tier 3 page |
| `ssot/tenants/tbwa-smp/seed/ppm_tasks.yaml` | No — stays in git (config-as-code) |
| `docs/architecture/*` | No — architects read git, not Files |
| `docs/ops/azure-boards-*.md` | Yes — as operator playbooks |

The git copy stays canonical. Tier 3 gets a rendered / narrative version for humans who don't read markdown in a repo.

---

## Bottom line

```
Tier 1 — Boards         → state, sprints, deps, OKRs as trackable work
Tier 2 — Odoo Projects  → delivery execution, timesheet, billing
Tier 3 — Odoo Files     → narrative, knowledge, playbooks, meeting notes
Tier git — doctrine     → architecture, SSOT, configs, seeds
```

**Don't force a narrative into a sprint. Don't force a task into a page. Put each artifact where it naturally lives.**

---

*Last updated: 2026-04-15*
