# CLAUDE.md — `<repo-name>` (starter template)

> Slim operator's index for Claude Code / repo-local AI. Copy this file to
> your repo root, replace `<placeholders>`, and delete any section that
> doesn't apply. Keep under ~200 lines.

**Project identity**: `<repo-name>`
**Owner (business)**: `<name_or_role>`
**Owner (technical)**: `<name_or_role>`
**Last updated**: `<YYYY-MM-DD>`

---

## Project identity

One paragraph: what is this repo, who uses it, what surface does it ship?

---

## Architecture summary (3–5 bullets)

- Stack: `<primary stack>`
- Runtime: `<Azure Container Apps / App Service / etc.>`
- Data: `<PostgreSQL / Databricks / etc.>`
- CI/CD: `<Azure Pipelines canonical>`
- Related monorepo SSOTs: `<pointers>`

---

## Source of truth map

| Concern | Authority |
|---|---|
| Architecture | `docs/architecture/*.md` |
| SSOT invariants | `ssot/**/*.yaml` |
| Path-scoped rules | `.claude/rules/*.md` |
| Specs | `spec/<slug>/{constitution,prd,plan,tasks}.md` |
| Operating standard | `docs/operating/CLAUDE_CODE_OPERATING_STANDARD.md` |
| Runbooks | `docs/runbooks/*.md` |
| Evidence | `docs/evidence/<YYYYMMDD-HHMM>/<scope>/` |

---

## Coding conventions

- Language primary: `<Python 3.12 / TypeScript / etc.>`
- Style: `<ruff + mypy / prettier + eslint / etc.>`
- Tests: `<pytest / vitest / etc.>`
- Package manager: `<uv / pnpm / npm workspaces>`
- Build tool: `<uv / turbo / etc.>`

---

## Test expectations

- Unit tests required for every new module
- Contract tests required for SSOT changes
- Integration tests required for external-system touch
- Smoke test must pass before merge
- Eval harness required for AI-surface changes

---

## Deployment rules

- **Deploy authority**: Azure Pipelines (never GHA; per CLAUDE.md parent doctrine)
- **Environments**: `<dev / staging / prod>`
- **Promotion**: PR → merge → CI → auto-deploy to dev → manual approval to staging → manual approval to prod
- **Rollback**: tested in preprod before any prod deploy

---

## Safety rules

- No hardcoded secrets (Key Vault + Managed Identity only)
- No deprecated services (see parent `CLAUDE.md` deprecation list)
- No destructive commands without approval (`rm -rf`, `git push --force`, `DROP TABLE`, etc.)
- No `--no-verify` on git
- No proactive documentation file creation
- Every edit preserves the existing coding style

---

## Approval boundaries

| Action | Approval needed |
|---|---|
| Any prod deploy | Yes (named approver) |
| Any destructive git operation | Yes |
| Any shared-state mutation (Slack / Teams / external service) | Yes |
| Local dev changes | No |
| Refactor within a file | No |
| New test | No |

---

## Agent commands

| Command | Purpose |
|---|---|
| `/project:plan` | Create implementation plan |
| `/project:implement` | Execute plan |
| `/project:verify` | Run verification |
| `/project:ship` | Full workflow end-to-end |
| `/project:fix-github-issue` | Fix a specific issue |

---

## Operating standard

See `docs/operating/CLAUDE_CODE_OPERATING_STANDARD.md` for canonical operating rules (authority order, startup routine, escalation, forbidden shortcuts).

---

## Commit convention

```
feat|fix|refactor|docs|test|chore(scope): description
```

Trailer required on every commit:
```
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Deprecated (never use)

List any repo-specific deprecated tooling here. Reference parent monorepo `CLAUDE.md` deprecation list for the canonical set.

---

## References

- Parent monorepo CLAUDE.md: `../../CLAUDE.md` (if this repo is in a monorepo)
- Operating standard: `docs/operating/CLAUDE_CODE_OPERATING_STANDARD.md`
- Subagent catalog: `templates/claude/SUBAGENT_CATALOG.md`
- Unified capability template: `spec/_templates/unified-capability-template.md`
