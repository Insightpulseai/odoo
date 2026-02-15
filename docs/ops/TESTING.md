# OdooOps Control Plane Testing Guide

## Overview

OdooOps control plane uses Supabase PostgreSQL with PostgREST API exposure. This guide documents testing patterns and RPC endpoint conventions.

## Architecture Pattern

```
PostgreSQL Schema:         PostgREST API Access:
┌────────────────┐        ┌─────────────────────────┐
│ ops.* tables   │ ─────> │ /rest/v1/table_name     │ (if exposed)
│ (internal)     │        │                         │
└────────────────┘        └─────────────────────────┘
        │
        │ called by
        ▼
┌────────────────┐        ┌─────────────────────────┐
│ public.fn()    │ ─────> │ /rest/v1/rpc/fn         │ (accessible)
│ wrappers       │        │                         │
└────────────────┘        └─────────────────────────┘
```

**Key Design Decision:** Keep `ops.*` schema internal, expose curated API surface via `public.*` wrapper functions.

## PostgREST RPC Endpoint Format

**Correct format:**
```bash
POST /rest/v1/rpc/<function_name>
```

**Incorrect formats (will fail):**
```bash
POST /rest/v1/rpc/ops.function_name   # ❌ Schema qualification not allowed
POST /rest/v1/rpc/schema.function     # ❌ Not supported
GET  /rest/v1/rpc/function_name       # ❌ RPC requires POST
```

**Why:** PostgREST resolves RPC functions in exposed schemas (typically `public`). Schema qualification in the URL is invalid.

## Function Wrapper Pattern

Functions in non-public schemas must be wrapped:

```sql
-- Internal function (NOT accessible via PostgREST)
CREATE FUNCTION ops.internal_logic() ...

-- Public wrapper (accessible via /rest/v1/rpc/api_function)
CREATE OR REPLACE FUNCTION public.api_function()
RETURNS SETOF ops.target_table
LANGUAGE SQL
SECURITY DEFINER
SET search_path = ops, public
AS $$
  SELECT * FROM ops.target_table;
$$;

GRANT EXECUTE ON FUNCTION public.api_function() TO authenticated, service_role;
```

**Security notes:**
- `SECURITY DEFINER`: Runs with definer privileges (required for cross-schema access)
- `SET search_path = ops, public`: Prevents search_path injection attacks
- Grant to `authenticated` + `service_role`, **NOT** `anon` for control plane security

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| `PGRST202` | Function not found in schema cache | Function doesn't exist in `public` schema or wrong signature |
| `PGRST204` | No data | Query succeeded but returned empty result |
| `42883` | Function does not exist | Function not created or wrong parameters |
| `42P01` | Table does not exist | Referenced table missing |

## Testing OdooOps RPC

**Automated smoke test:**
```bash
./scripts/ops/test_ops.sh
```

**Manual RPC test:**
```bash
curl -s -X POST \
  "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/rpc/list_projects" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"

# Expected: [] or [{"project_id": "...", ...}]
# NOT: {"code":"PGRST202", ...}
```

**Test with parameters:**
```bash
curl -s -X POST \
  "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/rpc/list_environments" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"p_project_id": "odoo-ce"}'

# Expected: environments filtered by project_id
```

## Available RPC Functions

| Function | Parameters | Returns | Purpose |
|----------|-----------|---------|---------|
| `list_projects()` | None | `SETOF ops.projects` | List all projects ordered by created_at |
| `list_environments(p_project_id TEXT)` | Optional project filter | `SETOF ops.environments` | List environments, optionally filtered |
| `list_runs(p_project_id TEXT, p_limit INT)` | Optional project + limit (default 50) | `SETOF ops.runs` | List recent runs, optionally filtered |

## Migration Application

**Via Supabase CLI (recommended):**
```bash
supabase db push
```

**Via direct SQL (if migration history is broken):**
```bash
cat supabase/migrations/20260215_000001_ops_public_rpc_wrappers.sql | \
  PGPASSWORD="$SUPABASE_DB_PASSWORD" \
  psql "postgresql://postgres@db.spdtwktxdalcfigzeqrz.supabase.co:6543/postgres?sslmode=require"
```

**Verification after migration:**
```bash
./scripts/ops/test_ops.sh
```

## Troubleshooting

### PGRST202: Function not found

**Symptoms:**
```json
{"code":"PGRST202","details":null,"hint":null,"message":"Could not find the public.list_projects() function..."}
```

**Diagnosis:**
1. Function doesn't exist in `public` schema
2. Function signature doesn't match call
3. PostgREST schema cache not refreshed

**Solution:**
```bash
# Verify function exists
psql -c "\df public.list_*"

# If missing, apply migration
supabase db push

# Refresh PostgREST schema cache (automatic after migration)
```

### Empty Results vs. No Function

**Empty results (OK):**
```json
[]
```

**Function not found (ERROR):**
```json
{"code":"PGRST202", ...}
```

**Key distinction:** `[]` means function works but returns no data. `PGRST202` means function doesn't exist.

## References

- [PostgREST RPC Documentation](https://postgrest.org/en/stable/references/api/functions.html)
- Migration: `supabase/migrations/20260215_000001_ops_public_rpc_wrappers.sql`
- Smoke test: `scripts/ops/test_ops.sh`
- PRD: `spec/odooops-sh/prd.md`
