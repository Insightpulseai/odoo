# Branch Hygiene Runbook

> Enforce clean branches before PRs. A dirty working tree when opening a PR
> creates ambiguity about what is "done" vs "local-only."

---

## Rules

1. **One PR, one concern.** Keep branch scope tight — secrets policy changes
   should not include unrelated spec bundles.

2. **Feature branches only.** Never commit directly to `main`.

3. **Commit before PR open.** All intended changes must be committed and pushed
   before running `gh pr create`.

4. **Verify diff before PR open.**
   ```bash
   git diff origin/main..HEAD --name-only
   ```
   Expected: only the files intended for this PR.

5. **Delete branch after merge.** No stale remote refs.

---

## PR creation gate

**Never open a PR with a dirty working tree.**

If `gh pr create` warns about uncommitted changes:

1. Run `git status --short` and classify every `??` / `M` entry:
   - **Intended for this PR** → stage and commit, then re-push
   - **Unrelated work** → spin a new branch, commit there
   - **Pre-existing untracked noise** → safe to ignore (they won't appear
     in the PR diff); document it in the PR description

2. Verify the PR diff is scoped correctly:
   ```bash
   git diff origin/main..HEAD --name-only
   ```

3. Re-open (or update) the PR only when `git diff` matches intent.

**Expectation: `git diff origin/main..HEAD --name-only` is clean and scoped
before the PR is considered ready for review.**

---

## Diagnosing "uncommitted changes" warnings from `gh pr create`

`gh pr create` counts **all** untracked files (`??`) in the working tree, not
just files changed on the current branch. A large monorepo will always produce
this warning — it does **not** automatically mean those files are in the PR diff.

**Interpret `git status --short` output like this:**

| Prefix | Meaning | Required action before PR |
|--------|---------|---------------------------|
| `??` | Untracked (never committed) | Safe if absent from PR diff — confirm with `git diff origin/main..HEAD` |
| `M` | Tracked file modified | **Must** be committed (if intended) or `git restore`d (if accidental) |
| `A` | Staged new file | **Must** be committed (if intended) or `git restore --staged` (if accidental) |
| `D` | Tracked file deleted | **Must** be committed (if intended) or `git restore`d (if accidental) |

**Rule: `M`/`A`/`D` entries are never safe to leave at PR open time.
`??` entries are safe only after confirming the PR diff.**

**Quick check:**
```bash
# Ground truth — what will actually merge:
git diff origin/main..HEAD --name-only

# Tracked modifications (must be zero before merging):
git status --short | grep -v '^??'

# Untracked noise (safe if absent from PR diff):
git status --short | grep '^??'
```

---

## Common patterns

| Scenario | Action |
|----------|--------|
| `??` files pre-date the branch | Confirm absent from PR diff — then safe to ignore |
| `M` (modified tracked file) intended | `git add <file>` → commit → push |
| `M` (modified tracked file) accidental | `git restore <file>` |
| `A` (staged new file) accidental | `git restore --staged <file>` |
| `D` (deleted tracked file) accidental | `git restore <file>` |
| New work accidentally on wrong branch | `git stash` → checkout correct branch → `git stash pop` |
| Large unrelated tree needs its own PR | `git checkout -b chore/cleanup-<scope>` → stage → commit → push → PR |

---

---

## Automated Branch Pruning

### Policy SSOT

`ssot/policy/branch_hygiene.yaml` — canonical source for retention days, candidate prefixes, and protected patterns.

### How it works

Workflow: `.github/workflows/branch-hygiene.yml`
Script: `scripts/ci/branch_hygiene.py`

Triggers:
- **Nightly** at 03:00 UTC (scheduled, dry-run unless policy changed)
- **Manual** via workflow_dispatch (set `dry_run: false` to actually delete)

Algorithm:
1. List all remote branches via GitHub API
2. Filter to candidate prefixes (`claude/`, `codex/`, `bot/`, `dependabot/`, `renovate/`)
3. Skip any branch with an open PR (draft or review-ready)
4. Skip any branch newer than `max_age_days` (default 14)
5. Skip all protected patterns (`main`, `release/`, `hotfix/`, `chore/`, `feat/`, etc.)
6. Delete (or log in dry-run) remaining branches

### Candidate prefixes (auto-delete)

| Prefix | Source | Notes |
|--------|--------|-------|
| `claude/` | Claude Code agent | All agent-generated branches |
| `codex/` | OpenAI Codex agent | — |
| `bot/` | GitHub Apps / bots | e.g. `bot/sync-anthropic-skills` |
| `dependabot/` | Dependabot | Closed-PR orphans only |
| `renovate/` | Renovate | Same as dependabot |

### Protected — never deleted

All other prefixes and patterns are **never** auto-deleted:
`main`, `master`, `develop`, `release/*`, `hotfix/*`, `chore/*`, `feat/*`, `fix/*`, `docs/*`, `test/*`, `refactor/*`

Any branch with an open PR (regardless of prefix) is also protected.

### To run manually

```bash
# Dry run (view what would be deleted)
gh workflow run branch-hygiene.yml -f dry_run=true -f older_than_days=14

# Live deletion (14-day cutoff)
gh workflow run branch-hygiene.yml -f dry_run=false -f older_than_days=14

# Local dry run
REPO=Insightpulseai/odoo DRY_RUN=true MAX_AGE_DAYS=14 \
  GH_TOKEN=$(gh auth token) python3 scripts/ci/branch_hygiene.py
```

### Report artifact

Every run uploads `reports/ci/branch_hygiene_report.json` as a GitHub Actions artifact (`branch-hygiene-report-<run_number>`, retained 30 days).

### To exempt a branch from pruning

Either:
1. Open a PR against it (even a draft), **or**
2. Add its prefix to `protected_patterns` in `ssot/policy/branch_hygiene.yaml`

---

## Related

- `CLAUDE.md` § Git Workflow (no direct commits to main, feature branches)
- `ssot/policy/branch_hygiene.yaml` — automated pruning policy
- `.github/workflows/branch-hygiene.yml` — nightly pruning workflow
- `scripts/ci/branch_hygiene.py` — pruning implementation
- `scripts/repo_health.sh` — run before opening PRs
- `scripts/git_state_preflight.sh` — pre-flight checklist for branch state
