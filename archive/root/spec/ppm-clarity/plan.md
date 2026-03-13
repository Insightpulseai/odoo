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
  ops-search-query                 ← FTS across ops tables (authenticated only)

Layer 4: Ops Console
  /tools/ppm                       ← portfolio table view
  /tools/search                    ← unified search UI
  /api/ppm/initiatives             ← GET → ops.ppm_initiatives  (internal-token guarded)
  /api/ppm/rollups                 ← GET → ops.ppm_status_rollups (internal-token guarded)
  /api/search                      ← POST {query} → ops-search-query (auth forwarded)

Layer 5: CI Automation
  .github/workflows/ppm-portfolio-sync.yml  ← POSTs portfolio.yaml to ops-ppm-rollup on main merge
```

## Data Flow

```
git push to main
  → ppm-portfolio-sync.yml (GitHub Action)
    → reads ssot/ppm/portfolio.yaml
    → POST ops-ppm-rollup with { initiatives: [...] }
      → ops.ppm_initiatives (upserted)
      → ops.ppm_status_rollups (computed)
      → ops.artifacts(kind=ppm_report) (written)

User query in /tools/search
  → /api/search (Next.js route, proxies with auth token)
    → ops-search-query (Edge Function, authenticated)
      → ops.ppm_initiatives + ops.runs + ops.convergence_findings (FTS)
        → results[]
```

## Delivery Mechanism for `ssot/ppm/portfolio.yaml` → Edge Function

**Decision: GitHub Action POST on merge to main.**

Why this and not alternatives:

| Option | Pros | Cons |
|--------|------|------|
| GitHub Action POST on merge | Deterministic, no drift, fully automated | Requires SUPABASE_SERVICE_ROLE_KEY in GitHub Secrets |
| PORTFOLIO_YAML env in Supabase | Simple | Manual update required; env size limits; out-of-sync risk |
| Store in Supabase table | DB-native | YAML ceases to be SSOT; two sources of truth |

The `ppm-portfolio-sync.yml` workflow:
1. Triggers on `push` to `main` with changes to `ssot/ppm/**`
2. Parses `ssot/ppm/portfolio.yaml` using Python
3. POSTs JSON payload `{ initiatives: [...] }` to `ops-ppm-rollup`
4. Fails the workflow if the Edge Function returns non-200

Weekly schedule (Monday 03:00 UTC) ensures rollup data stays fresh even without code changes.

## Security Model

| Surface | Auth mechanism | Notes |
|---------|----------------|-------|
| `/api/ppm/*` Next routes | `x-ops-internal-token` header (env `OPS_INTERNAL_TOKEN`) | Server-side only; token never sent to browser |
| `ops-search-query` Edge Fn | `Authorization: Bearer <supabase-user-jwt>` | Authenticated users only; anon blocked |
| `ops-ppm-rollup` Edge Fn | `Authorization: Bearer <service-role-key>` | Called only from CI; never from browser |
| `ops.ppm_initiatives` RLS | `authenticated` read, `service_role` write | Supabase auth layer |

## Constraints
- Migration `20260302000030` must be applied before Edge Functions are deployed
- `OPS_INTERNAL_TOKEN` must be set in Vercel env before ops-console routes are live
- `SUPABASE_SERVICE_ROLE_KEY` must be in GitHub Secrets as `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_URL` must be in GitHub Secrets as `SUPABASE_URL`

## Rollback
1. Delete `ops.ppm_initiatives` + `ops.ppm_status_rollups` (DROP CASCADE)
2. Remove Edge Functions: `supabase functions delete ops-ppm-rollup ops-search-query`
3. Disable `ppm-portfolio-sync.yml` (set `on: workflow_dispatch` only)
4. Revert Ops Console pages (the SSOT YAML files remain — safe)
