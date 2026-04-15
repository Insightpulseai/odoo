# Azure Boards Area Path + Iteration Map

> **Locked:** 2026-04-15
> **Project:** `insightpulseai/ipai-platform`
> **Companion:** [`azure-boards-portfolio-target-state.md`](./azure-boards-portfolio-target-state.md)

---

## Area path tree (team ownership)

```
\InsightPulseAI                       (root, portfolio team)
├── \InsightPulseAI\CoreOps           (Odoo, Pulser, Finance, ProjectOps, BIR)
├── \InsightPulseAI\AdsIntel          (Ads + Customer Insights parity)
├── \InsightPulseAI\Research          (PrismaLab + research workflows)
├── \InsightPulseAI\DataIntel         (Databricks, Fabric, lakehouse, semantic)
├── \InsightPulseAI\Platform          (Shared SaaS control plane + FinOps + Governance)
└── \InsightPulseAI\ReleaseOps        (Bicep / Pipelines / Observability / Release strategies)
```

### Rules
- Every active work item carries exactly one area path.
- Epics are owned at the root (`\InsightPulseAI`) by the portfolio team.
- Features are assigned to the owning domain area path.
- Stories / Tasks inherit the Feature's area path unless deliberately reassigned.

### Sub-paths (only when needed; create on demand)

```
\InsightPulseAI\CoreOps\Finance
\InsightPulseAI\CoreOps\ProjectOps
\InsightPulseAI\CoreOps\BIR
\InsightPulseAI\Research\PrismaLab
\InsightPulseAI\Research\AssistantAI
\InsightPulseAI\Platform\Tenancy
\InsightPulseAI\Platform\FinOps
\InsightPulseAI\ReleaseOps\IaC
\InsightPulseAI\ReleaseOps\Pipelines
\InsightPulseAI\ReleaseOps\Observability
```

Don't pre-create empty sub-paths. Create when there are ≥ 5 items under one.

---

## Iteration path tree (sprint cadence)

```
\InsightPulseAI                       (root)
└── \InsightPulseAI\2026
    ├── \InsightPulseAI\2026\Q1
    │   ├── 2026-S01 (Jan  6 – Jan 17)
    │   ├── 2026-S02 (Jan 20 – Jan 31)
    │   ├── 2026-S03 (Feb  3 – Feb 14)
    │   ├── 2026-S04 (Feb 17 – Feb 28)
    │   ├── 2026-S05 (Mar  3 – Mar 14)
    │   └── 2026-S06 (Mar 17 – Mar 28)
    ├── \InsightPulseAI\2026\Q2
    │   ├── 2026-S07 (Mar 31 – Apr 11)
    │   ├── 2026-S08 (Apr 14 – Apr 25)   ← active
    │   ├── 2026-S09 (Apr 28 – May  9)
    │   ├── 2026-S10 (May 12 – May 23)
    │   ├── 2026-S11 (May 26 – Jun  6)
    │   └── 2026-S12 (Jun  9 – Jun 20)
    ├── \InsightPulseAI\2026\Q3   (target R2 ship: 2026-07-14)
    │   ├── 2026-S13 (Jun 23 – Jul  4)
    │   ├── 2026-S14 (Jul  7 – Jul 18)   ← R2 ship sprint
    │   ├── 2026-S15 (Jul 21 – Aug  1)
    │   ├── 2026-S16 (Aug  4 – Aug 15)
    │   ├── 2026-S17 (Aug 18 – Aug 29)
    │   └── 2026-S18 (Sep  1 – Sep 12)
    └── \InsightPulseAI\2026\Q4   (target R3 ship: 2026-10-14, R4 GA: 2026-12-15)
        ├── 2026-S19 (Sep 15 – Sep 26)
        ├── 2026-S20 (Sep 29 – Oct 10)
        ├── 2026-S21 (Oct 13 – Oct 24)   ← R3 ship sprint
        ├── 2026-S22 (Oct 27 – Nov  7)
        ├── 2026-S23 (Nov 10 – Nov 21)
        ├── 2026-S24 (Nov 24 – Dec  5)
        └── 2026-S25 (Dec  8 – Dec 19)   ← R4 GA sprint
```

### Cadence
- **2-week sprints**, Monday 00:00 Asia/Manila start, Friday 23:59 week-2 end.
- Sprints align to ship gates from [`project_acceleration_plan_20260414.md`](../../.claude/projects/-Users-tbwa-Documents-GitHub-Insightpulseai/memory/project_acceleration_plan_20260414.md):
  - **R2** = 2026-07-14 (S14)
  - **R3** = 2026-10-14 (S21)
  - **R4 GA** = 2026-12-15 (S25)

### Rolling forward
On Apr 27 gate (per acceleration plan), provision Q4 + 2027-Q1 sprint paths.

---

## Test Plans (5)

Per portfolio target state, expand from current 2 to 5:

| Test Plan ID | Name | Owning area path |
|---|---|---|
| TP-001 | Platform Release Readiness | `\InsightPulseAI\ReleaseOps` |
| TP-002 | Odoo / CoreOps Regression | `\InsightPulseAI\CoreOps` |
| TP-003 | PrismaLab Tool Regression | `\InsightPulseAI\Research` |
| TP-004 | Agent / Pulser Eval + Acceptance | `\InsightPulseAI\AdsIntel` |
| TP-005 | Data-Intelligence Contract Validation | `\InsightPulseAI\DataIntel` |

Each Test Plan has its own iterations (run per release candidate, not per sprint).

---

## Provisioning order

1. Create root area path `\InsightPulseAI` (already exists).
2. Create the 6 child area paths.
3. Create the 2026 iteration tree (Q1–Q4).
4. Create the 5 Test Plans.
5. Run a one-time bulk re-area-path of existing items (script TBD).

---

## Anti-patterns

- Pre-creating empty sub-paths "for the future" — adds noise
- Using area paths for non-team purposes (don't encode product into area path; that's tags)
- Sprint paths not aligned to ship gates — defeats portfolio rollup
- Mixing old and new iteration trees (delete prior ad-hoc iterations)

---

*Last updated: 2026-04-15*
