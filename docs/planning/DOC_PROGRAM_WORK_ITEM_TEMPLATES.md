# Documentation Program — Work Item Templates

> Strict templates for Azure Boards work items in the documentation program.
> Process model: Agile | Hierarchy: Epic → Feature → User Story → Task

---

## Naming Conventions

### Epics

```
[TARGET] <Org-Wide Target Name>
```

Examples:
- `[TARGET] Odoo on Azure Operating Model Published`
- `[TARGET] AI Platform Operating Model Published`
- `[TARGET] Governance Drift Closed for Production Baseline`

### Features

```
[FEATURE] <Workstream or Deliverable Family Name>
```

Examples:
- `[FEATURE] Overview Family`
- `[FEATURE] Foundry Control Plane`
- `[FEATURE] Drift Model and Exceptions`

### User Stories

```
<PREFIX>: <canonical file path or validation target>
```

Prefixes:
- `WRITE:` — authored documentation work
- `EVIDENCE:` — validation / proof work
- `INDEX:` — cross-repo landing/index work

Examples:
- `WRITE: platform/docs/workload-center/index.md`
- `EVIDENCE: validate live inventory against IaC`
- `INDEX: docs/odoo-on-azure/ai-platform/index.md`

### Tasks

```
<verb> <specific action>
```

Examples:
- `Draft initial content for workload-center index`
- `Review cross-links and fix broken references`
- `Run az resource list and classify unmanaged resources`

---

## Tags Convention

| Tag | Meaning |
|---|---|
| `doc-program` | All work items in the documentation program |
| `spec-bundle` | Work item traces to a spec bundle |
| `foundation` | Foundation iteration scope |
| `wave-1` | Wave-1 iteration scope |
| `wave-2` | Wave-2 iteration scope |
| `hardening` | Hardening iteration scope |
| `evidence-required` | Story requires evidence artifact for closure |
| `cross-team` | Story requires coordination across teams |
| `depends-<team>` | Dependency on another team (e.g., `depends-infra`) |

---

## State Discipline

| State | Meaning | Rule |
|---|---|---|
| New | Created, not yet refined | Must not enter a sprint |
| Active | In the current sprint, work in progress | Exactly one assignee |
| Resolved | Work complete, awaiting review | PR merged, evidence exists |
| Closed | Accepted, DoD met | Boards rollup counts this |
| Removed | Descoped or duplicate | Must have a reason comment |

**Rule:** Never move directly from New → Closed. Every Story must pass through Active.

---

## Epic Template

```
Title:        [TARGET] <Org-Wide Target Name>
Work Item Type: Epic
Area Path:    ipai-platform
Iteration Path: ipai-platform\Docs
Value Area:   Architectural
Business Value: <50-100>
Time Criticality: <50-100>
Tags:         doc-program, spec-bundle

Description:
  Org-wide target: <1-2 sentence summary>.
  Spec bundle: spec/<target-slug>/
  Benchmark: <benchmark model reference>

Acceptance Criteria:
  - all workstreams have source-of-truth repo ownership
  - cross-repo navigation exists
  - Azure Boards Features are created and linked
  - completion visible through Feature rollups
```

---

## Feature Template

```
Title:        [FEATURE] <Workstream Name>
Work Item Type: Feature
Parent:       [TARGET] <parent Epic>
Area Path:    ipai-platform\<owning-team>
Iteration Path: ipai-platform\Docs\<phase>
Value Area:   Architectural
Business Value: <50-100>
Time Criticality: <50-100>
Tags:         doc-program, <phase>

Description:
  Workstream: <1-2 sentence summary>.
  Canonical repo: <repo name>
  Owning team: <team name>

Acceptance Criteria:
  - all child Stories are Closed or intentionally descoped
  - canonical file paths exist and are navigable
  - evidence Stories have artifacts
```

---

## User Story Template

```
Title:        <PREFIX>: <canonical path or validation target>
Work Item Type: User Story
Parent:       [FEATURE] <parent Feature>
Area Path:    ipai-platform\<owning-team>
Iteration Path: ipai-platform\Docs\<phase>
Tags:         doc-program, <phase>, [evidence-required]

Description:
  <What needs to be authored, validated, or indexed>

Acceptance Criteria:
  - [ ] <observable output 1>
  - [ ] <observable output 2>
  - [ ] PR merged with <keyword> AB#<id>
```

---

## Task Template

```
Title:        <verb> <specific action>
Work Item Type: Task
Parent:       <parent User Story>
Area Path:    ipai-platform\<owning-team>
Iteration Path: ipai-platform\Docs\<phase>

Description:
  <Specific execution step>

Remaining Work: <hours>
```

---

## PR Keyword Conventions

Azure Boards + GitHub integration uses keywords in PR descriptions and commit messages to transition work-item state.

| Keyword | Effect | When to use |
|---|---|---|
| `Resolve AB#1234` | Moves to Resolved on merge | Standard doc/code Stories |
| `Validate AB#1234` | Moves to Resolved on merge | Evidence Stories (semantic signal) |
| `Fixes AB#1234` | Moves to Resolved on merge | Bug-fix Stories |
| `AB#1234` (bare ref) | Links without state change | Cross-references, partial work |

### Rules

1. Every PR that closes a Story MUST include `Resolve AB#<id>` or `Validate AB#<id>` in the description
2. Use `Validate` for `EVIDENCE:` Stories to signal that the PR contains proof, not just code
3. Use `Fixes` only for bug-fix Stories
4. Bare `AB#1234` references are for linking — they do not close the Story
5. Multiple keywords in one PR are allowed: `Resolve AB#100, Resolve AB#101`
6. The keyword must be in the PR description body (not just the title)

### Example PR description

```markdown
## Summary
- Published workload-center index page
- Added cross-links to monitoring and runtime families

Resolve AB#1042
Resolve AB#1043

## Test plan
- [ ] Verify links render correctly
- [ ] Confirm doc-authority model compliance
```

---

## Example: Filled Epic

```
Title:        [TARGET] Odoo on Azure Operating Model Published
Work Item Type: Epic
Area Path:    ipai-platform
Iteration Path: ipai-platform\Docs
Value Area:   Architectural
Business Value: 100
Time Criticality: 95
Tags:         doc-program, spec-bundle

Description:
  Publish the canonical Odoo-on-Azure workload operating model.
  Spec bundle: spec/odoo-on-azure-operating-model/
  Benchmark: SAP on Azure workload operating model

Acceptance Criteria:
  - all 7 workstream Features are Closed or descoped
  - cross-repo navigation from docs/odoo-on-azure/ reaches all families
  - evidence Stories have artifacts in docs/evidence/
  - Azure Boards rollup shows 100% Feature completion
```

## Example: Filled User Story

```
Title:        WRITE: platform/docs/workload-center/index.md
Work Item Type: User Story
Parent:       [FEATURE] Workload Center Family
Area Path:    ipai-platform\platform
Iteration Path: ipai-platform\Docs\Foundation
Tags:         doc-program, foundation

Description:
  Author the workload-center index page covering OSI model,
  environment inventory, drift tracking, and lifecycle operations.

Acceptance Criteria:
  - [ ] File exists at platform/docs/workload-center/index.md
  - [ ] Page links to OSI, inventory, drift, and lifecycle sub-pages
  - [ ] Cross-link from docs/odoo-on-azure/ reaches this page
  - [ ] PR merged with Resolve AB#<id>
```

---

## Related Documents

- [DOC_PROGRAM_BACKLOG.md](DOC_PROGRAM_BACKLOG.md) — full backlog hierarchy
- [DOC_PROGRAM_SPRINT_MODEL.md](DOC_PROGRAM_SPRINT_MODEL.md) — sprint cadence and ceremonies
- [DOC_PROGRAM_SCALING.md](DOC_PROGRAM_SCALING.md) — multi-team scaling model
- [DOC_PROGRAM_IMPORT.csv](DOC_PROGRAM_IMPORT.csv) — Azure Boards CSV import

---

*Created: 2026-04-05 | Version: 1.0*
