# GitHub Copilot Instructions (Repo-level)

This file is loaded automatically by GitHub Copilot for all contributors.
Priority: repo-level instructions override personal settings.

---

## Directory Boundaries

Respect these strict directory boundaries at all times:

| Directory | Contains | Do NOT place |
|-----------|----------|--------------|
| `addons/ipai/` | Custom Odoo modules (`ipai_*`) | Non-Odoo code |
| `addons/oca/` | OCA submodules | Modified OCA source (override with `ipai_*` instead) |
| `supabase/` | Migrations, Edge Functions, seeds | Business logic not tied to Supabase |
| `apps/` | Deployable applications | Odoo modules or Supabase migrations |
| `packages/` | Shared libraries | App-specific code |
| `ssot/` | YAML-only policy/config registry | Executable code (`.py`, `.ts`, `.sh`, `.sql`) |
| `spec/` | Spec bundles for product requirements | Implementation code |
| `docs/` | Documentation and contracts | Source code |

## SSOT Rules

- All platform posture lives in `ssot/` as YAML.
- Never hardcode secrets: reference `ssot/secrets/registry.yaml` identifiers only.
- Generated files are listed in `docs/architecture/REPO_LAYOUT.md` — edit the upstream source, not the output.
- New cross-domain features require a contract doc in `docs/architecture/` (Rule 9).

## Odoo Module Rules

- Prefer `Config → OCA → ipai_*` in that order.
- Never modify OCA source directly — use `_inherit` overrides in `addons/ipai/`.
- Enterprise modules are forbidden; `ipai_*` must not depend on EE-only prefixes.
- Naming: `ipai_<domain>_<feature>` (e.g. `ipai_finance_ppm`, `ipai_ai_tools`).

## Supabase Rules

- All schema changes via migrations in `supabase/migrations/` — no dashboard ad-hoc SQL.
- `ops.*` tables are append-only (no DROP/TRUNCATE).
- Secrets stay in Supabase Vault; never in function code.

## Agentic Loop (when running as a coding agent)

Every code-changing run must follow:
1. **Plan**: identify impacted files; record `ops.runs` entry.
2. **Patch**: make minimal targeted edits; repo-first (no UI-only steps).
3. **Verify**: run tests and SSOT validators; capture logs.
4. **PR**: open/update PR with summary + evidence links + residual risk.

Never claim "done" without a passing verification step.

## Commit Convention

```
feat|fix|refactor|docs|test|chore(scope): description
```

Scopes: `oca`, `repo`, `ci`, `deps`, `deploy`, `ssot`, `advisor`, `devex`

## What "Done" Means

A task is complete only when:
- SSOT validators pass (`python scripts/ci/check_repo_structure.py`)
- Tests/linters pass
- PR exists with evidence attached
- No residual `TODO` left in production code paths
