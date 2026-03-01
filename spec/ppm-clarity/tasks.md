# Tasks — PPM Clarity

## Phase 1: SSOT Files
- [x] T1.1 `ssot/ppm/portfolio.yaml` — 5 seed initiatives
- [x] T1.2 `ssot/search/sources.yaml` — search source config

## Phase 2: Supabase Schema
- [x] T2.1 `supabase/migrations/20260302000030_ops_ppm_initiatives.sql`
  - `ops.ppm_initiatives` table + RLS
  - `ops.ppm_status_rollups` table + RLS
  - Updated_at trigger

## Phase 3: Edge Functions
- [x] T3.1 `supabase/functions/ops-ppm-rollup/index.ts`
  - Reads `portfolio.yaml` (from metadata arg or env)
  - Upserts `ops.ppm_initiatives`
  - Computes rollups from `ops.convergence_findings`
  - Writes `ops.artifacts(kind=ppm_report)` with Markdown report
- [x] T3.2 `supabase/functions/ops-search-query/index.ts`
  - POST `{query: string}` → FTS results
  - Sources: ppm_initiatives, ops.runs, convergence_findings

## Phase 4: Ops Console
- [x] T4.1 `apps/ops-console/app/tools/ppm/page.tsx` — portfolio table
- [x] T4.2 `apps/ops-console/app/tools/search/page.tsx` — search UI
- [x] T4.3 `apps/ops-console/app/api/ppm/initiatives/route.ts`
- [x] T4.4 `apps/ops-console/app/api/ppm/rollups/route.ts`
- [x] T4.5 `apps/ops-console/app/api/search/route.ts`

## Manual Steps (post-merge)
- [ ] `supabase db push` on DO droplet (applies migration 20260302000030)
- [ ] `supabase functions deploy ops-ppm-rollup --project-ref spdtwktxdalcfigzeqrz`
- [ ] `supabase functions deploy ops-search-query --project-ref spdtwktxdalcfigzeqrz`
- [ ] First run: POST to `ops-ppm-rollup` to seed `ops.ppm_initiatives`
