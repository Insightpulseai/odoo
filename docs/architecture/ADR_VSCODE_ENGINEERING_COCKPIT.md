# ADR: VS Code Engineering Cockpit — Devcontainer-First, Repo-Scoped Settings

> **Status**: Accepted
> **Date**: 2026-03-17
> **Deciders**: CEO
> **Source**: `docs/research/wholesale-saas-erp-azure-architecture-study.md`

---

## Context

VS Code settings drift caused Python 3.11/3.12 venv mismatch, hardcoded local paths,
and conflicting language server overrides across workspace levels. The platform needs a
deterministic engineering cockpit that works identically for local dev, devcontainers,
and CI.

## Decision

### Core rules

1. **Repo-scoped settings own correctness** — runtime, debug, lint, and test configuration
   lives in workspace `.vscode/settings.json` files tracked in git.
2. **User settings own personal UX only** — font, color theme, UI layout. Never runtime config.
3. **Devcontainer is the runtime/tooling contract** — `devcontainer.json` pins Python ≥3.10,
   PostgreSQL ≥13, and all required tooling. This is the single source of truth for the
   development environment.
4. **No hardcoded local interpreter paths in tracked settings** — use `${workspaceFolder}`
   variables or devcontainer-relative paths exclusively.

### Settings hierarchy

| Location | What belongs there |
|----------|-------------------|
| User settings | Personal UX only (font, UI layout) |
| Root `.vscode/settings.json` | Repo-wide exclusions, formatters, YAML/JSON schemas, tooling toggles |
| `odoo/.vscode/settings.json` | Python interpreter (devcontainer), Odoo lint paths, debug defaults |
| Nested frontend `.vscode/` | TypeScript/Node version, formatter/linter settings |
| **Banned** | Hardcoded pyenv paths, machine-specific filesystem paths, explicit `python.languageServer` overrides |

### Target capabilities

| Capability | Workspace scope |
|-----------|-----------------|
| Deterministic Odoo runtime (Python ≥3.10, PG ≥13) | `odoo/` devcontainer |
| Addon import resolution (`addons-path` ordering) | `odoo/.vscode/` |
| Ruff linting (Odoo PEP8 exceptions) | repo root config |
| YAML/JSON schema support | root `.vscode/settings.json` |
| Monorepo performance (`watcherExclude`, `search.exclude`) | root `.vscode/settings.json` |
| Debug/test tasks | root + `odoo/` |
| Pipeline authoring (GHA + Azure Pipelines) | root |

## Consequences

- All VS Code settings PRs must pass: no hardcoded local paths, no `python.languageServer`
  overrides, no user-scope leaks of runtime config
- Devcontainer image updates require testing against Odoo 19 source install constraints
- Python 3.11 is the repo standard (matches pyenv `odoo-19-dev` virtualenv)
- New workspace folders must inherit root settings or document overrides

## Alternatives considered

| Alternative | Why rejected |
|-------------|-------------|
| No devcontainer (native-only dev) | "Works on my machine" drift; Odoo has strict PG/Python deps |
| User-scope runtime settings | Invisible to CI, causes cross-developer inconsistency |
| Pylance as explicit language server override | Conflicted across workspace levels; let VS Code auto-detect |

---

*Accepted 2026-03-17.*
