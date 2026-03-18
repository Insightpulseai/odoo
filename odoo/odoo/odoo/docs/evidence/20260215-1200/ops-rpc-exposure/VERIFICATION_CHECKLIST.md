# OdooOps RPC Exposure - Verification Checklist

## Pre-Merge Verification Steps

### 1. Migration Application

**Choose one method:**

**Option A - Supabase CLI (Recommended):**
```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
supabase db push
```

**Option B - Direct SQL (if migration history broken):**
```bash
cat supabase/migrations/20260215_000001_ops_public_rpc_wrappers.sql | \
  PGPASSWORD="$SUPABASE_DB_PASSWORD" \
  psql "postgresql://postgres@db.spdtwktxdalcfigzeqrz.supabase.co:6543/postgres?sslmode=require"
```

**Option C - Supabase Dashboard:**
1. Open https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz
2. Navigate to SQL Editor
3. Copy contents of `supabase/migrations/20260215_000001_ops_public_rpc_wrappers.sql`
4. Execute
5. Verify output shows: "Successfully created 3 public RPC wrapper functions"

### 2. Smoke Test Execution

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
./scripts/ops/test_ops.sh
```

**Expected Output:**
```
🧪 OdooOps Control Plane RPC Smoke Test
========================================

1. Testing /rest/v1/rpc/list_projects...
   ✅ PASS: RPC callable (returned: []...)

2. Testing /rest/v1/rpc/list_environments...
   ✅ PASS: RPC callable (returned: []...)

3. Testing /rest/v1/rpc/list_runs...
   ✅ PASS: RPC callable (returned: []...)

========================================
✅ All RPC endpoints accessible and functional

Summary:
  - public.list_projects() ✅
  - public.list_environments() ✅
  - public.list_runs() ✅

OdooOps control plane RPC layer is ready for odooops-console integration.
```

**If you see retry messages:**
```
⚠️  PGRST202 on first attempt, retrying after 2s (schema cache lag)...
```
This is expected behavior - the test will retry once and should succeed.

### 3. Manual RPC Verification

**Test each endpoint manually:**

```bash
# Test 1: list_projects
curl -s -X POST \
  "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/rpc/list_projects" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json"

# Expected: [] or [{"project_id":"...","name":"...",...}]
# NOT: {"code":"PGRST202",...}

# Test 2: list_environments (with optional filter)
curl -s -X POST \
  "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/rpc/list_environments" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"p_project_id": null}'

# Expected: [] or rows

# Test 3: list_runs (with optional filters)
curl -s -X POST \
  "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/rpc/list_runs" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"p_project_id": null, "p_limit": 50}'

# Expected: [] or rows
```

### 4. Security Verification

**Verify anon role is blocked:**

```bash
# This should FAIL with permission denied
curl -s -X POST \
  "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/rpc/list_projects" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json"

# Expected: {"code":"42501","message":"permission denied for function list_projects"}
# NOT: [] or rows (if you get data, anon has access - SECURITY ISSUE)
```

### 5. Function Existence Check

**Via psql:**

```bash
PGPASSWORD="$SUPABASE_DB_PASSWORD" psql \
  "postgresql://postgres@db.spdtwktxdalcfigzeqrz.supabase.co:6543/postgres?sslmode=require" \
  -c "\df public.list_*"
```

**Expected Output:**
```
                                     List of functions
 Schema |       Name        | Result data type |    Argument data types    | Type
--------+-------------------+------------------+---------------------------+------
 public | list_environments | SETOF ops.environments | p_project_id text DEFAULT NULL::text | func
 public | list_projects     | SETOF ops.projects     |                           | func
 public | list_runs         | SETOF ops.runs         | p_project_id text DEFAULT NULL::text, p_limit integer DEFAULT 50 | func
(3 rows)
```

### 6. Checklist

- [ ] Migration applied without errors
- [ ] Smoke test passes (`./scripts/ops/test_ops.sh` exits 0)
- [ ] `/rest/v1/rpc/list_projects` returns `[]` or rows (NOT PGRST202)
- [ ] `/rest/v1/rpc/list_environments` returns `[]` or rows
- [ ] `/rest/v1/rpc/list_runs` returns `[]` or rows
- [ ] Anon role blocked (permission denied error)
- [ ] All 3 functions exist in public schema (`\df public.list_*`)
- [ ] Migration includes `REVOKE EXECUTE ... FROM anon` for all functions
- [ ] Docs updated with Security Model section
- [ ] Smoke test includes retry logic for schema cache lag

## Evidence Collection

After verification, capture evidence:

```bash
# Create evidence directory
mkdir -p docs/evidence/$(date +%Y%m%d-%H%M)/ops-rpc-verification

# Capture smoke test output
./scripts/ops/test_ops.sh > docs/evidence/$(date +%Y%m%d-%H%M)/ops-rpc-verification/smoke-test-output.txt 2>&1

# Capture manual RPC test
curl -s -X POST \
  "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/rpc/list_projects" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  | jq '.' > docs/evidence/$(date +%Y%m%d-%H%M)/ops-rpc-verification/list-projects-response.json

# Capture function list
PGPASSWORD="$SUPABASE_DB_PASSWORD" psql \
  "postgresql://postgres@db.spdtwktxdalcfigzeqrz.supabase.co:6543/postgres?sslmode=require" \
  -c "\df public.list_*" \
  > docs/evidence/$(date +%Y%m%d-%H%M)/ops-rpc-verification/function-list.txt
```

## Rollback Procedure (If Needed)

If issues are discovered after migration:

```sql
-- Drop public wrapper functions
DROP FUNCTION IF EXISTS public.list_projects();
DROP FUNCTION IF EXISTS public.list_environments(TEXT);
DROP FUNCTION IF EXISTS public.list_runs(TEXT, INT);
```

Then investigate and fix issues before reapplying.

## Success Criteria

All checks pass ✅:
- Migration applied successfully
- Smoke test exits 0
- All RPC endpoints return `[]` or data (no PGRST202)
- Security: anon blocked, authenticated/service_role allowed
- Documentation complete and accurate
- Evidence captured for audit trail

## Post-Verification Actions

1. Commit evidence to branch
2. Push branch: `git push origin fix/complete-root-hygiene-file-moves`
3. Create PR with verification results
4. Link PR to spec: `spec/odooops-sh/prd.md`
5. Request review from team
