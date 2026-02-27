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

## Related

- `CLAUDE.md` § Git Workflow (no direct commits to main, feature branches)
- `scripts/repo_health.sh` — run before opening PRs
- `scripts/git_state_preflight.sh` — pre-flight checklist for branch state
