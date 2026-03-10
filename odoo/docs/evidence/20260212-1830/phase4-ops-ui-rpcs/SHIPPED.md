# Phase 4: ops UI RPCs - SHIPPED

**Date**: 2026-02-12 18:30
**Scope**: Complete missing ops UI RPCs for odooops-console (backups, settings, upgrade versions)
**Status**: ✅ Migration + Pulser Bridge SHIPPED
**Commit**: a766951e

---

## What Was Shipped

### 1. SuperClaude→Pulser Bridge YAML

**File**: `superclaude_bridge.yaml`

**Purpose**: Maps SuperClaude framework (30 commands, 7 modes, 16 agents) to Pulser skill profiles with Odoo.sh-aligned personas

**Contents**:
- 30 `/sc:*` commands mapped to Pulser profiles
- 7 behavioral modes (brainstorming, deep_research, orchestration, token_efficiency, business_panel, task_management, introspection)
- 16 agents/personas (12 grounded, 4 placeholders)
- Odoo.sh skill profiles (odoo_dev, odoo_tester, odoo_pm, odoo_sre)
- Command→Profile mappings
- Agent→Profile mappings
- Mode→Overlay mappings
- Odoo.sh feature→Skill mappings

**Validation**:
```bash
✅ Commands: 30
✅ Modes: 7
✅ Agents: 16
✅ All commands mapped to profiles
```

### 2. ops UI RPCs Migration

**File**: `supabase/migrations/20260212_001400_ops_ui_rpcs.sql`

**Purpose**: Complete missing UI RPC surface for odooops-console

**Tables Created** (3):
- ✅ `ops.backups` - Backup metadata (id, project_id, status, provider, region, size_bytes, checksum)
- ✅ `ops.project_settings` - Project configuration (project_id, settings jsonb, updated_at, updated_by)
- ✅ `ops.project_upgrade_versions` - Upgrade history (id, project_id, from_version, to_version, status, planned_at, applied_at)

**RPCs Created** (4):
- ✅ `ops.ui_backups(project_id, limit, offset)` - List backups for project
- ✅ `ops.ui_project_settings(project_id)` - Read project settings
- ✅ `ops.ui_project_settings_upsert(project_id, settings)` - Save project settings
- ✅ `ops.ui_project_upgrade_versions(project_id, limit, offset)` - List upgrade versions

**Security**:
- ✅ RLS enabled on all tables
- ✅ Conditional policies if `ops.project_members` table exists
- ✅ Security definer RPCs for controlled access
- ✅ Service_role fallback if membership table doesn't exist

**Indexes Created** (2):
- ✅ `backups_project_created_idx` on `ops.backups(project_id, created_at desc)`
- ✅ `upgrade_versions_project_created_idx` on `ops.project_upgrade_versions(project_id, created_at desc)`

### 3. Rollback Script

**File**: `supabase/migrations/rollback_ops_ui_rpcs.sql`

**Purpose**: Safe rollback for ops UI RPCs

**Actions**:
- Drop 4 RPC functions
- Drop 3 tables in correct order (reverse dependency)

---

## Verification Commands

### 1. Apply Migration to Supabase

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo

# Link to Supabase project
supabase link --project-ref spdtwktxdalcfigzeqrz

# Apply migration
supabase db push

# Expected output:
# Applied migrations:
#   - 20260212_001400_ops_ui_rpcs.sql
```

### 2. Verify Functions Exist

```sql
select n.nspname as schema, p.proname as fn
from pg_proc p
join pg_namespace n on n.oid = p.pronamespace
where n.nspname = 'ops'
  and p.proname in ('ui_backups','ui_project_settings','ui_project_settings_upsert','ui_project_upgrade_versions')
order by 1,2;

-- Expected: 4 rows
```

### 3. Verify Tables Exist

```sql
select table_name from information_schema.tables
where table_schema = 'ops'
  and table_name in ('backups', 'project_settings', 'project_upgrade_versions')
order by table_name;

-- Expected: 3 rows
```

### 4. Smoke Test RPCs

```sql
-- Test with real project ID
select * from ops.ui_backups('[project_id]'::uuid, 10, 0);
select ops.ui_project_settings('[project_id]'::uuid);
select ops.ui_project_settings_upsert('[project_id]'::uuid, '{"theme":"dark"}'::jsonb);
select * from ops.ui_project_upgrade_versions('[project_id]'::uuid, 10, 0);

-- Expected: No errors (empty results if no data yet)
```

### 5. Verify RLS Enabled

```sql
select relrowsecurity
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname='ops' and c.relname in ('backups','project_settings','project_upgrade_versions');

-- Expected: 3 rows with relrowsecurity = true
```

---

## Phase 4 Scope Summary

**In-Scope** (✅ Complete):
- ✅ `ops.ui_backups()` - Backups table + read RPC for UI listing
- ✅ `ops.ui_project_settings()` - Settings table + read/write RPCs
- ✅ `ops.ui_project_upgrade_versions()` - Upgrade versions table + read RPC

**Out-of-Scope** (Separate Epics):
- ❌ `ops.month_close_*()` - Month-End Close / Finance Ops epic
- ❌ `tax.ui_filings_board()` - Tax/BIR Filings epic

---

## UI Pages Ready to Wire

With this migration, the following UI pages now have backend support:

**Now Ready**:
1. ✅ `app/app/projects/[projectId]/backups/page.tsx` - Can use `ops.ui_backups()`
2. ✅ `app/app/projects/[projectId]/settings/page.tsx` - Can use `ops.ui_project_settings()`
3. ✅ `app/app/projects/[projectId]/upgrade/page.tsx` - Can use `ops.ui_project_upgrade_versions()`

**Still Deferred** (Need separate backend work):
- ⏸️ `app/app/close/*` pages - Need month-end close backend
- ⏸️ `app/app/close/compliance/page.tsx` - Need tax filing backend

---

## Git Evidence

```
Commit: a766951e
Message: feat(pulser+ops): add SuperClaude bridge + ops UI RPCs (phase 4 scope)
Files: 3 files changed, 560 insertions(+)
Branch: feat/odooops-browser-automation-integration
```

**Files Committed**:
- superclaude_bridge.yaml
- supabase/migrations/20260212_001400_ops_ui_rpcs.sql
- supabase/migrations/rollback_ops_ui_rpcs.sql

---

## Next Steps

### Phase 4b: Wire Remaining UI Pages (Now Unblocked)

**Update 3 pages to use new RPCs**:
1. `app/app/projects/[projectId]/backups/page.tsx` - Replace demo data with `ops.ui_backups()`
2. `app/app/projects/[projectId]/settings/page.tsx` - Replace demo data with `ops.ui_project_settings()` + `ops.ui_project_settings_upsert()`
3. `app/app/projects/[projectId]/upgrade/page.tsx` - Replace demo data with `ops.ui_project_upgrade_versions()`

### Phase 5: Deploy to Production

**Deployment Steps**:
1. Apply migrations to Supabase production (`supabase db push`)
2. Verify RPC functions exist
3. Test UI pages with real data in local dev
4. Deploy console to `ops.insightpulseai.com` (Vercel)
5. Configure DNS (CNAME ops → Vercel)
6. Run E2E smoke tests

---

## Conclusion

**Status**: ✅ Phase 4 Backend COMPLETE

The missing ops UI RPCs are now fully implemented with:
- Complete database schema (3 tables with indexes and RLS)
- 4 RPC functions for UI data access
- SuperClaude→Pulser bridge for skill profile alignment
- Evidence in git (commit a766951e)

**Remaining**: Wire 3 UI pages + production deployment (Phases 4b-5)

**Verification**: Apply migration, verify functions, test UI locally
