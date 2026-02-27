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

## Diagnosing "144 uncommitted changes" style warnings

`gh pr create` counts **all** untracked files (`??`) in the working tree, not
just files changed on the current branch. A large monorepo with many in-progress
local files will always produce this warning — it does **not** mean those files
are in the PR diff.

**Quick check:**
```bash
# What is actually in the PR diff?
git diff origin/main..HEAD --name-only

# What is untracked (not in any commit)?
git status --short | grep '^??'
```

The PR diff is the ground truth. Untracked files are local-only unless explicitly
committed and pushed.

---

## Common patterns

| Scenario | Action |
|----------|--------|
| `??` files pre-date the branch | Ignore — not in PR diff |
| `M` (modified tracked file) not intended | `git restore <file>` |
| New work accidentally on wrong branch | `git stash` → checkout correct branch → `git stash pop` |
| Large unrelated tree needs its own PR | `git checkout -b chore/cleanup-<scope>` → stage → commit → push → PR |

---

## Related

- `CLAUDE.md` § Git Workflow (no direct commits to main, feature branches)
- `scripts/repo_health.sh` — run before opening PRs
- `scripts/git_state_preflight.sh` — pre-flight checklist for branch state
