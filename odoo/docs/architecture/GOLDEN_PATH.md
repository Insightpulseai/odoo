# Golden Path — Platform Engineering Contract

> **SSOT for: what lives where, what gates apply, and how changes ship.**
> All apps, packages, and platform services must follow this contract.

---

## 1. Monorepo Boundaries

### Surface map

| Directory | Kind | Deployable | CI Gates |
|-----------|------|-----------|---------|
| `apps/*` | Application | Yes (Vercel / DO App Platform) | App-specific + always-on policy gates |
| `packages/*` | Shared library | No (consumed by apps) | Type-check + unit tests |
| `addons/ipai/*` | Odoo module | Yes (Odoo restart) | Odoo convention + OCA lint |
| `addons/oca/*` | OCA module (read-only submodule) | Yes (same) | — |
| `scripts/*` | Automation script | No | shellcheck (advisory) |
| `infra/*` | IaC / config | Via CI | Terraform plan + DNS sync check |
| `docs/*` | Documentation | No | Spell/lint (advisory) |

### Rule: no cross-boundary imports

- `apps/*` may import from `packages/*` via `workspace:*` (pnpm) or npm path.
- `packages/*` must **not** import from `apps/*`.
- `addons/*` are Odoo-only — no imports from `apps/` or `packages/`.

---

## 2. App Registration Requirements

Before a new app is deployable, it must satisfy:

| Requirement | File / Check |
|-------------|-------------|
| Registered in `pnpm-workspace.yaml` | `packages:` includes `apps/*` |
| Unique package name in `package.json` | No collisions in workspace |
| `vercel.json` present with `ignoreCommand` | Skip unaffected builds |
| `.vercelignore` scoped to app root | No stale monorepo paths in bundle |
| Path-filtered CI workflows | `.github/workflows/<app>-check.yml` etc. |
| Runbook in `docs/ops/` | `VERCEL_<APP>.md` or `DO_<APP>.md` |

---

## 3. Required Gates (always-on)

These gates apply to **every PR**, regardless of changed paths:

| Gate | Workflow | What it enforces |
|------|----------|-----------------|
| Spec Bundle Presence | `.github/workflows/policy-gates.yml` | `feat/*` with >3 scoped changes needs `spec/<slug>/` |
| Secret Pattern Diff | `policy-gates.yml` | No hardcoded secrets in diff |
| Odoo 19 View Convention | `policy-gates.yml` | `<list>` not `<tree>` |
| Migration RLS Contract | `policy-gates.yml` | New tables must `ENABLE ROW LEVEL SECURITY` |
| Deprecated Reference Block | `policy-gates.yml` | No `.net`, Mattermost, Mailgun, Appfine references |
| Agent Instructions Drift | `.github/workflows/agent-instructions-drift.yml` | CLAUDE.md/AGENTS.md/GEMINI.md in sync with SSOT |
| DNS Sync Check | `.github/workflows/dns-sync-check.yml` | `infra/dns/subdomain-registry.yaml` artifacts in sync |

---

## 4. App-Level Gates (path-filtered)

These gates activate **only when the app's files change**:

### `apps/ops-console`

| Gate | Workflow | Trigger path |
|------|----------|-------------|
| ESLint + TypeScript + Prettier | `ops-console-check.yml` | `apps/ops-console/**` |
| Playwright E2E smoke | `ops-console-playwright.yml` | `apps/ops-console/**` |
| Bundle size delta | `ops-console-bundle-size.yml` | `apps/ops-console/**` |
| Golden Path gate | `golden-path-gate.yml` | `apps/**`, `packages/**` |

### Adding a new app

1. Create `apps/<name>/` following workspace registration requirements above.
2. Copy `.github/workflows/ops-console-check.yml` → `<name>-check.yml`, update paths.
3. Add a row to this table.
4. Add runbook under `docs/ops/`.

---

## 5. Release Lanes

| Lane | Branch pattern | Vercel environment | Auto-deploy |
|------|---------------|-------------------|-------------|
| **Preview** | `<any non-main>` | Preview (per-branch URL) | On push |
| **Staging** | `staging` | Preview (aliased) | On push |
| **Production** | `main` | Production | On push (gates must pass) |

**Preview deployments** are the primary UI review surface. All UI change PRs must
include the Vercel Preview URL in the PR description before merge.
See `docs/ops/VERCEL_PREVIEWS.md` for setup details.

---

## 6. Performance Budget (ops-console baseline)

| Metric | Budget | Measured by |
|--------|--------|-------------|
| Initial JS bundle | < 500 KB | `ops-console-bundle-size.yml` |
| Total bundle | < 2 MB | Same |
| LCP | < 2.5 s | Playwright + Vercel Speed Insights |
| FID / INP | < 100 ms | Vercel Speed Insights |
| CLS | < 0.1 | Same |

Bundle size delta is reported on every PR via `hashicorp/nextjs-bundle-analysis`.
A regression >20 KB triggers a warning comment; >100 KB blocks merge.

---

## 7. Documentation Contract

Every significant platform change must update one of:

- `docs/ops/` — Operational runbooks for deployed services
- `docs/platform/` — This Golden Path and platform contracts
- `docs/design/` — Design engineering workflow and token SSOT
- `docs/architecture/` — ADRs and runtime snapshots
- `docs/ai/` — AI agent instructions (edit SSOT, run sync script)

**Banned**: embedding runbook content in PR descriptions. Write docs, link to them.

---

## Related docs

| Doc | Purpose |
|-----|---------|
| `docs/ops/VERCEL_MONOREPO.md` | Vercel workspace setup, skip-unaffected |
| `docs/ops/VERCEL_PREVIEWS.md` | Preview deployments, PR review workflow |
| `docs/design/DESIGN_ENGINEERING_WORKFLOW.md` | Component lifecycle, token SSOT |
| `docs/ops/SUPABASE_VERCEL.md` | Env var sync contract |
| `docs/ai/CI_WORKFLOWS.md` | Full workflow catalog |
