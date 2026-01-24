# Supabase Project Verification Results

**Date**: 2026-01-24 11:09:00 UTC
**Verified By**: Claude Agent (Opus 4.5)

## CLI Link Verification

| Check | Status | Value |
|-------|--------|-------|
| Project Reference | PASS | `spdtwktxdalcfigzeqrz` |
| Pooler URL | PASS | `postgresql://postgres.spdtwktxdalcfigzeqrz@aws-1-us-east-1.pooler.supabase.com:5432/postgres` |
| Postgres Version | PASS | 17.6.1.021 |

## Configuration Validation

| File | Exists | Valid |
|------|--------|-------|
| `supabase/config.toml` | Yes | Yes |
| `supabase/.temp/project-ref` | Yes | Yes |
| `supabase/.temp/pooler-url` | Yes | Yes |
| `.env.example` | Yes | Yes |

## Integration Status (from Dashboard)

| Integration | Status |
|-------------|--------|
| GitHub | Connected (`jgtolentino/odoo-ce`) |
| Vercel | Connected (`insightpulseai` team) |
| AWS PrivateLink | Not configured |

## Schema Assets

| Asset Type | Count |
|------------|-------|
| Migrations | 50+ |
| Edge Functions | 30+ |
| Seed Files | 17+ |

## Verification Summary

All checks passed. The Supabase project `spdtwktxdalcfigzeqrz` (superset) is correctly configured with:

1. GitHub integration auto-deploying migrations on push to `main`
2. Vercel integration syncing environment variables
3. Local CLI linked to correct project reference
4. PostgreSQL 17.6.1 backend
5. Pooler connection via `aws-1-us-east-1`

## Files in This Evidence Pack

```
docs/evidence/20260124-supabase-setup/integrations/
├── SUPABASE_PROJECT_SETUP.md    # Full configuration documentation
├── git_state.txt                 # Git state at verification time
└── verification_results.md       # This file
```
