# Implementation Plan — PPM Clarity

## Architecture Layers

```
Layer 1: SSOT (repo)
  ssot/ppm/portfolio.yaml          ← portfolio source of truth
  ssot/search/sources.yaml         ← search index config

Layer 2: Supabase Schema
  ops.ppm_initiatives              ← portfolio mirror (upserted by rollup fn)
  ops.ppm_status_rollups           ← computed status rows

Layer 3: Edge Functions
  ops-ppm-rollup                   ← seed initiatives + compute rollups + write artifact
  ops-search-query                 ← FTS across ops tables

Layer 4: Ops Console
  /tools/ppm                       ← portfolio table view
  /tools/search                    ← unified search UI
  /api/ppm/initiatives             ← GET → ops.ppm_initiatives
  /api/ppm/rollups                 ← GET → ops.ppm_status_rollups
  /api/search                      ← POST {query} → ops-search-query
```

## Data Flow

```
portfolio.yaml
  → ops-ppm-rollup (scheduled/manual)
    → ops.ppm_initiatives (upserted)
    → ops.ppm_status_rollups (computed)
    → ops.artifacts(kind=ppm_report) (written)

User query in /tools/search
  → /api/search (Next.js route)
    → ops-search-query (Edge Function)
      → ops.ppm_initiatives + ops.runs + ops.convergence_findings (FTS)
        → results[]
```

## Constraints
- Migration `20260302000030` must be applied before Edge Functions are deployed
- Edge Functions need `SUPABASE_SERVICE_ROLE_KEY` in environment
- `ops.artifacts` table created by migration `20260302000020` (universal runs)
  — if that migration hasn't run, `ops-ppm-rollup` skips artifact write gracefully

## Rollback
1. Delete `ops.ppm_initiatives` + `ops.ppm_status_rollups` tables (DROP CASCADE)
2. Remove Edge Functions from Supabase dashboard
3. Remove Ops Console pages (revert commit)
- `ssot/ppm/portfolio.yaml` and `ssot/search/sources.yaml` are SSOT files — leave in repo
