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

### Safety model (two locks)

| Trigger | Behavior |
|---------|----------|
| Scheduled (nightly) | **Report-only** — Lock 1 forces `DRY_RUN=true` at the workflow layer; no branches are ever deleted |
| `workflow_dispatch` with `dry_run=true` (default) | Report-only — same as schedule |
| `workflow_dispatch` with `dry_run=false` + `confirm=YES` | **Live deletions** — both locks satisfied; candidates are deleted |
| `workflow_dispatch` with `dry_run=false` + no/wrong confirm | Refused — script exits with code 4 (`REFUSING_DELETE`) |

**Lock 1 (workflow)**: `branch-hygiene.yml` unconditionally sets `DRY_RUN=true` for all `schedule` events.

**Lock 2 (script)**: `branch_hygiene.py` refuses any deletion unless `--confirm=YES` is passed. This check runs before any API call; a wrong or missing value exits(4) immediately.

### Policy SSOT

`ssot/policy/branch_hygiene.yaml` — canonical source for retention days, candidate prefixes, and protected patterns.

### How it works

Workflow: `.github/workflows/branch-hygiene.yml`
Script: `scripts/ci/branch_hygiene.py`

Triggers:
- **Nightly at 03:00 UTC** (report-only — never deletes)
- **Manual** via `workflow_dispatch` (deletions only when `dry_run=false` + `confirm=YES`)

Algorithm:
1. List all remote branches via paginated GitHub API
2. Check exact protected names (`main`, `master`, `develop`, `gh-pages`) — skip
3. Check protected prefixes (`release/`, `hotfix/`, `chore/`, `feat/`, `fix/`, etc.) — skip
4. Filter to candidate prefixes only (`claude/`, `codex/`, `bot/`, `dependabot/`, `renovate/`)
5. Skip branches newer than `max_age_days` (default: 14)
6. Open-PR guard — skip any candidate with an open PR (draft or review-ready)
7. Delete (live) or report (dry-run) remaining candidates

### Candidate prefixes (auto-delete eligible)

| Prefix | Source | Default retention |
|--------|--------|-------------------|
| `claude/` | Claude Code agent | 7 days |
| `codex/` | OpenAI Codex | 7 days |
| `bot/` | GitHub Apps / bots | 7 days |
| `dependabot/` | Dependabot | 14 days |
| `renovate/` | Renovate Bot | 14 days |

### Protected — never deleted

```
Exact:    main, master, develop, gh-pages
Prefix:   release/  hotfix/  prod/  staging/
          chore/  feat/  fix/  docs/  test/  refactor/
+ Any branch with an open PR (regardless of prefix or age)
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success (including clean dry-run) |
| 2 | Misconfiguration (missing `REPO` env var) |
| 3 | API failure (could not list branches or delete failed) |
| 4 | Refused unsafe delete (`--dry-run=false` without `--confirm=YES`) |

### Running via workflow_dispatch

```bash
# View what would be deleted (safe — no deletions)
gh workflow run branch-hygiene.yml \
  -f dry_run=true \
  -f older_than_days=14

# Live deletion — requires confirm=YES (human intent required)
gh workflow run branch-hygiene.yml \
  -f dry_run=false \
  -f confirm=YES \
  -f older_than_days=14
```

### Running locally

```bash
# Dry run — report only
REPO=Insightpulseai/odoo DRY_RUN=true MAX_AGE_DAYS=14 \
  GH_TOKEN=$(gh auth token) \
  python3 scripts/ci/branch_hygiene.py --dry-run=true

# Live run — double lock enforced by script
REPO=Insightpulseai/odoo DRY_RUN=false MAX_AGE_DAYS=14 \
  GH_TOKEN=$(gh auth token) \
  python3 scripts/ci/branch_hygiene.py --dry-run=false --confirm=YES
```

### Report artifact

Every run writes `reports/ci/branch_hygiene_report.json` and uploads it as the
GitHub Actions artifact `branch-hygiene-report` (stable name, overwritten each run,
retained 30 days). A structured job summary is also written to the Actions UI.

### To exempt a branch from pruning

Either:
1. Open a PR against it (even a draft), **or**
2. Add the exact name to `excluded_branches` or its prefix to `protected_prefixes`
   in `ssot/policy/branch_hygiene.yaml`

---

## Related

- `CLAUDE.md` § Git Workflow (no direct commits to main, feature branches)
- `ssot/policy/branch_hygiene.yaml` — automated pruning policy
- `.github/workflows/branch-hygiene.yml` — nightly pruning workflow
- `scripts/ci/branch_hygiene.py` — pruning implementation
- `scripts/repo_health.sh` — run before opening PRs
- `scripts/git_state_preflight.sh` — pre-flight checklist for branch state
