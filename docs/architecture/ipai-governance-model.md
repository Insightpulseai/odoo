# IPAI Governance Model — One-Page Overlay

> Unifies VMOKRAPI-SPATRES (strategy) + PRINCE2 (delivery governance) + Spec Kit
> (spec-first execution) + Azure Boards (planning) + GitHub (code) + Azure
> DevOps Analytics/Power BI (reporting) + Odoo CE/OCA 18 (business ops).
> This is the final layer in the ipai-platform operating doctrine.

---

## The 5-layer stack

```
Strategy layer     VMOKRAPI-SPATRES            docs/strategy/ + SSOT yaml
    ↓ informs
Governance layer   PRINCE2 stages + controls   docs/governance/ + stage gates
    ↓ controls
Planning layer     Azure Boards (ipai-platform)  Epic → PBI → Task
    ↓ decomposed from
Spec layer         Spec Kit (repo-local)       spec/<slug>/ bundles
    ↓ implemented in
Code layer         GitHub (Insightpulseai org) PRs linked via AB#
    ↓ reported via
Reporting layer    ADO Analytics → Power BI    portfolio + delivery + traceability
    ↓ separate from
Business ops       Odoo CE/OCA 18              actual records + transactions
```

---

## Crosswalk — what each layer answers

| Question | Answered by |
|---|---|
| What are we trying to achieve? | VMOKRAPI-SPATRES (Vision → Strategies → Programs) |
| Why does this matter? How is it justified? | PRINCE2 Business Case |
| How is delivery governed and gated? | PRINCE2 stages + release gates |
| What's the canonical feature definition? | Spec Kit (`spec/<slug>/constitution.md` + PRD + plan + tasks) |
| What's in the delivery backlog? | Azure Boards (Epic → PBI → Task) |
| Who owns it? What's blocked? | Azure Boards (Area Path, State, Impediment) |
| What code changed? What CI passed? | GitHub + Azure Pipelines (AB#-linked) |
| How are we progressing vs roadmap? | ADO Analytics → Power BI |
| What actually happened in the business? | Odoo (`account.move`, `project.task`, DMS, etc.) |

---

## Crosswalk table

| VMOKRAPI-SPATRES | PRINCE2 | Azure Boards | GitHub/CI | Odoo CE/OCA 18 |
|---|---|---|---|---|
| Vision | Project Mandate | Epic narrative | Org charter docs | Business operating target |
| Mission | Business Case | Epic description | README / ARCH docs | Operating model |
| Objectives | Benefits / tolerances | Epics | Release goals | Business outcomes |
| KRAs | Themes | Area paths | Repo ownership | Company / queue ownership |
| Performance Indicators | Progress / quality | Dashboards + OData | CI checks | KPI reports |
| Strategies | Stage approach | Large PBIs | Roadmap branches | Module design choices |
| Programs | Stage grouping | Epic streams | Milestone grouping | Workstreams |
| Activities | Work packages | PBIs | PR-sized deliverables | Workflow records |
| Tasks | Delivery tasks | Tasks | Commits / PR tasks | `project.task`, approvals |
| Resources | Plans / controls | Capacity, iterations | Repos, runners, envs | Users, companies, DMS |

---

## Spec Kit → Azure Boards sync rules

Spec Kit is the **definitional** source. Boards is the **execution tracker**. Never duplicate.

### Direction: Spec Kit → Boards (one-way write)

```
spec/<slug>/tasks.md        (source of truth — feature intent)
    │
    │  sync script (spec-to-issue bridge)
    ▼
Azure Boards Epic: spec bundle title
  └── PBI: each plan slice
       └── Task: each unchecked tasks.md item
```

### Stable traceability fields

Every Boards item synced from a spec bundle MUST have these custom fields (or tags as fallback):

| Field | Example | Purpose |
|---|---|---|
| `spec_slug` | `pulser-assistant-odoo-finance` | Identifies source bundle |
| `spec_phase` | `plan` or `tasks` | Which doc in the bundle |
| `requirement_ref` | `FR-013` | Links to numbered requirement |
| `task_ref` | `T021` | Links to specific task in tasks.md |
| `delivery_stream` | `Finance Core` | Team/area path |
| `release_gate` | `R2-Core-Execution-60d` | Target iteration |
| `scenario` | `OPRG-2307-readiness` | Business scenario (if applicable) |

Tags (in addition): `pulser`, `odoo18`, `oca`, `foundry`, `bridge`, `evals`, `uat`, `finance`, `bir2307`, `fitout`, `wave-1`, `wave-2`, `wave-3`.

### Close-the-loop

- Spec `tasks.md` checkbox `[x]` → Boards Task state `Done`
- Boards Task `Done` → sync script updates `tasks.md` checkbox
- Boards has `spec_slug` populated → spec bundle has corresponding Board ID in tasks.md

No duplicate task systems. One canonical path.

---

## PRINCE2 stage gates for IPAI initiatives

Each major initiative (e.g., "Pulser for PH marketplace launch") passes through:

| Stage | Entry criteria | Exit criteria | IPAI iteration |
|---|---|---|---|
| **Initiation** | Mandate approved (VMOKRAPI-SPATRES Program defined) | Spec bundle(s) drafted, business case signed | R1-Foundation |
| **Core Execution** | Spec approved, Boards seeded, iterations assigned | Preview-submittable artifacts | R2-Core-Execution |
| **Hardening** | Preview submitted, UAT scenarios defined | Certification pass, no sev-1 bugs | R3-PH-Ops-Hardening |
| **Go-Live / GA** | All gates passed, design partners signed | Public publish, first transactable sales | R4-GA |
| **Post-GA / Close** | Customer references secured | Case studies published, retrospective complete | R5+ |

Each gate is a **human decision**, not an automated check. Gate evidence lives in `docs/evidence/<stamp>/<stage>/`.

---

## Power BI reporting model (via ADO Analytics OData)

### Dashboard set (minimum)

| Dashboard | Audience | Primary OData slice |
|---|---|---|
| **Executive Roadmap** | Jake, investors, MS sellers | `$filter=WorkItemType eq 'Epic'`, group by state + iteration |
| **Sprint / Iteration** | Each delivery stream team | `$filter=IterationPath eq 'R2-Core-Execution-60d'`, group by state |
| **Release Gate** | Compliance, release mgmt | `$filter=Tags/any(t: t eq 'release-gate')`, by stage |
| **Spec Traceability** | Jake (planning integrity) | `$filter=spec_slug ne null`, rollup by spec_slug |
| **Quality / PR Flow** | Engineering | `$filter=PullRequests/any()`, state × work item type |
| **Microsoft Co-sell** | Jake + So Yeong Choi | `$filter=Tags/any(t: t eq 'wave-1')`, group by Epic |

### Useful OData queries

```
# All work items for a spec bundle
$filter=Custom.spec_slug eq 'pulser-assistant-odoo-finance'

# Blocked items in current iteration
$filter=State eq 'Blocked' and IterationPath eq 'R2-Core-Execution-60d'

# Traceability completeness check
$filter=Custom.spec_slug eq null and WorkItemType eq 'PBI'

# Feature-level rollup for executive dashboard
$apply=filter(WorkItemType eq 'Epic')/groupby((State), aggregate(count() as Count))

# Blocked work by delivery stream
$filter=State eq 'Blocked'&$apply=groupby((AreaPath), aggregate(count() as Blocked))
```

Power BI gets these via the [Power Query OData connector](https://learn.microsoft.com/en-us/azure/devops/report/powerbi/access-analytics-power-bi) with `OmitValues = ODataOmitValues.Nulls` to prevent throttling.

---

## Odoo boundary — the one thing never in Boards

Business records stay in Odoo. Never syncing them into Boards. Ever. Reasons:

1. Odoo is the audit trail for finance/compliance — moving to Boards breaks audit
2. Odoo's state machine + approvals are governed by module logic; Boards can't enforce
3. Duplicate-write patterns always drift; single source of truth discipline
4. Boards OData wasn't designed for transaction-level volumes

Boundary summary:

| Concern | Lives in |
|---|---|
| "Is this invoice ready to post?" | Odoo |
| "Is the code for invoice-readiness logic merged?" | Boards + GitHub |
| "Is the UAT test run green for this logic?" | Boards + Azure Pipelines |
| "Is the pilot customer ready operationally?" | Odoo + business dashboards |
| "Is the release gate passed for marketplace publish?" | Boards |

Cross-plane summary answers ("Are we pilot-ready?") are synthesized from parallel MCP reads — they aren't stored anywhere as a single record.

---

## Execution doctrine (minimum viable discipline)

For every non-trivial initiative:

1. **Strategy** — write Vision/Mission/Objectives in `docs/strategy/<initiative>.md`
2. **Governance** — stage plan + business case in `docs/governance/<initiative>-stage-plan.md`
3. **Spec** — `spec/<slug>/` bundle (constitution + PRD + plan + tasks)
4. **Plan** — Epic + PBIs + Tasks in Boards, linked to spec_slug + requirement_ref
5. **Execute** — GitHub branch + PR, AB# link to work item
6. **Gate** — Azure Pipelines + human stage-gate review
7. **Report** — Power BI dashboard reflects progress
8. **Close** — Odoo records reflect actual business outcomes + retrospective committed

Skip any of 1-2 for small initiatives; 3-8 are non-negotiable.

---

## References

- `docs/architecture/plane-separation.md` — 4-plane model
- `docs/architecture/oprg-plane-mapping.md` — OPRG scenario routing
- `docs/templates/ado-copilot-work-item.md` — Copilot-ready work items
- `docs/templates/repo-to-boards-contract.md` — AB# linking
- `docs/templates/basic-vs-scrum-decision.md` — process choice
- `docs/templates/ipai-platform-boards-config.md` — team/iteration/WIP setup
- [VMOKRAPI-SPATRES overview](https://en.wikipedia.org/wiki/OKR) *(general reference)*
- [PRINCE2 overview](https://www.axelos.com/certifications/prince2/prince2-foundation)
- [Azure DevOps Analytics + Power BI](https://learn.microsoft.com/en-us/azure/devops/report/powerbi/access-analytics-power-bi)
