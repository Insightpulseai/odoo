# Phase 4 ops UI RPCs Deployment Checklist

**Date**: 2026-02-12 18:30
**Environment**: Supabase Production (spdtwktxdalcfigzeqrz)
**Migration**: `20260212_001400_ops_ui_rpcs.sql`

---

## Pre-Deployment Checklist

- [x] Migration created (`20260212_001400_ops_ui_rpcs.sql`)
- [x] Rollback script created (`rollback_ops_ui_rpcs.sql`)
- [x] Git commit created (a766951e)
- [x] Changes pushed to remote
- [ ] Migration tested locally
- [ ] RPCs tested with sample data
- [ ] Production secrets prepared (if needed)

---

## Deployment Steps

### 1. Link to Production Supabase

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo

# Link to production Supabase
supabase link --project-ref spdtwktxdalcfigzeqrz

# Verify link
supabase status
```

### 2. Review Migration Before Applying

```bash
# Review migration content
cat supabase/migrations/20260212_001400_ops_ui_rpcs.sql | head -100

# Expected: 3 tables, 4 RPC functions, RLS policies
```

### 3. Apply Migration to Production

```bash
# Apply migration
supabase db push

# Expected output:
# Applied migrations:
#   - 20260212_001400_ops_ui_rpcs.sql
```

### 4. Verify Tables Created

```sql
-- Connect to Supabase SQL Editor or use psql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 <<'SQL'
select table_name from information_schema.tables
where table_schema = 'ops'
  and table_name in ('backups', 'project_settings', 'project_upgrade_versions')
order by table_name;
SQL

-- Expected: 3 rows
-- backups
-- project_settings
-- project_upgrade_versions
```

### 5. Verify RPC Functions Created

```sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 <<'SQL'
select n.nspname as schema, p.proname as fn
from pg_proc p
join pg_namespace n on n.oid = p.pronamespace
where n.nspname = 'ops'
  and p.proname in ('ui_backups','ui_project_settings','ui_project_settings_upsert','ui_project_upgrade_versions')
order by 1,2;
SQL

-- Expected: 4 rows
-- ops | ui_backups
-- ops | ui_project_settings
-- ops | ui_project_settings_upsert
-- ops | ui_project_upgrade_versions
```

### 6. Verify RLS Enabled

```sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 <<'SQL'
select
  c.relname as table_name,
  c.relrowsecurity as rls_enabled
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname='ops'
  and c.relname in ('backups','project_settings','project_upgrade_versions')
order by c.relname;
SQL

-- Expected: 3 rows with rls_enabled = true
```

### 7. Smoke Test RPCs

```sql
-- Test with dummy project ID (replace with real ID if available)
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 <<'SQL'
select * from ops.ui_backups('00000000-0000-0000-0000-000000000000'::uuid, 10, 0);
select ops.ui_project_settings('00000000-0000-0000-0000-000000000000'::uuid);
select ops.ui_project_settings_upsert('00000000-0000-0000-0000-000000000000'::uuid, '{"theme":"dark"}'::jsonb);
select * from ops.ui_project_upgrade_versions('00000000-0000-0000-0000-000000000000'::uuid, 10, 0);
SQL

-- Expected: No errors (empty results if no data yet)
```

### 8. Seed Test Data (Optional)

```sql
-- Create test org if not exists
insert into registry.orgs (name) values ('Test Org')
on conflict do nothing
returning id;
-- Save org_id: [ORG_ID]

-- Create test project
insert into ops.projects (org_id, name, slug, repo_url, runtime_version)
values ('[ORG_ID]', 'Test Project', 'test-proj', 'github.com/test/proj', '19.0')
on conflict do nothing
returning id;
-- Save project_id: [PROJECT_ID]

-- Create test backup
insert into ops.backups (project_id, status, provider, region, size_bytes)
values ('[PROJECT_ID]', 'completed', 'supabase', 'us-east-1', 1024000000);

-- Create test settings
insert into ops.project_settings (project_id, settings)
values ('[PROJECT_ID]', '{"theme":"dark","autoBackup":true}'::jsonb);

-- Create test upgrade version
insert into ops.project_upgrade_versions (project_id, from_version, to_version, status)
values ('[PROJECT_ID]', '18.0', '19.0', 'completed');

-- Verify data
select * from ops.ui_backups('[PROJECT_ID]'::uuid, 10, 0);
select ops.ui_project_settings('[PROJECT_ID]'::uuid);
select * from ops.ui_project_upgrade_versions('[PROJECT_ID]'::uuid, 10, 0);
```

---

## Post-Deployment Checklist

- [ ] Migration applied successfully
- [ ] Tables exist in ops schema
- [ ] RPC functions exist and are callable
- [ ] RLS enabled on all tables
- [ ] Smoke test RPCs return expected results
- [ ] Test data created and retrieved successfully

---

## Rollback Plan (If Needed)

### Rollback Migration (DESTRUCTIVE)

```bash
# Execute rollback script
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f supabase/migrations/rollback_ops_ui_rpcs.sql

# Verify tables dropped
psql "$DATABASE_URL" -c "select table_name from information_schema.tables where table_schema = 'ops' and table_name in ('backups', 'project_settings', 'project_upgrade_versions');"

# Expected: 0 rows (tables dropped)
```

### Rollback Git Commit

```bash
# Revert commit
git revert a766951e

# Push revert
git push origin feat/odooops-browser-automation-integration
```

---

## Monitoring

### Health Checks

```bash
# Check RPC function logs (if available in Supabase)
# Navigate to: Supabase Dashboard → Database → Functions → ops.ui_backups

# Check database connections
psql "$DATABASE_URL" -c "select count(*) from ops.backups;"
psql "$DATABASE_URL" -c "select count(*) from ops.project_settings;"
psql "$DATABASE_URL" -c "select count(*) from ops.project_upgrade_versions;"
```

### Alerts

Set up alerts for:
- RPC execution errors (>1% error rate)
- RPC execution time (>500ms p95)
- Table growth rate (>1000 rows/day for backups)

---

## Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| Migration applied | Yes | ⏳ Pending |
| Tables created | 3/3 | ⏳ Pending |
| RPC functions created | 4/4 | ⏳ Pending |
| RLS enabled | Yes | ⏳ Pending |
| Smoke test passed | Yes | ⏳ Pending |
| Test data created | Yes | ⏳ Pending |

---

**Deployment Window**: 15 minutes
**Rollback Time**: 2 minutes (destructive)
**Team**: Solo deployment (Claude + human approval)
