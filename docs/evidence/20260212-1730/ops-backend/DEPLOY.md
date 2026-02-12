# ops.* Backend Deployment Checklist

**Date**: 2026-02-12 17:30
**Environment**: Supabase Production (spdtwktxdalcfigzeqrz)

---

## Pre-Deployment Checklist

- [x] Schema migrations created (4 files)
- [x] Edge Functions implemented (3 files)
- [x] UI pages wired to RPCs (2 pages)
- [x] Git commit created (d2e2d75a)
- [ ] Migrations tested locally
- [ ] Edge Functions tested locally
- [ ] UI tested with demo data
- [ ] Production secrets prepared

---

## Deployment Steps

### 1. Apply Migrations to Production

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo

# Link to production Supabase
supabase link --project-ref spdtwktxdalcfigzeqrz

# Review migrations before applying
cat supabase/migrations/20260212_001*.sql | head -100

# Apply migrations
supabase db push

# Verify schema
supabase db diff

# Expected: No differences (migrations applied cleanly)
```

**Verification SQL**:
```sql
-- Check tables
select count(*) from information_schema.tables where table_schema = 'ops';
-- Expected: 10

-- Check functions
select count(*) from information_schema.routines where routine_schema = 'ops';
-- Expected: 12+

-- Check RLS policies
select schemaname, tablename, count(*) as policy_count
from pg_policies
where schemaname = 'ops'
group by schemaname, tablename;
-- Expected: 10 tables with 1-3 policies each
```

### 2. Generate and Set Secrets

```bash
# Generate secure tokens
OPS_INGEST_TOKEN=$(openssl rand -hex 32)
OPS_ADVISORY_SCAN_TOKEN=$(openssl rand -hex 32)

# Store tokens in ~/.zshrc (optional, for reference)
echo "export OPS_INGEST_TOKEN='$OPS_INGEST_TOKEN'" >> ~/.zshrc
echo "export OPS_ADVISORY_SCAN_TOKEN='$OPS_ADVISORY_SCAN_TOKEN'" >> ~/.zshrc

# Set secrets in Supabase
supabase secrets set \
  SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co" \
  SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_ROLE_KEY" \
  SUPABASE_ANON_KEY="$SUPABASE_ANON_KEY" \
  OPS_INGEST_TOKEN="$OPS_INGEST_TOKEN" \
  OPS_ADVISORY_SCAN_TOKEN="$OPS_ADVISORY_SCAN_TOKEN"

# Verify secrets set
supabase secrets list
```

### 3. Deploy Edge Functions

```bash
# Deploy ops-trigger-build
supabase functions deploy ops-trigger-build

# Deploy ops-metrics-ingest
supabase functions deploy ops-metrics-ingest

# Deploy ops-advisory-scan
supabase functions deploy ops-advisory-scan

# Verify deployments
supabase functions list
```

**Expected Output**:
```
NAME                    CREATED AT           VERSION    STATUS
ops-trigger-build       2026-02-12 17:30:00  1          ACTIVE
ops-metrics-ingest      2026-02-12 17:31:00  1          ACTIVE
ops-advisory-scan       2026-02-12 17:32:00  1          ACTIVE
```

### 4. Test Edge Functions

```bash
# Test metrics ingest
curl -X POST https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/ops-metrics-ingest \
  -H "content-type: application/json" \
  -H "x-ops-ingest-token: $OPS_INGEST_TOKEN" \
  -d '{
    "project_id": "00000000-0000-0000-0000-000000000000",
    "ts": "2026-02-12T17:30:00Z",
    "samples": [
      {"metric": "cpu_pct", "value": 45.2},
      {"metric": "mem_mb", "value": 1024}
    ]
  }'

# Expected: {"inserted": 2}

# Test advisory scan (requires valid project)
curl -X POST https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/ops-advisory-scan \
  -H "content-type: application/json" \
  -H "x-ops-advisory-token: $OPS_ADVISORY_SCAN_TOKEN"

# Expected: {"advisories_created": N}
```

### 5. Seed Initial Data (Optional)

```sql
-- Create test org
insert into registry.orgs (name) values ('InsightPulse AI')
returning id;
-- Save org_id: [ORG_ID]

-- Create test project
insert into ops.projects (org_id, name, slug, repo_url, runtime_version)
values ('[ORG_ID]', 'Production ERP', 'prod-erp', 'github.com/insightpulseai/odoo', '19.0')
returning id;
-- Save project_id: [PROJECT_ID]

-- Create production branch
insert into ops.branches (project_id, name, stage, is_production)
values ('[PROJECT_ID]', 'main', 'production', true)
returning id;
-- Save branch_id: [BRANCH_ID]

-- Create test build
insert into ops.builds (project_id, branch_id, status, trigger, commit_sha)
values ('[PROJECT_ID]', '[BRANCH_ID]', 'success', 'manual', 'abc123')
returning id;

-- Verify data
select * from ops.list_projects();
select * from ops.project_branches('[PROJECT_ID]');
```

### 6. Deploy UI to Vercel

```bash
cd templates/odooops-console

# Set environment variables in Vercel
vercel env add NEXT_PUBLIC_SUPABASE_URL production
# Value: https://spdtwktxdalcfigzeqrz.supabase.co

vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# Value: [SUPABASE_ANON_KEY]

# Deploy to production
vercel --prod

# Expected output:
# Production: https://odooops-console.vercel.app
```

### 7. Configure DNS

```bash
# Add CNAME record in Cloudflare
# Name: ops
# Target: cname.vercel-dns.com
# Proxy: No (DNS only)

# Wait for DNS propagation
dig ops.insightpulseai.com

# Add domain in Vercel
vercel domains add ops.insightpulseai.com
```

### 8. E2E Verification

```bash
# Test projects page
curl -s https://ops.insightpulseai.com/app/projects | grep "Projects"

# Test API (after authentication)
curl -s https://ops.insightpulseai.com/api/ops/projects \
  -H "Cookie: [AUTH_COOKIE]" | jq .

# Expected: {"projects": [...]}
```

---

## Post-Deployment Checklist

- [ ] Migrations applied successfully
- [ ] Edge Functions deployed and active
- [ ] Secrets configured correctly
- [ ] Test data created
- [ ] UI deployed to Vercel
- [ ] DNS configured (ops.insightpulseai.com)
- [ ] Projects page loads
- [ ] Branches page loads
- [ ] Build trigger works
- [ ] Metrics ingest works
- [ ] Advisory scan works

---

## Rollback Plan

### Rollback Migrations (DESTRUCTIVE)
```sql
-- Drop ops schema (will delete all data)
drop schema if exists ops cascade;

-- Re-apply previous migration state
supabase db reset
```

### Rollback Edge Functions
```bash
# Delete functions
supabase functions delete ops-trigger-build
supabase functions delete ops-metrics-ingest
supabase functions delete ops-advisory-scan
```

### Rollback UI
```bash
# Revert to previous Vercel deployment
vercel rollback

# Or redeploy from previous commit
git checkout HEAD~1
vercel --prod
```

---

## Monitoring

### Health Checks

```bash
# Check Edge Function logs
supabase functions logs ops-trigger-build
supabase functions logs ops-metrics-ingest
supabase functions logs ops-advisory-scan

# Check database connections
psql "$SUPABASE_DATABASE_URL" -c "select count(*) from ops.projects;"

# Check UI uptime
curl -I https://ops.insightpulseai.com/app/projects
```

### Alerts

Set up alerts for:
- Edge Function errors (>1% error rate)
- RPC execution time (>500ms p95)
- Database connection pool saturation (>80%)
- UI uptime (availability <99%)

---

## Known Issues

1. **Build Queue**: No runner implemented yet (ops.run_queue will fill but not execute)
2. **Metrics Rollup**: Materialized view not scheduled for refresh
3. **Advisory Scan**: No cron schedule (manual trigger only)
4. **UI Pages**: Only 2/21 pages wired (projects, branches)

**Mitigations**:
- Implement Pulser/Codex runner for build queue (Phase 2)
- Schedule pg_cron for metrics rollup and advisory scan
- Wire remaining 19 UI pages incrementally

---

## Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| Migrations applied | 4/4 | ⏳ Pending |
| Edge Functions deployed | 3/3 | ⏳ Pending |
| Secrets configured | 5/5 | ⏳ Pending |
| Test data created | Yes | ⏳ Pending |
| UI deployed | Yes | ⏳ Pending |
| DNS configured | Yes | ⏳ Pending |
| Projects page working | Yes | ⏳ Pending |
| Branches page working | Yes | ⏳ Pending |

---

**Deployment Window**: 30 minutes
**Rollback Time**: 5 minutes (destructive)
**Team**: Solo deployment (Claude + human approval)
