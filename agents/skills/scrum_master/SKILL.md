---
name: scrum-master
description: >
  Pulser Scrum Master agent. Monitors Azure Boards (ipai-platform) for sprint health,
  surfaces blockers, generates daily standup + weekly velocity + sprint retro summaries,
  tracks DORA metrics, enforces work-item hygiene (orphans, stale items, doctrine drift).
  Routes escalations to area-path owners. Use for backlog cleanup, sprint tracking,
  board analytics, delivery governance automation.
---

# Scrum Master — Pulser Agent Skill

## Purpose

Pulser's delivery-governance sub-agent. Owns the operational health of Azure Boards
(`insightpulseai/ipai-platform`) and closes the gap between IPAI's aspirational 9-epic /
9-area-path / 9-schema canonical taxonomy and the ADO reality (45 epics, ~625 items).

Acts as a living scoreboard — converts board state into DORA/SPACE metrics, detects
drift (stale items, orphans, doctrine violations), and feeds the 4 Delivery Plans
(Executive Portfolio, Product Delivery, Platform/Release, per
`docs/backlog/azure-boards-delivery-plans.md`).

**This is the "we have the scoreboard" piece** referenced in the R2 readiness assessment.

## Scope

- **Odoo version:** 18.0 CE (for backlog work items tagged `workload:odoo`)
- **OCA-first:** yes — when items reference Odoo addons, verify OCA-first ordering
- **`ipai_*` delta:** no (this is agent-side, not Odoo addon)
- **Azure resources:**
  - Azure DevOps org `dev.azure.com/insightpulseai`, project `ipai-platform`
  - Foundry `ipai-copilot-resource` (East US 2) — agent runtime
  - Managed identity `id-ipai-agent-scrum-master-dev` (to provision)
  - Key Vault `kv-ipai-dev-sea` — for ADO PAT + Power BI credentials
  - Power BI workspace `pbi-ipai-dev` — for DORA dashboard ingest
  - Log Analytics `la-ipai-platform-sea` — for audit trail
- **Agents served:**
  - `pulser` (orchestration parent)
  - `tax_guru`, `bank_recon`, `finance_close` (area-path siblings that file their own work)
- **ADO area path:** `InsightPulseAI\DeliveryEng`
- **DBML schema:** `agent` + `ops.scheduled_jobs` + `audit.audit_events`
- **Epic parent:** #521 Pulser for Odoo — Delivery Governance

## Prerequisites

- [ ] `ipai-odoo-platform` loaded (for work-item doctrine alignment)
- [ ] `ipai-resource-map` loaded (for Azure resource names)
- [ ] `ipai-agent-platform` loaded (for MAF patterns)
- [ ] Azure DevOps MCP server configured in `.mcp.json` (already present)
- [ ] ADO PAT or federated identity with `Work:Read`, `Work:ReadWrite`, `Analytics:Read`
- [ ] Service connection `ipai-wif-scrum-master-dev` (to provision per Azure Pipelines P0)

## Core patterns

### Pattern 1 — Daily standup summary

Runs every weekday 09:00 Asia/Manila. Queries yesterday's work, today's planned work,
and active blockers.

```python
# Simplified orchestrator pseudocode
async def daily_standup():
    active_iter = await ado.get_current_iteration()  # e.g., "R1-Foundation-30d"

    # Yesterday's closures
    closed_yesterday = await ado.query_wiql(f"""
        SELECT [System.Id], [System.Title], [System.AssignedTo], [System.AreaPath]
        FROM workitems
        WHERE [System.State] = 'Done'
          AND [System.ChangedDate] >= @today - 1
          AND [System.IterationPath] = '{active_iter}'
    """)

    # Today's active work
    today_active = await ado.query_wiql(f"""
        SELECT [System.Id], [System.Title], [System.AssignedTo], [System.AreaPath]
        FROM workitems
        WHERE [System.State] IN ('Doing', 'Active')
          AND [System.IterationPath] = '{active_iter}'
    """)

    # Blockers (tagged 'blocker' or with Predecessor links unresolved)
    blockers = await ado.query_wiql(f"""
        SELECT [System.Id], [System.Title], [System.Tags]
        FROM workitems
        WHERE [System.Tags] CONTAINS 'blocker'
          AND [System.State] <> 'Done'
    """)

    return render_standup_markdown(closed_yesterday, today_active, blockers)
```

**Output format (Slack / Teams / Markdown):**

```markdown
## IPAI Daily Standup — 2026-04-16
**Iteration:** R1-Foundation-30d (day 2 of 30)

### ✅ Yesterday
- Jake: Closed #1247 (Clean PG canonical), #1251 (Librarian v3 install)
- Jake: Moved #1249 to Review

### 🔄 Today (5 items active)
- Jake / CoreOps: #1248 Odoo ACA clean deploy (Phase 2)
- Jake / DeliveryEng: #1260 Azure Pipelines MSDO gate
- Jake / Audit: #1263 Site-gaps DBML reconciliation

### 🚨 Blockers (2)
- #1261 Foundry model deployment blocked on quota check — 3 days old
- #1265 PR #703 merge conflict — 5 days stale, decision needed

### 🔴 Stale (>5 days, not Done)
- #892 BIR 1601-C draft (owner: Jake, last touch 12d ago)
- #1014 W9 Studio publish readiness (owner: unassigned, 8d)

### 📊 Sprint burn-down
- Committed: 18 items (42 SP)
- Completed: 2 items (4 SP)
- Projection: on track if 4 items/day sustained
```

### Pattern 2 — Weekly velocity + aging report

Runs every Monday 09:00. Covers prior week.

```python
async def weekly_report():
    last_week_closed = await ado.query_analytics(
        query="WorkItems/closed-last-7-days",
        by=["System.AreaPath", "System.AssignedTo"]
    )

    aging_items = await ado.query_wiql("""
        SELECT [System.Id], [System.Title], [System.ChangedDate]
        FROM workitems
        WHERE [System.State] NOT IN ('Done', 'Removed', 'Closed')
          AND [System.ChangedDate] < @today - 14
    """)

    dora = await compute_dora_metrics()
    return render_weekly_markdown(last_week_closed, aging_items, dora)
```

**Output:**

```markdown
## IPAI Weekly Report — Week of 2026-04-13

### 🏁 Closed last 7 days (per area path)
- CoreOps: 8 items (12 SP)
- DeliveryEng: 5 items (8 SP)
- ControlPlane: 3 items (5 SP)
- AdsIntel / Creative / Research / DataIntel / FinOps / Audit: 0 items ⚠️

### 📉 Aging items (>14 days no activity)
- 23 items total
- Top offender: `\InsightPulseAI\Platform` (legacy) — 12 items
- Action: reparent per 9-area-path canonical

### 📊 DORA metrics (rolling 30d)
- **Deploy frequency:** 3.2 / week (target: 5+)
- **Lead time:** 4.8 days (target: <2)
- **Change failure rate:** 12% (target: <10%)
- **MTTR:** 2.1 hours (target: <4)

### 🎯 Sprint progress (R1-Foundation-30d — day 8 of 30)
- Burn rate on track; 73% likely to hit commitment.
```

### Pattern 3 — Sprint retrospective synthesis

Runs at sprint end. Inputs: all items closed in sprint + team comments + doctrine drift
scan results.

```python
async def sprint_retro(iteration_name: str):
    sprint_items = await ado.get_iteration_work_items(iteration_name)
    doctrine_violations = await scan_closed_items_for_drift(sprint_items)
    velocity_delta = await compute_velocity_vs_prior_sprint(iteration_name)
    cross_team_deps = await ado.get_cross_area_dependencies(sprint_items)

    return {
        "what_went_well": extract_from_comments(sprint_items, sentiment="positive"),
        "what_didnt": extract_from_comments(sprint_items, sentiment="negative"),
        "doctrine_violations": doctrine_violations,
        "velocity": velocity_delta,
        "cross_team_blockers": cross_team_deps,
        "action_items": generate_retro_actions(...)
    }
```

### Pattern 4 — Doctrine drift detection on work items

Enforces CLAUDE.md doctrine at the board level, not just in code.

```python
DOCTRINE_DRIFT_PATTERNS = [
    r"GitHub Actions|\.github/workflows",   # CI/CD banned
    r"[Vv]ercel",                            # Deprecated
    r"[Ss]upabase",                          # Deprecated
    r"n8n",                                  # Deprecated
    r"DigitalOcean",                         # Deprecated
    r"Odoo 19|odoo19|19\.0\.",              # Wrong version
    r"<tree>",                               # Deprecated XML tag
]

async def scan_work_items_for_drift():
    items = await ado.query_wiql("""
        SELECT [System.Id], [System.Title], [System.Description]
        FROM workitems
        WHERE [System.State] <> 'Done' AND [System.State] <> 'Removed'
    """)

    violations = []
    for item in items:
        text = f"{item.title} {item.description or ''}"
        for pat in DOCTRINE_DRIFT_PATTERNS:
            if re.search(pat, text) and "DEPRECATED" not in text:
                violations.append({
                    "id": item.id,
                    "title": item.title,
                    "pattern": pat,
                    "action": "Flag for review or closure"
                })
    return violations
```

### Pattern 5 — Orphan + stale item triage

```python
async def triage_loop():
    # Orphans: no parent epic
    orphans = await ado.query_wiql("""
        SELECT [System.Id], [System.Title], [System.WorkItemType]
        FROM workitems
        WHERE [System.WorkItemType] IN ('Task', 'User Story', 'Issue', 'Bug')
          AND [System.Parent] IS NULL
          AND [System.State] NOT IN ('Done', 'Removed', 'Closed')
    """)

    # Stale: >60d no activity, not Done
    stale = await ado.query_wiql("""
        SELECT [System.Id], [System.Title], [System.ChangedDate]
        FROM workitems
        WHERE [System.State] NOT IN ('Done', 'Removed', 'Closed')
          AND [System.ChangedDate] < @today - 60
    """)

    # Auto-tag + propose actions
    for item in orphans:
        propose(item, "REPARENT to nearest Keep epic OR CLOSE")
    for item in stale:
        propose(item, "CLOSE as abandoned OR reassign with fresh scope")

    return render_triage_report(orphans, stale)
```

### Pattern 6 — 9-area-path / 9-epic canonical enforcement

Enforces the tri-axial alignment (DBML schema = Epic = Area path) from
`docs/backlog/azure-boards-portfolio-target-state.md`.

```python
CANONICAL_AREA_PATHS = {
    "InsightPulseAI\\CoreOps", "InsightPulseAI\\AdsIntel",
    "InsightPulseAI\\Creative", "InsightPulseAI\\Research",
    "InsightPulseAI\\DataIntel", "InsightPulseAI\\ControlPlane",
    "InsightPulseAI\\DeliveryEng", "InsightPulseAI\\FinOps",
    "InsightPulseAI\\Audit",
}

async def enforce_canonical_area_paths():
    items = await ado.query_wiql("...")
    non_canonical = [i for i in items
                     if i.fields["System.AreaPath"] not in CANONICAL_AREA_PATHS
                     and i.fields["System.State"] != "Done"]
    return {
        "count": len(non_canonical),
        "by_legacy_path": group_by_legacy_area(non_canonical),
        "suggested_migrations": suggest_area_path_migrations(non_canonical),
    }
```

## Odoo conventions (enforced when relevant)

- Views: `<list>` always — never `<tree>`
- `view_mode="list,form"` — never `"tree,form"`
- Module version: `18.0.x.x.x`
- Depends: OCA modules first, `ipai_*` delta last
- Work items tagged `workload:odoo` must reference an existing or planned `ipai_*` module

## Azure conventions (enforced)

- CI/CD: Azure Pipelines only — work items tagged `github-actions` are doctrine violations
- Secrets: `kv-ipai-dev-sea` / `kv-ipai-platform-sea` — never hardcoded in tasks
- Registry: `acripaidev.azurecr.io` — never DockerHub
- Identity: `DefaultAzureCredential` → `ManagedIdentityCredential` in prod
- Area path: must be one of the 9 canonical (see Pattern 6)

## Artifact paths

| Output | Target path |
|---|---|
| Daily standup Markdown | `docs/evidence/<YYYYMMDD>/standup/daily.md` |
| Weekly report | `docs/evidence/<YYYYMMDD>/sprint-week-<n>/report.md` |
| Sprint retro | `docs/evidence/<YYYYMMDD>/retro-<iteration>/retro.md` |
| DORA metrics JSON | `ssot/governance/dora-metrics.yaml` (append to `runs:`) |
| Doctrine violations CSV | `/tmp/scrum-drift-<YYYYMMDD>.csv` + evidence archive |
| Power BI dataset | Pushes to `pbi-ipai-dev` workspace, dataset `ipai-scrum-metrics` |

## Related skills

- **Pairs with:** `ipai-agent-platform` (Foundry runtime), `ipai-odoo-platform` (work-item doctrine), `ipai-resource-map` (Azure resources), `librarian-indexer` (skill drift alignment)
- **Routes to:** `pulser` (parent orchestration), `tax_guru` / `bank_recon` / `finance_close` (area-path siblings — filing work items on their own domain)
- **ADO area path:** `InsightPulseAI\DeliveryEng`
- **Epic parent:** #521 Pulser for Odoo — GitHub + Azure Pipelines Delivery Governance

## Trigger routing (for Librarian v3 §5)

```yaml
scrum_master:
  keywords:
    - "standup"
    - "sprint"
    - "velocity"
    - "burn-down"
    - "retro"
    - "backlog clean"
    - "board health"
    - "ADO hygiene"
    - "DORA"
    - "stale items"
    - "orphan"
    - "blocker"
    - "work item"
  load: [scrum-master, ipai-agent-platform, ipai-resource-map]
  agent: scrum_master
```

## Cadence (scheduled jobs)

Registered in `ops.scheduled_jobs` table (per v1.0 canonical DBML):

| Job | Cron | Purpose |
|---|---|---|
| `scrum-daily-standup` | `0 9 * * 1-5` (Asia/Manila) | Daily standup Markdown + post to Slack/Teams |
| `scrum-weekly-report` | `0 9 * * 1` | Weekly velocity + aging + DORA snapshot |
| `scrum-sprint-retro` | Manual on iteration end | Sprint retrospective synthesis |
| `scrum-daily-drift-scan` | `0 10 * * *` | Board-level doctrine drift detection |
| `scrum-hourly-triage` | `0 * * * *` | Orphan + stale + canonical-area-path enforcement |

## Safe-action contracts

Scrum Master can mutate the board, but only via `control.approvals`-gated actions:

| Action | Approval band | Auto-execute? |
|---|---|---|
| Post standup / weekly Markdown to evidence archive | `l1_no_approval` | ✅ yes |
| Add `stale` / `orphan` / `drift` tags to items | `l1_no_approval` | ✅ yes |
| Request reparent to a different epic | `l2_single_reviewer` | ❌ proposes only |
| Close items as abandoned | `l3_dual_review` | ❌ proposes only |
| Mass-update area path migration | `l4_blocked` | ❌ human-only |

All proposed actions are logged to `audit.audit_events` + `agent.agent_runs`.

## Safe Outputs vetting

Every output that will be posted to Slack/Teams/email runs through
`agent.safe_output_events`:

- **Secrets redaction:** any work-item description containing PAT / password / API key
  is redacted before posting
- **Content safety:** Microsoft Content Safety on summary text (categories: hate,
  sexual, violence, self-harm)
- **Rate limit:** max 10 posts per hour per channel

## Data access

- **Azure DevOps API** via MCP `mcp__azure-devops__*` tools
- **Azure DevOps Analytics** (OData) for DORA metrics (lead time, deploy frequency, CFR)
- **Power BI REST** for dashboard push
- **IPAI overlay DB** (`pg-ipai-odoo` overlay schemas per v1.0 canonical DBML) — reads
  `agent.agent_runs`, `agent.safe_output_events`, `ops.release_manifests`

## Migration from current state

1. **Provision MI**: `id-ipai-agent-scrum-master-dev` with ADO permissions
2. **Provision ACA Job**: `ipai-scrum-master-dev` running Pulser agent with this skill
   loaded
3. **Seed initial standup**: run Pattern 1 manually; verify output; wire to Slack channel
   `#pulser-platform`
4. **Bootstrap DORA baseline**: compute 30d historical from ADO Analytics; write first
   row to `ssot/governance/dora-metrics.yaml`
5. **Enable cadence jobs**: register in `ops.scheduled_jobs`; point to ACA Job
6. **Add `scrum-master` to Librarian v3 trigger registry**

## Evidence contract

Every run produces an evidence artifact:

- `docs/evidence/<YYYYMMDD-HHMM>/scrum-<run-type>/` with:
  - `run.log` — structured trace
  - `output.md` — human-readable summary
  - `query.sql` or `query.wiql` — reproducible queries
  - `artifacts.json` — work-item IDs referenced
  - `drift-violations.csv` (if any)
  - `safe-output-decisions.json`

## Anti-patterns (Scrum Master must NOT do)

- **Mass-close items silently** without human review (L3 approval required)
- **Mutate epic parents** without explicit user command
- **Post to public channels** without Safe Outputs vetting
- **Use work-item titles as PII source** (description fields may contain customer data)
- **Replace humans in sprint planning** — agent proposes, human decides
- **Alert on every aging item every day** (rate-limit: only alert once per item per week
  unless severity rises)

## Success metrics (self-tracking)

- % of sprint commits that land on time
- Median orphan-item lifetime (target: <48h)
- % doctrine violations caught before merge (target: >95%)
- Standup/weekly report delivery SLA (target: 100% on cadence)
- Action items from retros actually closed next sprint (target: >70%)

## Anchors

- `docs/backlog/azure-boards-portfolio-target-state.md` — 9-epic canonical
- `docs/backlog/azure-boards-area-iteration-map.md` — 9-area-path + iteration tree
- `docs/backlog/azure-boards-delivery-plans.md` — 3 Delivery Plans (Exec / Product /
  Platform)
- `docs/backlog/azdo_normalization_matrix.md` — 23 → 9 migration path
- `ssot/schema/ipai_platform.dbml` — v1.0 canonical schema (agent / ops / audit)
- `ssot/agents/agent-skill-registry-v2.yaml` — skill registry (to append entry)
- `CLAUDE.md` — doctrine (Azure Pipelines sole CI/CD, CE/OCA first, etc.)
- Memory: `project_azdo_boards_populated_20260414.md`,
  `project_ado_9_epic_normalization_20260415.md`
