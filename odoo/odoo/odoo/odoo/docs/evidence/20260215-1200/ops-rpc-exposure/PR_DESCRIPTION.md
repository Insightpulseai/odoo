# PR: OdooOps RPC Exposure Fix + Authority Model Documentation

## Summary

Implements public RPC wrappers for OdooOps control plane functions with belt-and-suspenders security hardening, plus canonical Odoo vs Supabase authority model documentation.

## Problem

OdooOps control plane RPC functions (`ops.list_projects()`, `ops.list_environments()`, `ops.list_runs()`) were not accessible via PostgREST API:
- Functions existed in `ops` schema (internal, not exposed to PostgREST)
- RPC endpoints returned `PGRST202` error (function not in schema cache)
- No public API surface for odooops-console integration

## Solution

### 1. Public RPC Wrappers
Created public wrapper functions following security best practices:

**Migration:** `supabase/migrations/20260215_000001_ops_public_rpc_wrappers.sql`

**Functions created:**
- `public.list_projects()` - Returns all projects ordered by created_at
- `public.list_environments(p_project_id TEXT)` - Lists environments with optional filter
- `public.list_runs(p_project_id TEXT, p_limit INT)` - Lists recent runs with filters

**Security pattern:**
```sql
CREATE FUNCTION public.list_projects()
RETURNS SETOF ops.projects
LANGUAGE SQL
SECURITY DEFINER
SET search_path = ops, public
AS $$ SELECT * FROM ops.projects ORDER BY created_at DESC; $$;

-- Belt-and-suspenders guards
REVOKE EXECUTE ON FUNCTION public.list_projects() FROM anon;
GRANT EXECUTE ON FUNCTION public.list_projects() TO authenticated, service_role;
```

### 2. Security Hardening
- Explicit `REVOKE EXECUTE ... FROM anon` for all RPC functions
- `SET search_path = ops, public` prevents search_path injection
- Grant only to `authenticated` + `service_role` (control plane requires auth)

### 3. Testing & Documentation
- **Smoke test:** `scripts/ops/test_ops.sh` with retry logic for schema cache lag
- **Security model docs:** `docs/ops/TESTING.md` explains SECURITY DEFINER boundary
- **Evidence-based validation:** Fails loudly on PGRST202 errors

### 4. Authority Model Documentation
Added canonical Odoo vs Supabase authority model to `docs/ai/ARCHITECTURE.md`:

**Key principle:** Odoo = System of Record for transactions, Supabase = SSOT for control plane/analytics/AI

**Governance:**
- One-way mirroring: Odoo → Supabase (read-only replicas)
- No dual-write, deterministic keys, RLS enforcement
- Clear domain boundaries with examples

## Changes

### Files Created
- `supabase/migrations/20260215_000001_ops_public_rpc_wrappers.sql` (3 public functions)
- `scripts/ops/test_ops.sh` (evidence-based smoke test with retry logic)
- `docs/ops/TESTING.md` (PostgREST RPC patterns, security model, troubleshooting)
- `docs/evidence/20260215-1200/ops-rpc-exposure/IMPLEMENTATION.md` (implementation evidence)
- `docs/evidence/20260215-1200/ops-rpc-exposure/VERIFICATION_CHECKLIST.md` (verification steps)
- `docs/evidence/20260215-1200/ops-rpc-exposure/PR_DESCRIPTION.md` (this file)

### Files Modified
- `docs/ai/ARCHITECTURE.md` (added Authority Model section)

## Verification

### Before Merge

**1. Apply migration:**
```bash
supabase db push
# OR: cat supabase/migrations/20260215_000001_ops_public_rpc_wrappers.sql | psql ...
# OR: Supabase Dashboard SQL Editor
```

**2. Run smoke test:**
```bash
./scripts/ops/test_ops.sh
```

**Expected output:**
```
✅ All RPC endpoints accessible and functional
  - public.list_projects() ✅
  - public.list_environments() ✅
  - public.list_runs() ✅
```

**3. Manual verification:**
```bash
curl -s -X POST \
  "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/rpc/list_projects" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"

# Expected: [] or [{"project_id":"..."}]
# NOT: {"code":"PGRST202",...}
```

**4. Security check:**
```bash
# Verify anon is blocked (should get permission denied)
curl -s -X POST \
  "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/rpc/list_projects" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY"

# Expected: {"code":"42501","message":"permission denied for function list_projects"}
```

### Checklist

- [ ] Migration applied without errors
- [ ] Smoke test passes (`./scripts/ops/test_ops.sh` exits 0)
- [ ] All RPC endpoints return `[]` or rows (NO PGRST202)
- [ ] Anon role blocked (permission denied)
- [ ] Functions exist in public schema (`\df public.list_*`)
- [ ] Documentation accurate and complete

## Testing

**Smoke test features:**
- Tests all 3 RPC endpoints (`list_projects`, `list_environments`, `list_runs`)
- Includes retry logic for PostgREST schema cache lag (2s delay)
- Fails loudly on PGRST202 errors after retry
- Evidence-based validation (no false positives)

**Security verification:**
- Functions use `SECURITY DEFINER` with `SET search_path = ops, public`
- Explicit `REVOKE EXECUTE ... FROM anon` hardens against accidental grants
- Only `authenticated` + `service_role` can execute

## References

- **Spec:** `spec/odooops-sh/prd.md` (OdooOps control plane requirements)
- **Core schema:** `supabase/migrations/20260214_000001_ops_schema_core.sql`
- **Original RPC migration:** `supabase/migrations/20260212_001200_ops_rpc_functions.sql`
- **PostgREST docs:** https://postgrest.org/en/stable/references/api/functions.html

## Lessons Learned

1. **Evidence-based testing:** Always verify actual behavior, don't assume success
2. **PostgREST schema exposure:** Functions must be in exposed schemas (typically `public`)
3. **RPC endpoint format:** `/rest/v1/rpc/<function_name>` with NO schema qualification
4. **PGRST202 meaning:** Function not in schema cache (doesn't exist, wrong schema, or signature mismatch)
5. **Public wrapper pattern:** Keep internal schema for organization, expose curated API via public wrappers
6. **Belt-and-suspenders security:** Explicit REVOKE + GRANT prevents accidental exposure
7. **Schema cache lag:** PostgREST may need time to refresh after migration (retry logic handles this)

## Related Work

- **Root cleanup:** PR #357 (repository root hygiene after merge creating duplicates)
- **OdooOps spec:** `spec/odooops-sh/` (complete control plane specification)

## Next Steps

After merge:
1. ✅ RPC endpoints accessible for odooops-console integration
2. ✅ Security hardened against accidental anon grants
3. ✅ Authority model documented for team alignment
4. 🔄 Implement odooops-console CLI (uses these RPC endpoints)
5. 🔄 Add project/environment/run CRUD operations via RPC

## Commits

1. **2855b200** - `fix(ops): expose OdooOps RPC functions via public schema wrappers`
   - Initial migration, smoke test, documentation

2. **eee49c9b** - `docs(architecture): add canonical Odoo vs Supabase authority model`
   - Authority model, domain boundaries, governance guardrails

3. **4d128c71** - `fix(ops): harden RPC wrappers with belt-and-suspenders security guards`
   - REVOKE anon, Security Model docs, retry logic

---

**Ready for review and merge after migration verification.**
