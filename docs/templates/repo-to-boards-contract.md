# Repo ↔ Boards Operating Contract (ipai-platform ↔ Insightpulseai GitHub org)

> Canonical linking model: Azure Boards for planning, GitHub for code, AB#
> linking for traceability. GitHub is source-of-truth for PRs; Boards is
> source-of-truth for work tracking. Do not migrate source into Azure Repos.

---

## 1. Topology

```
Azure DevOps
└── org: insightpulse
    └── project: ipai-platform   ← planning/governance truth
        └── work items (Epic/Feature/PBI/Task)
                   │
                   │  AB# linking + Azure Boards app
                   ▼
GitHub Enterprise: ipai
└── org: Insightpulseai
    ├── odoo / web / agents / platform / infra / data-intelligence /
    ├── agent-platform / automations / design / docs / .github / templates /
    └── ugc-mediaops-kit / etc.                    ← code truth
```

Connection is maintained by the **Azure Boards App for GitHub** (not individual PATs).
Install link: [github.com/apps/azure-boards](https://github.com/apps/azure-boards) →
authorize for `Insightpulseai` org → select all relevant repos.

## 2. Naming conventions

### 2.1 Branch names

```
Pattern:   <type>/ab<work-item-id>-<kebab-case-summary>
Examples:
  feature/ab1234-2307-readiness-validator
  fix/ab1287-entra-agent-scope
  chore/ab1301-upstream-azure-skills-refresh
  docs/ab1315-update-ship-readiness-checklist
```

Rules:
- `<type>` ∈ `{feature, fix, chore, docs, test, refactor}` — matches your commit convention
- `ab<id>` is required so Boards auto-links the branch to the work item
- Summary ≤ 50 chars, lowercase, hyphenated
- Never push to `main` directly

### 2.2 PR titles

```
Pattern:   <type>(<scope>): <summary>  AB#<work-item-id>
Examples:
  feat(bir): add 2307 release blocker when final certificate missing  AB#1234
  fix(agent): correct Entra scope on pulser-finance  AB#1287
  docs(release): clarify Feature Ship-Readiness gate 3.2  AB#1315
```

Rules:
- `<scope>` matches your existing scopes: `oca`, `repo`, `ci`, `deps`, `deploy`, or a module name
- `AB#<id>` at end — Boards automatically links the PR to the work item
- PR **body** includes at minimum:
  - Link to the spec bundle: `Spec: spec/<bundle>/`
  - Scope summary (what's in, what's out)
  - Acceptance criteria from the work item (copy-paste OK)
  - Screenshots / logs / evidence as applicable

### 2.3 Commit messages

```
Pattern:   <type>(<scope>): <summary>

[body]

AB#<work-item-id>
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

The `AB#` trailer links each commit to its work item — useful when backporting or auditing.

### 2.4 State-transition keywords

GitHub PR merge can auto-transition a work item if the PR body or commit message contains one of:

- `fixes AB#1234` → moves work item to Done/Closed on merge
- `closes AB#1234` → same
- `resolves AB#1234` → same

**Use sparingly** — only when the PR fully completes the work item. For partial progress, just reference `AB#1234` without keyword.

## 3. Work item field contract

Every Boards work item MUST have:

| Field | Required for | Purpose |
|---|---|---|
| Title | All types | Short, verb-first |
| Description | All types | Business context + scope |
| Acceptance Criteria | PBI, Bug, Issue | Testable closure conditions |
| Repo | Implementation items | Maps to GitHub repo (single repo per item) |
| Tag(s) | All | Filter views (`wave-1`, `marketplace`, `pulser`, `bir`, `security`, ...) |
| Priority | All | 1 (critical) · 2 (important) · 3 (nice-to-have) |
| Area Path | All | Maps to team / capability area |
| Iteration Path | Active items | Sprint or release window |

Optional but recommended:

- **Spec bundle link** (as a URL field or in description) → `spec/<bundle>/`
- **Attached artifacts** (PR URL, deployment log, screenshot) once work starts
- **Comments** for decisions/pivots during implementation

## 4. Pull request gate

Every PR on a work item-linked branch goes through:

1. **Required checks** (Azure Pipelines) — canonical merge gate per CLAUDE.md authority matrix
2. **Required review** — at least 1 approver (Jake for production repos)
3. **Auto-transition** on merge (if `fixes AB#` keyword) or **manual state move** to Done

No merges with unlinked PRs to `main`. Exceptions require written ADR in `docs/architecture/`.

## 5. Anti-patterns

| Don't | Why |
|---|---|
| Create a branch without AB#id | Breaks traceability |
| One PR spanning multiple work items | Violates 1:1 mapping; review complexity explodes |
| PR body "see AB for details" with no details | Reviewers shouldn't context-switch to read the story |
| Skipping `AB#` in commit trailer | Auditor can't follow commit → item path without it |
| Using Azure Repos | Not canonical — stay on GitHub for source control |
| Editing the PR title after link created | Can unlink; if you must, also update the work item comment |

## 6. AB# quick reference

| AB# form | Placement | Effect |
|---|---|---|
| `AB#1234` | PR title or body, commit message | Links PR/commit to work item |
| `fixes AB#1234` | PR body or merge commit | Auto-transitions state on merge |
| `Epic: AB#1234` | Child work item description | Visual parent reference only |
| `Related: AB#1234, AB#1235` | Any text field | Soft reference (not formal link) |

## 7. Example end-to-end (BIR 2307 blocker)

```
1. Plane: Spec lives at spec/bir-tax-compliance/ (existing)
2. Boards: PBI "Add 2307 release blocker when final certificate PDF missing"
   ID = AB#1234
   Repo field: Insightpulseai/odoo
   Tags: bir-compliance, finance, pulser, wave-1
3. Dev:
     git checkout -b feature/ab1234-2307-readiness-validator
     # Copilot auto-launch from Boards populates initial commit
     # …tests + implementation…
     git commit -m "feat(bir): add 2307 release blocker AB#1234"
4. PR opens:
     Title: "feat(bir): add 2307 release blocker  AB#1234"
     Body: includes spec link + acceptance criteria + test evidence
     Keywords: "fixes AB#1234" (because PR fully completes the item)
5. Azure Pipelines runs (canonical gate)
6. Reviewer approves
7. Merge → work item auto-transitions to Done
8. Spec bundle: update spec/bir-tax-compliance/tasks.md — mark [x]
```

## 8. Setup checklist (one-time, per Boards project)

- [ ] Install Azure Boards App for GitHub (org-scoped, not user PAT)
- [ ] Authorize all repos under `Insightpulseai` org
- [ ] Configure default area/iteration paths on `ipai-platform`
- [ ] Add `AB#` to branch-protection linting on `main` (optional: block PRs without AB#)
- [ ] Document this contract in team onboarding (linked from `CLAUDE.md`)
- [ ] Migrate existing open PRs — add AB# retroactively if they map to existing items

## 9. References

- [Azure Boards ↔ GitHub overview](https://learn.microsoft.com/en-us/azure/devops/boards/github)
- [AB# linking syntax](https://learn.microsoft.com/en-us/azure/devops/boards/github/link-to-from-github)
- [Azure Boards App for GitHub](https://github.com/apps/azure-boards)
- IPAI CLAUDE.md authority matrix — Azure Pipelines is canonical deploy authority
- `docs/templates/ado-copilot-work-item.md` — sister doc for Copilot-launched items
