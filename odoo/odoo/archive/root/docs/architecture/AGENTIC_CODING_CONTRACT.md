# Agentic Coding Contract

> **Purpose**: Define the mandatory loop, evidence requirements, rubric, and
> governance integration for all agentic coding runs in the IPAI stack.
>
> **Scope**: Every agent runtime that modifies files, opens PRs, or executes
> code in the `Insightpulseai/odoo` monorepo on behalf of a user or an
> automated trigger.
>
> **Effective date**: 2026-03-01
>
> **Version**: 1.0.0
>
> **Owner**: Platform team (CODEOWNERS: `docs/architecture/AGENTIC_CODING_CONTRACT.md`)

---

## Section 1: The Agentic Coding Loop

Every agentic coding run must complete the following four phases in order.
Skipping a phase or executing phases out of order is a contract violation.

### 1.1 PLAN

The planning phase translates a task input into a structured, reviewable plan
before any file is modified.

**Substeps:**

1. **Create ops.runs entry** — INSERT a row with `status: running` before
   touching any file. The `task_id` field must reference a Plane issue or
   GitHub issue number. This is the audit anchor for the entire run.

2. **Read the task input** — Parse the GitHub issue, Plane task, or chat message.
   Identify: objective, acceptance criteria, and any referenced spec bundles.

3. **Read existing code** — For each file that will be modified, read it first.
   Never patch a file without understanding its current state.

4. **Identify impacted paths** — List every file that will be changed, created,
   or deleted. Flag any restricted paths (see Section 5) for explicit approval.

5. **Assess risk** — Identify whether the change touches: production data paths,
   CI gate configuration, SSOT files, or external API contracts. High-risk
   changes require a plan checkpoint before proceeding.

6. **Produce a structured plan** — Write a plan document containing:
   - Objective (one sentence)
   - Impacted files (repo-relative paths)
   - Spec bundle reference (if applicable)
   - Test strategy (which gate commands will be run)
   - Risk flags (restricted paths, production impact)

7. **Attach plan to ops.runs** — Set `ops.runs.plan_artifact` to the plan
   document path. Update ops.run_events: `step=plan, outcome=completed`.

**Exit criteria:** ops.runs entry exists, plan document written, no restricted
paths touched without explicit approval.

---

### 1.2 PATCH

The patch phase applies the minimal diff required to satisfy the plan.

**Substeps:**

1. **Apply changes file-by-file** — Modify only the files listed in the plan.
   If a new file must be created that was not in the plan, update the plan
   document and add an ops.run_events entry before creating it.

2. **Enforce patch minimality** — Changes must be directly traceable to the
   task objective. No cosmetic reformatting of unrelated files. No adding
   features not in scope. A reviewer should be able to understand every changed
   line in under 5 minutes.

3. **Respect restricted paths** — Files in `ssot/`, `supabase/migrations/`,
   `.github/workflows/`, `infra/`, and `.github/copilot-instructions.md` may not
   be modified without an explicit approval flag (`approved_restricted_paths: true`)
   in the task input or a human comment on the PR.

4. **No secret introduction** — The patch must not add raw API keys, passwords,
   tokens, or credentials to any file. Secret references use environment variable
   names or Vault key references only.

5. **Record patch step** — Update ops.run_events: `step=patch, outcome=applied`,
   with a `detail` JSON object containing the count of files modified and a
   summary of change types (add/edit/delete).

**Exit criteria:** All planned file changes applied, no unplanned files modified,
no secrets in diff, ops.run_events patch record written.

---

### 1.3 VERIFY

The verification phase runs all required CI gates and captures their output as
evidence artifacts before the PR is created.

**Required gate commands (in order):**

```bash
# 1. Repo structure and SSOT health
./scripts/repo_health.sh

# 2. Spec bundle validation (run only if a spec bundle is referenced)
./scripts/spec_validate.sh

# 3. JavaScript/TypeScript lint and type checking (for apps/ and packages/)
pnpm lint
pnpm typecheck

# 4. Python lint (for addons/ipai/, supabase/functions/, scripts/)
python -m flake8 $(git diff --name-only HEAD | grep '\.py$')

# 5. Odoo module syntax check (if addons/ipai/ files are modified)
python -m py_compile $(git diff --name-only HEAD | grep 'addons/ipai.*\.py$')
```

**Evidence capture:**

All gate output must be saved to `docs/evidence/<YYYYMMDD-HHMM+0800>/<task-slug>/logs/`:

```
docs/evidence/20260301-1400+0800/my-task-slug/logs/
├── repo_health.log      # stdout + exit code of repo_health.sh
├── spec_validate.log    # stdout + exit code of spec_validate.sh (if run)
├── lint.log             # stdout + exit code of pnpm lint
├── typecheck.log        # stdout + exit code of pnpm typecheck
└── flake8.log           # stdout + exit code of flake8 (if Python files modified)
```

**Gate failure behavior:**

If any required gate fails, the run MUST NOT proceed to the PR phase.
The agent must:

1. Update ops.run_events: `step=verify, outcome=failed`, with gate name and
   first 10 lines of error output in the `detail` field.
2. Update ops.runs.status to `failed`.
3. Comment on the originating issue with a failure summary and the evidence path.
4. Stop the run. Do not attempt to fix the gate failure automatically in the
   same run — this requires a new run with an updated plan.

**Exit criteria:** All required gates exit 0, evidence artifacts written to
canonical path, ops.run_events verify record written with `outcome=pass`.

---

### 1.4 PR

The PR phase creates the pull request that delivers the verified patch for
human review.

**Substeps:**

1. **Create feature branch** — All changes must be on a feature branch.
   Branch naming: `agent/<task-slug>-<YYYYMMDD>` (e.g., `agent/fix-auth-20260301`).
   Never push directly to `main` or `master`.

2. **Compose PR body** — The PR body must follow the output contract exactly:

   ```
   **[CONTEXT]**
   - repo: Insightpulseai/odoo
   - branch: agent/<task-slug>-<date>
   - cwd: /workspaces/odoo (or agent sandbox path)
   - goal: <single-line task objective>
   - stamp: <ISO8601 with timezone>

   **[CHANGES]**
   - <repo-relative-path>: <one-line intent>
   - ...

   **[EVIDENCE]**
   - command: ./scripts/repo_health.sh
     result: PASS — Health checks: 12/12 passed
     saved_to: docs/evidence/<stamp>/<task>/logs/repo_health.log
   - command: pnpm lint
     result: PASS — 0 errors, 0 warnings
     saved_to: docs/evidence/<stamp>/<task>/logs/lint.log
   - ...

   **[DIFF SUMMARY]**
   - <repo-relative-path>: <why this changed>

   **[BLOCKERS]** (omit if none)
   - <what is blocked>
   - <remediation steps>
   ```

3. **Set PR reviewers and labels** — Auto-assign CODEOWNERS reviewers.
   Add label `agent-generated` to every PR created by an agentic run.

4. **Link ops.runs** — Set `ops.runs.pr_url` to the opened PR URL.
   Set `ops.runs.status` to `completed`.
   Update ops.run_events: `step=pr, outcome=completed`, detail includes PR URL.

5. **Update ops.runs evidence_path** — Set to the canonical evidence directory
   path so the Ops Console can navigate directly to the artifacts.

**Exit criteria:** PR open, body follows output contract, `agent-generated`
label applied, ops.runs.pr_url set, ops.runs.status = `completed`.

---

## Section 2: Mandatory Evidence Requirements

Each phase has non-negotiable evidence requirements. A run cannot be considered
complete if any of the following evidence is absent.

| Phase | Required Evidence | Where Stored |
|-------|-------------------|--------------|
| PLAN | ops.runs row (status: running) | Supabase ops.runs |
| PLAN | ops.run_events row (step=plan, outcome=completed) | Supabase ops.run_events |
| PLAN | Plan document (objective, files, spec ref, risks) | ops.runs.plan_artifact path |
| PATCH | ops.run_events row (step=patch, outcome=applied) | Supabase ops.run_events |
| VERIFY | All gate output files (*.log) | docs/evidence/<stamp>/<task>/logs/ |
| VERIFY | ops.run_events row (step=verify, outcome=pass) | Supabase ops.run_events |
| PR | PR URL on ops.runs.pr_url | Supabase ops.runs |
| PR | PR body with all four output contract sections | GitHub PR |
| PR | ops.runs.evidence_path set to evidence directory | Supabase ops.runs |
| PR | ops.run_events row (step=pr, outcome=completed) | Supabase ops.run_events |

**Evidence that is never sufficient:**

- "See terminal output" — Evidence must be a file path, not a reference to ephemeral output.
- A gate log file that exists but is empty — Empty logs indicate the gate was not run.
- An ops.runs entry without a `task_id` — Untraced runs are governance violations.
- A PR body with the sections present but empty — Sections must have actual content.

---

## Section 3: Rubric

Agentic coding runs are scored on five dimensions, each rated 0–3.
The rubric SSOT is `ssot/advisor/rubrics/agentic_coding.yaml`.

### 3.1 Dimension Definitions

**Dimension 1: Planning quality** (0–3)

| Score | Label | Criteria |
|-------|-------|---------|
| 0 | None | No plan documented before patch |
| 1 | Minimal | Impacted files listed but no spec or rationale |
| 2 | Adequate | Spec or intent documented, impacted files listed, ops.runs entry created |
| 3 | Full | Spec bundle referenced, risk assessment included, ops.runs entry with task_id |

**Dimension 2: Patch minimality** (0–3)

| Score | Label | Criteria |
|-------|-------|---------|
| 0 | None | No constraint on patch scope; changes unrelated files |
| 1 | Partial | Mostly targeted but includes unrelated changes |
| 2 | Good | Only required files changed; no dead-code added |
| 3 | Excellent | Minimal diff; reviewer can confirm scope in under 5 minutes |

**Dimension 3: Test and gate coverage** (0–3)

| Score | Label | Criteria |
|-------|-------|---------|
| 0 | None | No tests run before PR |
| 1 | Partial | Some CI gates pass but SSOT validators not run |
| 2 | Good | All required gates pass (lint, typecheck, repo_health.sh) |
| 3 | Full | All gates pass including spec_validate.sh; gate output attached as evidence |

**Dimension 4: PR evidence quality** (0–3)

| Score | Label | Criteria |
|-------|-------|---------|
| 0 | None | PR exists but has no structured evidence |
| 1 | Minimal | PR description mentions what changed but no evidence links |
| 2 | Good | Evidence section present with file paths and pass/fail lines |
| 3 | Excellent | Evidence follows output contract (CONTEXT, CHANGES, EVIDENCE, DIFF SUMMARY) |

**Dimension 5: Audit trail (ops.runs)** (0–3)

| Score | Label | Criteria |
|-------|-------|---------|
| 0 | None | No ops.runs entry |
| 1 | Partial | ops.runs entry exists but incomplete (missing outcome or evidence_path) |
| 2 | Good | ops.runs entry with task_id, outcome, and PR link |
| 3 | Excellent | ops.runs + ops.run_events for each step; evidence_path populated |

### 3.2 Total Score

Maximum score: **15** (5 dimensions × 3).

Score is computed by summing all five dimension scores. Dimension scores are
assigned by the Advisor scan or by a human reviewer using the rubric as a
reference.

---

## Section 4: Advisor Integration

### 4.1 ops.runs Logging

Every agentic run must produce entries in two Supabase tables:

```sql
-- One row per run (created at PLAN phase start)
ops.runs: id, task_id, agent_id, triggered_by, status,
          plan_artifact, evidence_path, pr_url, score,
          created_at, updated_at

-- One row per step transition (created throughout the run)
ops.run_events: id, run_id, step, outcome, detail, created_at
```

The `agent_id` field must be one of the registered values:
- `copilot_coding_agent`
- `claude_code`
- `semantic_kernel`
- `autogen`
- `manual` (human-executed run following the same loop)

### 4.2 Findings Escalation

Advisor findings related to agentic coding run quality are escalated as follows:

| Rubric Score | Action |
|-------------|--------|
| 0–5 (Baseline) | Advisor finding: high severity — open Plane issue for loop remediation |
| 6–9 (Developing) | Advisor finding: medium severity — log in Ops Console, no immediate escalation |
| 10–12 (Established) | Informational: loop is healthy, log for trend tracking |
| 13–15 (Optimized) | Informational: exemplary run, no action required |

Advisor findings are logged to the Ops Console and linked to the `ops.runs.id`
of the run that produced them.

### 4.3 Score Thresholds

- **Block merge threshold**: Any run with a Dimension 5 (audit_trail) score of 0
  is flagged in the PR with a failing check. The PR cannot be merged until the
  ops.runs entry is created and the score is at least 1.
- **Escalation threshold**: Any run with a total score below 6 produces a
  high-severity Advisor finding that must be acknowledged in the Ops Console
  before the next agentic run is permitted on the same task.
- **Maturity regression threshold**: If the rolling 7-day average score for a
  given `agent_id` drops below 8, the Advisor notifies the platform team.

---

## Section 5: Non-Negotiable Rules

The following rules are absolute. No exception or override is permitted without
a manual review and explicit approval from the platform team lead.

### Rule 1: No "done" without passing verify

A run is not complete until all required CI gates exit 0 and their output is
saved as evidence artifacts. Marking a run as `status: completed` in ops.runs
before the VERIFY phase passes is a contract violation.

**Enforcement**: CI check on PR that validates ops.runs.evidence_path contains
all required log files.

### Rule 2: PR required for all code changes

Every file modification produced by an agentic run must be delivered via a PR.
Direct commits to `main`, `master`, or any protected branch by an agent are
forbidden. Branch protection enforces this at the platform level.

**Enforcement**: Organization-level ruleset (see `ssot/advisor/rulepacks/github_governance.yaml`,
rule `org_rulesets_default_branch`).

### Rule 3: ops.runs entry required before patch

The ops.runs entry must exist (status: running) before the first file in the
PATCH phase is modified. A PR that exists without a corresponding ops.runs entry
is a governance violation.

**Enforcement**: CI check on PR that validates a matching ops.runs.pr_url entry
exists via the Supabase REST API.

### Rule 4: No secrets in patches

Agentic patches must not introduce raw secrets, tokens, passwords, or credentials
into any file. Secret references use environment variable names or Supabase Vault
key names only.

**Enforcement**: Secret scanning CI check on every PR (gitleaks or trufflehog).

### Rule 5: Restricted path changes require human approval

Modifications to `ssot/`, `supabase/migrations/`, `.github/workflows/`, `infra/`,
or `.github/copilot-instructions.md` require a human reviewer to explicitly
approve the PR before merge. CODEOWNERS enforcement covers this.

**Enforcement**: CODEOWNERS file + required reviewers in branch protection ruleset.

---

## Section 6: Maturity Levels

Maturity is assessed based on the rolling average rubric score for all agentic
runs over the past 30 days for a given team or repository.

| Level | Score Range | Description |
|-------|-------------|-------------|
| Baseline | 0–5 | Ad-hoc agentic runs with no audit trail or PR discipline. Individual runs may work but the process is unreliable. ops.runs entries are absent or incomplete. |
| Developing | 6–9 | Most runs produce PRs but evidence is incomplete. ops.runs entries exist but ops.run_events step tracking is sparse. Gate coverage is partial. |
| Established | 10–12 | Consistent loop with ops.runs entries and passing verification on every run. PR evidence follows the output contract. Gate output is saved as artifacts. |
| Optimized | 13–15 | Full loop with automated evidence capture and regression prevention. ops.run_events covers every step. Rubric scoring is automated in the Ops Console. Rolling average score is stable above 12. |

**Target maturity**: The platform team target is **Established (10–12)** within
60 days of Copilot Coding Agent activation, and **Optimized (13–15)** within
180 days.

---

## References

| Resource | Path / URL |
|----------|-----------|
| Agent Runtimes catalog | `docs/architecture/AGENT_RUNTIMES.md` |
| Agentic Coding Rubric (SSOT) | `ssot/advisor/rubrics/agentic_coding.yaml` |
| Baseline Workbook | `ssot/advisor/workbooks/agentic_coding_baseline.yaml` |
| GitHub Copilot SDK SSOT | `ssot/integrations/github_copilot_sdk.yaml` |
| Microsoft Agent Framework SSOT | `ssot/integrations/microsoft_agent_framework.yaml` |
| GitHub Governance Rulepack | `ssot/advisor/rulepacks/github_governance.yaml` |
| Ops Advisor Contract | `docs/architecture/OPS_ADVISOR_CONTRACT.md` |
| Output contract (global) | `~/.claude/CLAUDE.md` — Output Contract section |
| Output contract (repo) | `CLAUDE.md` — Project Output Contract section |
| Secrets policy | `docs/architecture/SECRETS_POLICY.md` |
| Restricted paths | `docs/architecture/SSOT_BOUNDARIES.md` |
