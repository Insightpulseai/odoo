# OdooOps RPC Exposure Fix - Implementation Evidence

## Problem Statement

OdooOps control plane RPC functions were created in `ops` schema but not accessible via PostgREST API due to schema exposure limitations.

**Root Cause:** Functions created as `ops.list_projects()` etc., but PostgREST only exposes functions in the `public` schema by default.

## Solution Implemented

Created public wrapper functions that internally call `ops.*` tables, following security best practices.

## Files Created/Modified

### 1. Migration: Public RPC Wrappers
**File:** `supabase/migrations/20260215_000001_ops_public_rpc_wrappers.sql`

**Functions created:**
- `public.list_projects()` - Returns all projects ordered by created_at
- `public.list_environments(p_project_id TEXT DEFAULT NULL)` - Lists environments with optional filter
- `public.list_runs(p_project_id TEXT DEFAULT NULL, p_limit INT DEFAULT 50)` - Lists recent runs with optional filters

**Security pattern:**
```sql
CREATE OR REPLACE FUNCTION public.list_projects()
RETURNS SETOF ops.projects
LANGUAGE SQL
SECURITY DEFINER
SET search_path = ops, public
AS $$
  SELECT *
  FROM ops.projects
  ORDER BY created_at DESC;
$$;

GRANT EXECUTE ON FUNCTION public.list_projects() TO authenticated, service_role;
```

**Key decisions:**
- `SECURITY DEFINER` with `SET search_path = ops, public` (prevents injection attacks)
- Grant to `authenticated` and `service_role` (NOT `anon` - control plane requires auth)
- Verification block to ensure functions created successfully

### 2. Smoke Test Script
**File:** `scripts/ops/test_ops.sh`

**Purpose:** Evidence-based validation that RPC endpoints are accessible

**Tests:**
1. `POST /rest/v1/rpc/list_projects` → Expected: `[]` or rows, NOT `PGRST202`
2. `POST /rest/v1/rpc/list_environments` → Expected: `[]` or rows
3. `POST /rest/v1/rpc/list_runs` → Expected: `[]` or rows

**Fail-loud behavior:** Script exits with error code 1 if any endpoint returns `PGRST202` (function not found)

### 3. Documentation
**File:** `docs/ops/TESTING.md`

**Content:**
- Architecture pattern (ops.* internal, public.* exposed)
- PostgREST RPC endpoint format (`/rest/v1/rpc/<function_name>`, no schema qualification)
- Function wrapper pattern with security annotations
- Error code reference (PGRST202, PGRST204, etc.)
- Testing procedures and troubleshooting

## Application Instructions

### Option A: Via Supabase CLI (Recommended)

```bash
# Ensure local migrations are synced
git pull origin main

# Apply migration
supabase db push

# Verify RPC exposure
./scripts/ops/test_ops.sh
```

### Option B: Direct SQL Execution

```bash
# If migration history is broken
cat supabase/migrations/20260215_000001_ops_public_rpc_wrappers.sql | \
  PGPASSWORD="$SUPABASE_DB_PASSWORD" \
  psql "postgresql://postgres@db.spdtwktxdalcfigzeqrz.supabase.co:6543/postgres?sslmode=require"

# Verify
./scripts/ops/test_ops.sh
```

### Option C: Manual Execution (Supabase Dashboard)

1. Open Supabase SQL Editor
2. Copy contents of `supabase/migrations/20260215_000001_ops_public_rpc_wrappers.sql`
3. Execute
4. Run smoke test: `./scripts/ops/test_ops.sh`

## Verification Checklist

- [ ] Migration applied without errors
- [ ] `public.list_projects()` function exists (`\df public.list_*` in psql)
- [ ] RPC endpoint `/rest/v1/rpc/list_projects` returns `[]` or rows (NOT `PGRST202`)
- [ ] RPC endpoint `/rest/v1/rpc/list_environments` accessible
- [ ] RPC endpoint `/rest/v1/rpc/list_runs` accessible
- [ ] Smoke test script passes: `./scripts/ops/test_ops.sh` exits 0

## Expected Outcomes

**Before migration:**
```bash
curl -X POST https://.../rest/v1/rpc/list_projects ...
# {"code":"PGRST202","message":"Could not find the public.list_projects() function..."}
```

**After migration:**
```bash
curl -X POST https://.../rest/v1/rpc/list_projects ...
# [] or [{"project_id":"odoo-ce","name":"Odoo CE",...}]
```

## References

- **Spec:** `spec/odooops-sh/prd.md`
- **Core schema:** `supabase/migrations/20260214_000001_ops_schema_core.sql`
- **Original RPC functions:** `supabase/migrations/20260212_001200_ops_rpc_functions.sql`
- **PostgREST docs:** https://postgrest.org/en/stable/references/api/functions.html

## Lessons Learned

1. **Evidence-based testing:** Always verify actual behavior, don't assume success from command completion
2. **PostgREST schema exposure:** Functions must be in exposed schemas (typically `public`)
3. **RPC endpoint format:** `/rest/v1/rpc/<function_name>` with NO schema qualification
4. **PGRST202 meaning:** Function not in schema cache (doesn't exist, wrong schema, or wrong signature)
5. **Public wrapper pattern:** Keep internal schema for organization, expose curated API via public wrappers

## Related PRs

- **Root cleanup:** PR #357 (repository root hygiene)
- **This fix:** (PR to be created after verification)
