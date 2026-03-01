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

## PR Atomicity (enforced by Vercel Agent review)

One PR = one logical unit. Flag (do not merge) any PR that mixes:

| Mixed in same PR | Why it's banned |
|-----------------|-----------------|
| SQL migrations + Edge Functions | Merge order dependency; migrations must land first |
| SSOT YAML + runtime code (`.ts`, `.py`) | SSOT files are policy; runtime is implementation |
| Odoo modules + Supabase migrations | Different deployment surfaces |
| Multiple unrelated feature domains | Contaminates git history and makes rollback harder |

Cross-branch contamination check: if a PR's file set spans more than one of
`supabase/migrations/`, `supabase/functions/`, `apps/`, `addons/`, `ssot/` —
it is likely contaminated and must be split before merge.

## Vercel Agent PR Review (advisory signals)

When `@vercel` suggestions appear in PR comments:
- Apply **only** sandbox-validated suggestions (Vercel suppresses ones that fail builds).
- Suggestions that modify files in `ssot/` must be **rejected** — SSOT is human/CI-only.
- Suggestions that introduce inline secrets must be **rejected** — use Vault refs.
- Log acted-upon suggestions into `ops.run_events` for audit trail.
- On-demand invocation: `@vercel run a review`, `@vercel fix the type errors`.
- Advisory only: Vercel Agent is not authoritative; CI gates are the source of truth.

### Conflict resolution via Vercel Agent

Vercel Agent can propose patches for merge conflicts and sandbox-validate them, but
**cannot resolve conflicts at the git plumbing level** — a commit is still required.

**Use it for** (high effectiveness): `apps/**/*.ts`, `docs/**/*.md`, `ssot/**/*.yaml`
**Avoid relying on it for**: `supabase/migrations/**`, `addons/oca/**`, `*.lock`, generated files

**@vercel prompts for conflict resolution:**
```
@vercel resolve the merge conflicts and keep ssot/ boundary rules intact
@vercel resolve conflicts in ssot/** and docs/**; do not touch addons/**
@vercel fix the merge conflicts in apps/ keeping existing import paths
```

**Post-resolution checklist before merging:**
- [ ] `python scripts/ci/check_repo_structure.py` passes
- [ ] SSOT invariants preserved (no keys removed/renamed without intention)
- [ ] No UI-only steps introduced by the resolution
- [ ] `pnpm lint && pnpm typecheck` pass if TS files were touched

## What "Done" Means

A task is complete only when:
- SSOT validators pass (`python scripts/ci/check_repo_structure.py`)
- Tests/linters pass
- PR exists with evidence attached
- PR contains exactly one logical unit (atomicity check above)
- No residual `TODO` left in production code paths
