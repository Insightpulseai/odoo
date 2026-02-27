# Branch Hygiene — Insightpulseai/odoo

## Rules

1. **One feature = one branch = one PR.**
2. No long-lived `claude/*` branches without a PR within 24 h of the first commit.
3. **Merge order** (to keep main stable):
   - Unblock prod (`fix/*`) → infra/CI gates (`chore/ci/*`) → features (`feat/*`) → deps bumps (`dependabot/*` batched)
4. Squash-merge preferred; preserve multi-commit history only for refactors with meaningful per-commit messages.
5. Delete branch after merge (no stale remote refs).

## Naming

| Type | Pattern | Example |
|------|---------|---------|
| Bug fix | `fix/<area>-<slug>` | `fix/mail-zoho-transport` |
| Feature | `feat/<area>-<slug>` | `feat/omc-company-scope` |
| Chore | `chore/<area>-<slug>` | `chore/deps-batch-20260227` |
| Claude agent | `claude/<slug>-<hash>` | `claude/add-service-health-checks-Jqvz8` |
| Docs | `docs/<slug>` | `docs/monorepo-contract` |

## Cleanup procedure

```bash
# After a PR is merged, delete the remote branch:
git push origin --delete <branch-name>

# Prune stale remote-tracking refs locally:
git fetch --prune

# List all remote branches older than 30 days with no associated open PR:
git for-each-ref --sort=-committerdate --format='%(refname:short) %(committerdate:relative)' refs/remotes/origin/ \
  | grep -v 'HEAD\|main'
```

## Dependabot batching

Individual dependabot PRs should be batched before merging:

```bash
# Create a batch branch from main
git checkout main && git pull
git checkout -b chore/deps-batch-$(date +%Y%m%d)

# Cherry-pick each dependabot commit
git cherry-pick <sha1> <sha2> ...

# Open a single PR that closes all individual ones
gh pr create --title "chore(deps): batch dependency updates" \
  --body "Closes #NNN, #NNN, ..."
```

Close the individual Dependabot PRs after the batch PR merges.

## Agent branch policy

`claude/*` branches are created by the Claude Code agent. Rules:

- If the branch has been merged into main: **delete it**.
- If the branch has no open PR after 24 h: open a PR or delete the branch.
- CI nightly audit (`branch-hygiene.yml`) tracks branches older than 7 days without a PR.

## Nightly hygiene audit

See `.github/workflows/branch-hygiene.yml` — runs nightly, opens/updates a
GitHub issue listing `claude/*` and feature branches older than 7 days with no
associated open PR. **No branches are auto-deleted** — this is tracking only.
