# GitHub CLI Safe Skill

## Purpose

Interact with GitHub through the `gh` CLI in non-interactive mode.
Scoped to PR/issue operations, workflow dispatch, and status checks.

## Preconditions

- `gh` CLI installed
- Authenticated via `gh auth status`
- Repository context available (inside a git repo or `--repo` specified)

## Allowed operations

### Read-only
- `gh pr list`, `gh pr view`, `gh pr checks`
- `gh issue list`, `gh issue view`
- `gh run list`, `gh run view`
- `gh api repos/<owner>/<repo>/...` (GET)
- `gh repo view`

### Controlled write
- `gh pr create`, `gh pr merge` (with review)
- `gh issue create`, `gh issue close`
- `gh workflow run` (trigger dispatch)
- `gh pr comment`, `gh issue comment`
- `gh release create` (tagged release)

## Disallowed operations

- `gh repo delete` — destructive
- `gh release delete` — destructive
- `git push --force` via gh — destructive
- `gh auth login` — bootstrap only
- `gh repo create` — use through separate workflow

## Output contract

- Use `--json` flag for structured output where available
- Prefer `gh api` with `-q` (jq filter) for complex queries

## Verification contract

```bash
# After PR creation:
gh pr view <number> --json state,url --jq '.state'
# Expected: "OPEN"

# After workflow dispatch:
gh run list --workflow <name> --limit 1 --json status --jq '.[0].status'
# Expected: "in_progress" or "completed"
```
