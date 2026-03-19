# Supabase Database Linter - Security Remediation Plan

**Status**: 🔴 CRITICAL - 36 security issues detected
**Date**: 2026-01-01
**Database**: Supabase PostgreSQL (project: `spdtwktxdalcfigzeqrz`)

---

## Executive Summary

Supabase Database Linter flagged **36 security issues** across 2 categories:

1. **SECURITY DEFINER Views** (25 views) - Views bypassing RLS enforcement
2. **RLS Disabled** (11 tables) - Public tables without Row Level Security

**Impact**: EXTERNAL facing (accessible via PostgREST API)
**Risk Level**: ERROR (immediate remediation required)

---

## Issue Breakdown

### Issue 1: SECURITY DEFINER Views (25 views)

**Problem**: Views defined with `SECURITY DEFINER` run with creator's privileges, bypassing RLS policies of the querying user.

**Risk**: Potential privilege escalation, unauthorized data access

**Affected Views**:

#### Public Schema (15 views)
1. `v_kpi_summary` - KPI dashboard aggregation
2. `current_production_deployment` - Deployment status
3. `v_planner_bucket_status_counts` - Planning metrics
4. `v_period_progress` - Period tracking
5. `v_tx_trends` - Transaction trends
6. `current_dev_deployment` - Dev deployment status
7. `deployment_summary` - Deployment overview
8. `v_product_mix` - Product analytics
9. `v_employee_workload` - Workload metrics
10. `v_geo_regions` - Geographic analysis
11. `preset_docs_cron_status` - Cron job status
12. `preset_docs_latest` - Latest documentation
13. `v_data_health_summary` - Data quality metrics
14. `v_brand_performance` - Brand analytics
15. `v_task_dashboard` - Task overview
16. `current_staging_deployment` - Staging deployment status

#### Odoo Schema (10 views)
1. `v_planner_bucket_status_counts` - Planner bucket metrics
2. `v_planner_data_integrity` - Data integrity checks
3. `v_planner_plan_status_counts` - Plan status metrics
4. `v_planner_task_status_bucket` - Task bucket status
5. `v_planner_task_grid` - Task grid view
6. `v_enabled_modules` - Enabled Odoo modules
7. `v_planner_priority_status_counts` - Priority metrics
8. `v_planner_member_status_counts` - Member status
9. `v_planner_recurrence_health` - Recurrence health
10. `v_planner_task_schedule` - Task schedule

**Remediation Options**:

**Option A: Convert to SECURITY INVOKER (Recommended)**
```sql
-- Drop and recreate view without SECURITY DEFINER
DROP VIEW IF EXISTS public.v_kpi_summary;
CREATE OR REPLACE VIEW public.v_kpi_summary AS
  SELECT ... -- original query
;
-- Default is SECURITY INVOKER (respects querying user's RLS)
```

**Option B: Document Justification (If SECURITY DEFINER Required)**
```sql
COMMENT ON VIEW public.v_kpi_summary IS
  'SECURITY DEFINER: Required for cross-schema analytics aggregation.
   Justification: [specific reason]
   Reviewer: [name]
   Review Date: 2026-01-01
   Next Review: 2026-04-01';
```

**Action Required**: Review each view to determine if SECURITY DEFINER is intentional or can be safely removed.

---

### Issue 2: RLS Disabled on Public Tables (11 tables)

**Problem**: Tables exposed via PostgREST without RLS protection allow unrestricted access.

**Risk**: Data breach, unauthorized data modification

**Affected Tables**:

| Schema | Table | Description | Tenant Isolation Column |
|--------|-------|-------------|-------------------------|
| odoo | module_catalog | Odoo module metadata | N/A (reference data) |
| public | activity_types | Activity type reference | N/A (reference data) |
| public | clusters | Data clusters | company_id (assumed) |
| public | task_templates | Task templates | N/A (reference data) |
| public | categories | Category reference | N/A (reference data) |
| public | employees | Employee records | company_id |
| public | bir_forms | BIR form reference | N/A (reference data) |
| public | bir_filings | BIR filing records | company_id, employee_id |
| public | tasks | Task records | company_id, assigned_to |
| public | task_activities | Task activity log | task_id (inherited) |
| public | schema_migrations | Migration history | N/A (system table) |

**Remediation Applied**:

1. **Enable RLS on all tables**:
```sql
ALTER TABLE public.activity_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.employees ENABLE ROW LEVEL SECURITY;
-- ... (all 11 tables)
```

2. **Create appropriate RLS policies**:

**Reference Data Tables** (read-only):
- `activity_types`, `categories`, `bir_forms` - Allow SELECT for all
- `task_templates`, `module_catalog` - Allow SELECT for authenticated users

**Multi-Tenant Tables** (company_id isolation):
- `employees` - Filter by `app.current_company_id`
- `clusters` - Filter by `app.current_company_id`
- `bir_filings` - Filter by `app.current_company_id` OR `app.current_user_id`

**User-Scoped Tables** (user ownership):
- `tasks` - Filter by `company_id` OR `assigned_to` OR `created_by`
- `task_activities` - Inherit access from parent task

**System Tables** (admin only):
- `schema_migrations` - Restrict to `service_role`

---

## Deployment Plan

### Phase 1: Immediate Actions (Priority 1)

1. **Deploy RLS Remediation Migration**:
```bash
psql "$POSTGRES_URL" -f supabase/migrations/20250101_security_linter_remediation.sql
```

2. **Verify RLS Enablement**:
```sql
SELECT
  n.nspname AS schema_name,
  c.relname AS table_name,
  c.relrowsecurity AS rls_enabled
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname IN ('public', 'odoo')
  AND c.relkind = 'r'
ORDER BY n.nspname, c.relname;
```

3. **Test RLS Policies**:
```sql
-- Set test context
SET app.current_company_id = '1';
SET app.current_user_id = '123';

-- Verify tenant isolation
SELECT * FROM public.employees;  -- Should only show company_id=1
SELECT * FROM public.tasks;      -- Should show company_id=1 OR assigned_to=123
```

### Phase 2: SECURITY DEFINER View Review (Priority 2)

**For Each View**:
1. Review view definition and purpose
2. Determine if SECURITY DEFINER is required
3. Choose remediation:
   - **Remove**: Convert to SECURITY INVOKER (default)
   - **Keep**: Document justification with quarterly review schedule

**Review Template**:
```markdown
View: public.v_kpi_summary
Purpose: Cross-schema analytics aggregation
SECURITY DEFINER Required: YES/NO
Justification: [Specific reason if YES]
Alternative Approach: [If NO, describe SECURITY INVOKER implementation]
Reviewer: [Name]
Review Date: 2026-01-01
Next Review: 2026-04-01
```

### Phase 3: Performance Optimization (Priority 3)

**Add Indexes for RLS Filter Columns**:
```sql
CREATE INDEX IF NOT EXISTS idx_employees_company_id ON public.employees(company_id);
CREATE INDEX IF NOT EXISTS idx_tasks_company_id ON public.tasks(company_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON public.tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_bir_filings_company_id ON public.bir_filings(company_id);
CREATE INDEX IF NOT EXISTS idx_bir_filings_employee_id ON public.bir_filings(employee_id);
```

**Monitor Query Performance**:
```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries >1s
SELECT pg_reload_conf();

-- Monitor slow queries
SELECT * FROM pg_stat_statements
WHERE query LIKE '%employees%' OR query LIKE '%tasks%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## Testing Protocol

### Test 1: RLS Enforcement
```sql
-- Create test user context
SET app.current_company_id = '1';
SET app.current_user_id = '100';

-- Test multi-tenant isolation (should only see company_id=1)
SELECT COUNT(*) FROM public.employees WHERE company_id = 1;  -- Should return N
SELECT COUNT(*) FROM public.employees WHERE company_id = 2;  -- Should return 0

-- Test user ownership (should see assigned tasks)
SELECT COUNT(*) FROM public.tasks WHERE assigned_to = 100;  -- Should return N
SELECT COUNT(*) FROM public.tasks WHERE assigned_to = 200;  -- Should return 0
```

### Test 2: Reference Data Access
```sql
-- Reference data should be readable by all
SELECT COUNT(*) FROM public.activity_types;  -- Should return total count
SELECT COUNT(*) FROM public.categories;      -- Should return total count
```

### Test 3: Service Role Bypass
```sql
-- Service role should bypass RLS
SET ROLE service_role;
SELECT COUNT(*) FROM public.employees;  -- Should return ALL records
RESET ROLE;
```

### Test 4: SECURITY DEFINER Views (If Retained)
```sql
-- Set non-privileged user context
SET app.current_company_id = '1';

-- View should return cross-company aggregation (if SECURITY DEFINER)
SELECT * FROM public.v_kpi_summary;

-- Verify no unauthorized data exposure
-- Review returned data for company_id=2, 3, etc.
```

---

## Rollback Plan

If RLS policies cause production issues:

### Quick Disable (Emergency Only)
```sql
-- Disable RLS on specific table (TEMPORARY)
ALTER TABLE public.employees DISABLE ROW LEVEL SECURITY;

-- Re-enable after fix
ALTER TABLE public.employees ENABLE ROW LEVEL SECURITY;
```

### Full Rollback
```sql
-- Drop all policies
DROP POLICY IF EXISTS "employees_tenant_isolation" ON public.employees;
DROP POLICY IF EXISTS "tasks_user_access" ON public.tasks;
-- ... (all policies)

-- Disable RLS
ALTER TABLE public.employees DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.tasks DISABLE ROW LEVEL SECURITY;
-- ... (all tables)
```

**CAUTION**: Disabling RLS exposes data. Only use as emergency measure with immediate remediation plan.

---

## Post-Deployment Monitoring

### Metrics to Track

1. **RLS Coverage**:
```sql
SELECT
  COUNT(CASE WHEN c.relrowsecurity THEN 1 END) AS rls_enabled,
  COUNT(*) AS total_tables,
  ROUND(100.0 * COUNT(CASE WHEN c.relrowsecurity THEN 1 END) / COUNT(*), 2) AS coverage_pct
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname IN ('public', 'odoo') AND c.relkind = 'r';
```

2. **Policy Count**:
```sql
SELECT schemaname, tablename, COUNT(*) AS policies
FROM pg_policies
WHERE schemaname IN ('public', 'odoo')
GROUP BY schemaname, tablename
ORDER BY schemaname, tablename;
```

3. **Query Performance**:
```sql
SELECT
  query,
  calls,
  mean_exec_time,
  max_exec_time
FROM pg_stat_statements
WHERE query ILIKE '%employees%' OR query ILIKE '%tasks%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

4. **Access Denials** (application logs):
- Monitor for increased "permission denied" errors
- Track RLS policy violations
- Identify missing policies or incorrect configurations

---

## Next Steps

### Immediate (24 hours)
- [x] Create remediation migration
- [ ] Deploy RLS policies to production
- [ ] Test RLS with actual user contexts
- [ ] Monitor for access errors

### Short-term (1 week)
- [ ] Review all 25 SECURITY DEFINER views
- [ ] Document justifications or convert to SECURITY INVOKER
- [ ] Add performance indexes for RLS filter columns
- [ ] Update application code to set session variables (`app.current_company_id`)

### Medium-term (1 month)
- [ ] Quarterly review schedule for SECURITY DEFINER views
- [ ] Performance tuning based on query logs
- [ ] Additional RLS policies for newly exposed tables
- [ ] Security audit of all PostgREST endpoints

### Long-term (Ongoing)
- [ ] Automated RLS coverage monitoring (CI/CD)
- [ ] Security linter integration in deployment pipeline
- [ ] Regular security reviews (quarterly)
- [ ] Developer training on RLS best practices

---

## Resources

- **Supabase RLS Guide**: https://supabase.com/docs/guides/auth/row-level-security
- **Database Linter Docs**: https://supabase.com/docs/guides/database/database-linter
- **SECURITY DEFINER Risks**: https://supabase.com/docs/guides/database/database-linter?lint=0010_security_definer_view
- **RLS Best Practices**: https://supabase.com/docs/guides/database/database-linter?lint=0013_rls_disabled_in_public

---

**Remediation Status**: 🟡 IN PROGRESS
**Next Review**: 2026-02-14
**Owner**: Database Security Team

---

## Batch 2 Remediation (2026-02-07)

### New Findings: 47 issues

**Linter re-scan** on 2026-02-07 detected additional security issues not covered by Batch 1:

#### SECURITY DEFINER Views (2 new)

| Schema | View | Action |
|--------|------|--------|
| public | `view_system_health_hourly` | Converted to SECURITY INVOKER |
| public | `AssetSearchView` | Converted to SECURITY INVOKER |

#### RLS Disabled (42 new tables)

**High Risk (sensitive columns)**:
- `public.user` (password, token)
- `public.api_secrets`
- `public.project_member_invite` (token)
- `public.workspace_member_invite` (token)
- `public.social_login_connection`
- `public.SsoDetails`
- `public.UserOrganization`

**Auth / Permissions**:
- `public.auth_permission`, `public.auth_group`, `public.auth_group_permissions`
- `public.user_groups`, `public.user_user_permissions`

**Workspace / Team / Project hierarchy**:
- `public.workspace`, `public.workspace_member`
- `public.team`, `public.team_member`
- `public.project`, `public.project_member`, `public.project_identifier`

**Issue tracking**:
- `public.issue`, `public.issue_timeline`, `public.issue_sequence`
- `public.issue_property`, `public.issue_label`, `public.issue_blocker`
- `public.issue_assignee`, `public.issue_activity`, `public.issue_comment`

**Cycles / Modules / Misc**:
- `public.state`, `public.cycle`, `public.cycle_issue`
- `public.label`, `public.shortcut`, `public.file_asset`, `public.view`
- `public.module`, `public.module_member`, `public.module_issues`

**System / Migration tables**:
- `public.django_migrations`, `public.django_content_type`
- `public._prisma_migrations`, `public._AssetToTag`

**OPS schema**:
- `ops.model_repo_scans`

#### Sensitive Columns Exposed (3 tables)

| Table | Sensitive Columns | Policy |
|-------|-------------------|--------|
| `public.user` | password, token | service_role OR owner only |
| `public.project_member_invite` | token | service_role OR accepted_by |
| `public.workspace_member_invite` | token | service_role OR accepted_by |

### Migration File

`supabase/migrations/20260207_security_definer_views_rls_remediation.sql`

### RLS Policy Strategy

| Table Category | SELECT Policy | Write Policy |
|----------------|---------------|--------------|
| Sensitive (passwords/tokens) | service_role OR owner | service_role only |
| Auth/Permissions | authenticated | service_role only |
| Workspace/Team/Project | membership-based | service_role only |
| Issue tracking | project membership | service_role only |
| Reference data (state, label) | authenticated | service_role only |
| System/Migration tables | service_role only | service_role only |
