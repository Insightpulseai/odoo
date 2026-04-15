# Azure Boards ↔ GitHub Traceability Rules

> **Locked:** 2026-04-15
> **Project:** `insightpulseai/ipai-platform`
> **Companion:** [`docs/ops/azure-boards-operating-guide.md`](../ops/azure-boards-operating-guide.md) §GitHub integration
> **Microsoft refs:**
> - [Azure Boards Integration With GitHub](https://learn.microsoft.com/en-us/azure/devops/boards/github/?view=azure-devops)
> - [Link GitHub commits, PRs, branches, and issues to work items](https://learn.microsoft.com/en-us/azure/devops/boards/github/link-to-from-github?view=azure-devops)

---

## The split (locked)

```
Azure Boards = planning truth         (portfolio, sprints, dependencies)
GitHub PRs/branches/commits = delivery evidence
GitHub Issues = optional repo-local backlog
GitHub Projects = optional team-local board
```

Both systems exist; they **link**, not merge.

---

## Mandatory linkage rules

```
Every PR              → links to ONE primary Boards work item (Story or Feature)
Every Story           → has parent Feature
Every Feature         → has parent Epic
Every Epic            → owned by one of the 7 canonical area-path teams
GitHub Issue          → linked to a Boards work item only when adding repo-local detail
```

### Mention syntax

In any GitHub PR, commit, or Issue body:
```
AB#123                 → links to ADO work item 123 (no state change)
Fixes AB#123           → links AND closes work item on PR merge
Resolved AB#123        → links AND moves work item to Resolved on PR merge
Validate AB#123        → links AND requires approval gate
```

### Reverse direction
In any ADO work item, paste a GitHub URL → auto-creates a "GitHub Pull Request" / "GitHub Commit" / "GitHub Branch" / "GitHub Issue" link object on the work item's Development tab.

---

## Connection setup (one-time)

| Step | Action |
|---|---|
| 1 | ADO project → Project Settings → GitHub connections → New connection |
| 2 | Authorize the Azure Boards GitHub app at the GitHub org level |
| 3 | Select `Insightpulseai/odoo` repo (and any other repos to connect) |
| 4 | Verify by mentioning `AB#1` in a test PR description and confirming the link appears on work item 1 |

**Hard limit:** A GitHub repo can be connected to **only one Azure DevOps organization+project** for Boards integration. So `Insightpulseai/odoo` ↔ `insightpulseai/ipai-platform` is the locked pairing.

**Capacity:** up to 2,000 GitHub repos per Boards connection.

---

## PR template (enforced via `.github/pull_request_template.md`)

```markdown
## Summary
<1–3 bullets>

## Boards link
Closes AB#<id>     ← REQUIRED. PRs without this fail the trace check.

## Test plan
- [ ] ...

## Doctrine alignment
- [ ] Confirms one of the 14+ doctrine contracts in CLAUDE.md
- [ ] Tags + naming + BOM-compliant if infra change
```

A pre-merge check fails if `AB#<digits>` is not present in the PR body.

---

## Enforcement (CI gate)

Add `azure-pipelines/boards-traceability-check.yml`:

```yaml
trigger: none
pr:
  branches:
    include:
      - main
      - 'release/*'

jobs:
  - job: trace_check
    pool: vmImage: ubuntu-latest
    steps:
      - script: |
          if ! grep -qE 'AB#[0-9]+' "$PR_BODY"; then
            echo "FAIL: PR body must include AB#<id> linking to Boards"
            exit 1
          fi
        env:
          PR_BODY: $(System.PullRequest.Body)
```

This runs in Azure Pipelines (per CLAUDE.md doctrine #24 — Azure Pipelines is sole CI/CD authority).

---

## State transition rules

| GitHub event | ADO work item action |
|---|---|
| PR opened with `AB#123` | Story 123 gets a PR link in Development tab; state unchanged |
| PR review approved | No automatic state change; human triages |
| PR merged with `Fixes AB#123` | Story 123 transitions to **Resolved** |
| PR merged with `Resolved AB#123` | Story 123 transitions to **Resolved** |
| PR merged with `Closes AB#123` | Story 123 transitions to **Closed** |
| PR closed without merge | No automatic state change; PR link remains for history |
| GitHub Issue mentioning `AB#123` | Issue ↔ Story 123 linked; bidirectional |

Final acceptance (Closed state) always requires PM/owner confirmation, not auto-fire on merge.

---

## When to use GitHub Issues (NOT Boards)

| Situation | System |
|---|---|
| "Bug found by external contributor in OSS context" | GitHub Issue |
| "Refactor a single method, single PR" | GitHub Issue (or no Issue, just the PR) |
| "Dependency upgrade batch" | GitHub Issue (Dependabot) |
| "Customer-reported defect requiring triage + SLA" | **ADO Bug** (link the GH PR that fixes it) |
| "Multi-sprint feature with stakeholders" | **ADO Feature** |
| "Sprint-planned engineering chore" | **ADO Story / Task** |
| "Compliance work item" | **ADO Story** (per [`ph-close-bir-compliance-board-pack.md`](./ph-close-bir-compliance-board-pack.md)) |

Default: when in doubt, use ADO. GH Issues are **optional repo-local detail**, never primary planning.

---

## SMART success criteria

- 100% of code-delivery PRs link to a Boards work item (`AB#<id>`)
- 0 "orphan" PRs merged to `main` without a Boards link
- 100% of Story closures triggered by either PR merge OR PM acceptance (not silent close)
- 100% of Bugs link to the PR that fixed them (when fixed)
- 0 cross-team dependencies tracked only in PR comments (must be in Boards Related/Predecessor link)

---

## Anti-patterns

- Treating GitHub Issues + Boards Stories as duplicates of the same work
- Using GitHub Projects as primary portfolio system (Boards has the right hierarchy)
- Skipping `AB#<id>` in the PR body
- Closing an ADO Story without the linked PR being merged first
- Connecting one GitHub repo to two ADO projects (not supported)
- Using `AB#<id>` to link to a Backlog item that doesn't exist (broken trace)

---

## Migration checklist

- [ ] Verify Azure Boards GitHub app installed at `Insightpulseai` org level
- [ ] Connect `Insightpulseai/odoo` ↔ `insightpulseai/ipai-platform`
- [ ] Add `.github/pull_request_template.md` enforcing `AB#<id>`
- [ ] Add `azure-pipelines/boards-traceability-check.yml`
- [ ] Make traceability check a required status check on `main` + `release/*`
- [ ] Backfill `AB#<id>` links on open PRs (manual)
- [ ] Document the rule in `CONTRIBUTING.md`

---

*Last updated: 2026-04-15*
