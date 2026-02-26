# Repo Layout Migration Backlog

> **Purpose**: Track top-level directory sprawl reduction.
> **Reference**: `docs/architecture/CANONICAL_MONOREPO_LAYOUT.md`
> **Rule**: NO changes to `web/` or `apps/` without an approved spec bundle in `spec/repo-layout-*/`.

---

## Completed (chore(repo): reduce top-level dir sprawl — Tier 0–2)

- [x] `.gitignore`: add transient dev artifacts (`.pnpm-store/`, `.worktrees/`, `.pytest_cache/`)
- [x] `.agent/` merged into canonical `agents/` directory
  - 3 entrypoints updated in `agents/registry/agents.yaml`
  - Removed stale `.agent` scan target from `.github/workflows/policy-no-cli.yml`
- [x] `design-tokens/` → `design/tokens/` (tokens.json) + `design/figma/` (figma exports)

---

## Tier 3 — Medium risk (needs spec bundle before action)

- [ ] `templates/` — evaluate each: is it a scaffold or a deployable app?
  - Several templates may belong under `apps/` or a new `scaffolds/` root
  - Requires: inventory of which are actively used vs archived
- [ ] `platform/` — split:
  - `platform/vercel-integrations/` → `infra/vercel/`
  - `platform/advisor/` → `apps/advisor/`
  - Requires: check if any CI workflow references `platform/` directly

---

## Tier 4 — High risk (needs dedicated spec + CI migration plan)

### `web/` — DO NOT TOUCH without approved spec

> **Risk**: CATASTROPHIC — ~40+ CI workflow references, pnpm-workspace.yaml `"web/*"` pattern,
> DevContainer bind-mount at `/workspaces/odoo`, multiple Vercel projects rooted here.

- [ ] `web/` restructure: ~36 subdirs, 40+ CI workflow refs, pnpm-workspace.yaml coupling
  - Required spec: `spec/repo-layout-web-migration/`
  - Pre-work: audit all `.github/workflows/` for `web/` path filters
  - Pre-work: audit `pnpm-workspace.yaml` for `"web/*"` pattern implications
  - Pre-work: audit `vercel.json` and Vercel project roots

### `apps/` — DO NOT TOUCH without audit

> **Risk**: HIGH — Electron app (`colima-desktop`) split across `web/apps/` and `apps/`,
> iOS app at `apps/odoo-mobile-ios/`, CI workflow references.

- [ ] `apps/` consolidation: colima-desktop split needs iOS/Electron audit first
  - Required: inventory `apps/` vs `web/apps/` for all app types
  - Required spec: `spec/repo-layout-apps-migration/`

---

## Canonical Structure Target

```
/
├── addons/          # Odoo modules (odoo/, oca/, ipai/)
├── agents/          # AI agent configs, skills, personas  ← was .agent/ + agents/
├── apps/            # Deployable applications
├── config/          # Runtime configuration
├── design/          # Design tokens, figma exports        ← was design-tokens/
├── docs/            # Documentation
├── infra/           # Infrastructure as code
├── mcp/             # MCP servers
├── packages/        # Shared libraries
├── platform/        # Platform integrations (→ Tier 3)
├── runtime/         # Runtime patches and scripts
├── scripts/         # Automation scripts
├── spec/            # Spec bundles
├── ssot/            # SSOT maps, policy matrices
├── supabase/        # Supabase functions and migrations
├── templates/       # Scaffold templates (→ Tier 3)
└── web/             # Web applications (→ Tier 4, do not restructure)
```

---

*Last updated: 2026-02-27 | Maintained in `Insightpulseai/odoo`*
