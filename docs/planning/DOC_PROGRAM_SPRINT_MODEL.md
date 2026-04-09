# Documentation Program — Sprint Operating Model

> Sprint cadence, ceremonies, and Definition of Done for the Odoo-on-Azure documentation program.
> Aligned to Azure Boards Agile process and the doc-program backlog.

---

## Sprint Cadence

| Parameter | Value |
|---|---|
| Sprint length | 2 weeks |
| Iteration path root | `ipai-platform\Docs\*` |
| Iteration phases | Foundation → Wave-1 → Wave-2 → Hardening |
| Board process | Agile (Epic → Feature → User Story → Task) |
| Planning tool | Azure Boards |
| Implementation tool | GitHub (branches, PRs, merge commits) |

---

## Ceremonies

### Sprint Planning

| Item | Detail |
|---|---|
| When | Day 1 of sprint, 60 min |
| Who | All team leads (ipai-docs, ipai-platform-control, ipai-infra, ipai-odoo-runtime, ipai-agents, ipai-data-intelligence) |
| Input | Refined backlog, Feature priority, dependency tags |
| Output | Sprint backlog with committed Stories and Tasks |
| Rule | Every committed Story must have an Area Path, Iteration Path, and acceptance criteria before entering the sprint |

### Daily Scrum

| Item | Detail |
|---|---|
| When | Daily, 15 min (async-first — Slack thread if synchronous is impractical) |
| Who | Active contributors |
| Format | What shipped yesterday → what ships today → blockers |
| Rule | Blockers must reference the Azure Boards work item ID |

### Sprint Review

| Item | Detail |
|---|---|
| When | Last day of sprint, 30 min |
| Who | All team leads + stakeholders |
| Format | Demo shipped docs, walk through evidence, show Boards rollup |
| Rule | Stories without evidence are not demoed — they are moved back to backlog |

### Sprint Retrospective

| Item | Detail |
|---|---|
| When | After sprint review, 30 min |
| Who | All team leads |
| Output | 1-3 actionable improvements, captured as Tasks in the next sprint |
| Rule | At least one improvement must address process, not just content |

---

## Definition of Done (DoD)

A User Story is "Done" only when ALL of the following are true:

### For `WRITE:` Stories
- [ ] Document exists at the canonical path declared in the Story
- [ ] Document follows the doc-authority model (`docs/odoo-on-azure/reference/doc-authority.md`)
- [ ] Cross-links to related docs exist
- [ ] PR is merged with `Resolve AB#<id>` in the commit message
- [ ] No broken relative links

### For `EVIDENCE:` Stories
- [ ] Evidence artifact exists in `docs/evidence/<YYYYMMDD-HHMM>/<scope>/`
- [ ] Evidence validates the specific claim (not a generic "looks good")
- [ ] PR is merged with `Validate AB#<id>` in the commit message

### For `INDEX:` Stories
- [ ] Index page exists and links to canonical locations
- [ ] Navigation from the central `docs/odoo-on-azure/` tree reaches the target
- [ ] PR is merged with `Resolve AB#<id>` in the commit message

### For all Stories
- [ ] Azure Boards work item is updated to Closed
- [ ] Build status is linked on the work item (YAML build pipeline)

---

## Recommended First 3 Sprints

### Sprint 1 — Foundation

**Iteration:** `ipai-platform\Docs\Foundation`

**Goals:**
- Publish `docs/odoo-on-azure/README.md` and overview family
- Publish workload-center index and OSI model page
- Publish doc-authority model and benchmark map
- Establish Azure Boards Epic/Feature hierarchy for all 5 targets
- Confirm Area Path ownership for every Feature

**Exit criteria:**
- Navigation from `docs/odoo-on-azure/` reaches all planned sections (even if stubs)
- Azure Boards shows 5 Epics, all Features created, Foundation Stories committed

### Sprint 2 — Wave-1

**Iteration:** `ipai-platform\Docs\Wave-1`

**Goals:**
- Publish monitoring, deployment-automation, and runtime doc families
- Publish integration playbooks (Entra, Key Vault, AI Foundry)
- First evidence pass: validate live inventory against doc claims

**Exit criteria:**
- All Wave-1 Features have at least one merged Story with evidence
- No unresolved dependency tags blocking Wave-2

### Sprint 3 — Wave-2 (start)

**Iteration:** `ipai-platform\Docs\Wave-2`

**Goals:**
- Publish AI platform, engineering, and data-intelligence index pages
- Author Foundry control-plane and retrieval docs
- Author spec-driven development and agent-assisted delivery docs
- Author lakehouse and governance docs

**Exit criteria:**
- All three benchmark families (AI, engineering, data) have published index pages
- Cross-links between workload, AI, engineering, and data families exist

---

## Backlog Refinement

| Parameter | Value |
|---|---|
| Frequency | Weekly, 30 min |
| Input | Unrefined Stories in the backlog |
| Output | Stories with acceptance criteria, Area Path, estimate, and dependency tags |
| Rule | Stories without acceptance criteria cannot enter a sprint |

### Refinement checklist

- [ ] Story has a clear `WRITE:`, `EVIDENCE:`, or `INDEX:` prefix
- [ ] Canonical file path is specified
- [ ] Acceptance criteria reference observable output
- [ ] Area Path matches the owning team
- [ ] Dependency tags are set if cross-team
- [ ] Effort estimate is set (Story Points or T-shirt size)

---

## Related Documents

- [DOC_PROGRAM_BACKLOG.md](DOC_PROGRAM_BACKLOG.md) — full backlog hierarchy
- [DOC_PROGRAM_SCALING.md](DOC_PROGRAM_SCALING.md) — multi-team scaling model
- [DOC_PROGRAM_WORK_ITEM_TEMPLATES.md](DOC_PROGRAM_WORK_ITEM_TEMPLATES.md) — work-item templates
- [DOC_PROGRAM_IMPORT.csv](DOC_PROGRAM_IMPORT.csv) — Azure Boards CSV import

---

*Created: 2026-04-05 | Version: 1.0*
