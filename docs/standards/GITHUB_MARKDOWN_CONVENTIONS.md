# GitHub Markdown Conventions

Canonical source: [`ssot/governance/github-markdown-conventions.yaml`](../../ssot/governance/github-markdown-conventions.yaml)

## Scope

Applies to:

- README files
- Architecture docs (`docs/architecture/`)
- Runbooks (`docs/runbooks/`)
- Spec bundles (`spec/`)
- Issue and PR templates where applicable
- Contributor guides

Does not apply to generated Markdown, auto-exported notebooks, or vendored upstream docs.

## Rules

- Use relative links for files and images within the same repository.
- Use fenced code blocks with language tags whenever possible.
- Keep heading depth shallow and stable (default max depth: 3).
- Use task lists for executable work tracking.
- Use alerts sparingly and never stack multiple alerts back-to-back.
- Prefer standard heading anchors over custom HTML anchors.
- Use inline code for paths, commands, identifiers, and environment variables.
- Avoid decorative formatting in formal technical documentation.
- No team mentions in permanent docs (acceptable in issues/PRs only).
- No absolute GitHub blob URLs for files in the same repo.

## Examples

### Relative links

```markdown
[Architecture map](../architecture/REPO_SSOT_MAP.md)
```

Not:

```markdown
[Architecture map](https://github.com/Insightpulse-ai/odoo/blob/main/docs/architecture/REPO_SSOT_MAP.md)
```

### Code fences

````markdown
```yaml
key: value
```
````

### Alerts

```markdown
> [!IMPORTANT]
> This repo is not the runtime authority. See `platform/ssot/...`.
```

Allowed types: `NOTE`, `TIP`, `IMPORTANT`, `WARNING`, `CAUTION`. Max consecutive: 1. Preferred max per doc: 2.

### Task lists

```markdown
- [ ] Add OIDC federated credential
- [ ] Publish GHCR image
- [ ] Validate ACA revision health
```

## Per-artifact guidance

### README.md

- Purpose, repo boundaries, quickstart, canonical links, key commands, runtime topology summary.
- Avoid tutorial-length walkthroughs and full architecture dumps.

### Architecture docs

- Headings, sparse alerts, diagrams with relative links, code fences for contracts, footnotes for caveats.
- Avoid speculative roadmaps (use `spec/` instead).

### Runbooks

- Task lists for steps, fenced code blocks for commands, alerts for destructive steps.
- Required: owner, last_updated, preconditions, postconditions, rollback.

### Spec bundles

- Task lists, stable heading hierarchy, relative links across constitution / PRD / plan / tasks.
- Minimal styling, maximum scannability.

### Issues and PRs

- Task lists, team mentions, issue references (`#123`), alerts where the template renders well.

## Enforcement

- Linting: `markdownlint-cli2` (primary) or `remark-lint`.
- Link validation pre-merge: relative link resolution.
- Broken external link audit runs on schedule, not as pre-merge blocker.
- Docs link check is permitted under the GHA scoped exception — see [`ssot/governance/gha-scoped-exception.yaml`](../../ssot/governance/gha-scoped-exception.yaml).

## Review checklist

- [ ] Headings follow stable hierarchy (no skipped levels)
- [ ] In-repo links are relative
- [ ] Code fences have language tags
- [ ] Alerts used sparingly, none stacked back-to-back
- [ ] No team mentions in permanent docs
- [ ] No absolute GitHub blob URLs for in-repo files
- [ ] Images have alt text

## Non-goals

- Does not dictate prose style (voice, tone).
- Does not prescribe a diagram tool (Mermaid, drawio, Figma all acceptable).
- Does not enforce line-length — reader viewport is the constraint.
- Does not block legitimate raw HTML for documented edge cases.

## Related

- [GitHub operating layers](../../ssot/governance/github-operating-layers.yaml)
- [VS Code operating profile](../../ssot/governance/vscode-operating-profile.yaml)
- [Unified capability template authority](../../ssot/governance/unified-capability-template-authority.yaml)
