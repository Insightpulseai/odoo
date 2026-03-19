# Tasks — PPM Clarity

## Phase 1: SSOT Files ✅
- [x] T1.1 `ssot/ppm/portfolio.yaml` — 5 seed initiatives
- [x] T1.2 `ssot/search/sources.yaml` — search source config

## Phase 2: Schema + Functions + UI ✅ (code only, not yet deployed)
- [x] T2.1 `supabase/migrations/20260302000030_ops_ppm_initiatives.sql`
  - `ops.ppm_initiatives` table + RLS
  - `ops.ppm_status_rollups` table + RLS
  - FTS generated column + GIN index
  - Updated-at trigger
- [x] T2.2 `supabase/functions/ops-ppm-rollup/index.ts`
  - Reads initiatives from request body (see plan.md §Delivery mechanism)
  - Upserts `ops.ppm_initiatives`
  - Computes rollups from `ops.convergence_findings`
  - Writes `ops.artifacts(kind=ppm_report)` with Markdown report
  - Input validation: INIT-ID format, status enum, spec_slug safety
- [x] T2.3 `supabase/functions/ops-search-query/index.ts`
  - POST `{query: string}` → FTS results (max 50)
  - Query sanitization: max 200 chars, allowlisted tables
  - Requires `authenticated` token (not anon)
- [x] T2.4 `apps/ops-console/app/tools/ppm/page.tsx` — portfolio table
- [x] T2.5 `apps/ops-console/app/tools/search/page.tsx` — search UI
- [x] T2.6 `apps/ops-console/app/api/ppm/initiatives/route.ts`
  - Auth guard: `x-ops-internal-token` header required
- [x] T2.7 `apps/ops-console/app/api/ppm/rollups/route.ts`
  - Auth guard: `x-ops-internal-token` header required
- [x] T2.8 `apps/ops-console/app/api/search/route.ts`
  - Proxies to `ops-search-query` with authenticated token
- [x] T2.9 `.github/workflows/ppm-portfolio-sync.yml`
  - Posts `portfolio.yaml` to `ops-ppm-rollup` on merge to main

## Phase 3: Deploy & Seed ⏳ (manual — post-merge)

> **These items are NOT complete until executed in production.**

- [ ] T3.1 Apply schema migration on DO droplet
  ```bash
  ssh root@178.128.112.214 "cd /workspaces/odoo && supabase db push --project-ref spdtwktxdalcfigzeqrz"
  ```
- [ ] T3.2 Deploy Edge Functions
  ```bash
  supabase functions deploy ops-ppm-rollup --project-ref spdtwktxdalcfigzeqrz
  supabase functions deploy ops-search-query --project-ref spdtwktxdalcfigzeqrz
  ```
- [ ] T3.3 Add `OPS_INTERNAL_TOKEN` to Vercel env (ops-console app)
  — generate: `openssl rand -hex 32`
  — add to Vercel dashboard under `ops-console` project
- [ ] T3.4 Add `SUPABASE_SERVICE_ROLE_KEY` to ops-ppm-rollup Edge Function secrets
  — already in Supabase Vault; confirm it's set in Edge Function env
- [ ] T3.5 First run / portfolio seed (triggered by CI on merge via `ppm-portfolio-sync.yml`)
- [ ] T3.6 Smoke test ops-console pages
  - `/tools/ppm` → shows 5 initiatives
  - `/tools/search?q=ppm` → returns at least 1 result
- [ ] T3.7 Verify weekly cron schedule
  - `ppm-portfolio-sync.yml` runs weekly on schedule (Monday 03:00 UTC)
  - Confirm first scheduled run fires without error

## Rollback
1. `DROP TABLE ops.ppm_status_rollups, ops.ppm_initiatives CASCADE;`
2. `supabase functions delete ops-ppm-rollup ops-search-query`
3. Revert commit (SSOT YAML files stay — they are safe)
