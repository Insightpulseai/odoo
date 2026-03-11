# Allowed Operations — GitHub CLI

## Read-only (always safe)

- `gh pr list`, `gh pr view`, `gh pr checks`, `gh pr diff`
- `gh issue list`, `gh issue view`
- `gh run list`, `gh run view`, `gh run watch`
- `gh repo view`
- `gh api <GET endpoints>`

## Controlled write (requires verification after)

- `gh pr create` — creates pull request
- `gh pr merge` — merges after review
- `gh pr comment` — adds comment
- `gh issue create` — creates issue
- `gh issue close` — closes issue
- `gh workflow run` — triggers workflow dispatch
- `gh release create` — creates tagged release

## Blocked by default

- `gh repo delete` — destructive
- `gh release delete` — destructive
- `gh repo archive` — destructive
- `git push --force` — destructive
- `gh auth login` — bootstrap only
- `gh repo create` — use through separate workflow
