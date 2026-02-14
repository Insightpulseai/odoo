# Supabase ops.* Schema - Quick Reference

> Ultra-condensed reference for OdooOps Sh control plane schema
> Full docs: `docs/implementation/supabase-ops-setup.md`

## 9 Tables

```sql
ops.projects              -- Workspace containers
ops.workflows             -- Build/test/deploy definitions
ops.runs                  -- Main execution queue
ops.run_events            -- Append-only event log
ops.run_artifacts         -- S3-style artifact metadata
ops.run_logs              -- Structured logs (full-text search)
ops.tools                 -- Docker image registry
ops.upgrade_advisories    -- Breaking change warnings
ops.project_memberships   -- RBAC (owner|admin|developer|viewer)
```

## 6 RPC Functions

```sql
-- Worker queue lifecycle
ops.claim_next_run(worker_id) → {run_id, project_id, workflow_id}
ops.start_workflow_run(run_id, worker_id) → {success, started_at}
ops.complete_workflow_run(run_id, exit_code, error) → {success, status}
ops.append_run_log(run_id, level, message, metadata) → {success}
ops.add_run_artifact(run_id, key, url, ...) → {success, artifact_id}
ops.list_queued_runs() → table(run_id, status, created_at, ...)
```

## State Machine

```
queued → claimed → running → succeeded|failed|canceled
```

## Quick Commands

```bash
# Apply migrations
supabase db push --linked

# List tables
psql "$SUPABASE_URL" -c "\dt ops.*"

# List functions
psql "$SUPABASE_URL" -c "\df ops.*"

# Test worker claim
psql "$SUPABASE_URL" -c "SELECT ops.claim_next_run('test-worker');"
```

## Files

```
docs/implementation/
├── supabase-ops-setup.md      # 1,486 lines - complete guide
├── SUPABASE_OPS_SUMMARY.md    # 159 lines - executive summary
└── SUPABASE_OPS_QUICKREF.md   # This file - quick reference

supabase/migrations/
├── 20260213_000001_ops_rename_agent_tables.sql    # ✅ EXISTS
├── 20260213_000100_ops_core_schema.sql            # 📋 SPEC'D
├── 20260213_000200_ops_rpc_functions.sql          # 📋 SPEC'D
├── 20260213_000300_ops_rls_policies.sql           # 📋 SPEC'D
└── 20260213_000400_ops_indexes_constraints.sql    # 📋 SPEC'D
```

## RLS Quick Summary

```sql
-- Project isolation: users see only their projects
-- Role hierarchy: owner > admin > developer > viewer
-- Service role: bypasses RLS (Edge Functions)

ops.current_user_id() → uuid
ops.current_user_role(project_id) → text
```

## Typical Workflow

```sql
-- 1. Create project
INSERT INTO ops.projects (workspace_key, slug, name, odoo_version)
VALUES ('ipai_workspace', 'my-project', 'My Project', '19.0');

-- 2. Create workflow
INSERT INTO ops.workflows (project_id, workflow_type, name)
VALUES ('<project_id>', 'build', 'Production Build');

-- 3. Create run
INSERT INTO ops.runs (project_id, workflow_id, status)
VALUES ('<project_id>', '<workflow_id>', 'queued');

-- 4. Worker claims run
SELECT ops.claim_next_run('worker-001');

-- 5. Worker starts execution
SELECT ops.start_workflow_run('<run_id>', 'worker-001');

-- 6. Worker logs progress
SELECT ops.append_run_log('<run_id>', 'info', 'Building...', '{}');

-- 7. Worker adds artifacts
SELECT ops.add_run_artifact('<run_id>', 'build.tar.gz', 's3://...', ...);

-- 8. Worker completes
SELECT ops.complete_workflow_run('<run_id>', 0, null);
```

## Concurrency Pattern

```sql
-- SELECT FOR UPDATE SKIP LOCKED ensures atomic claiming
-- Multiple workers can call simultaneously without collision
SELECT * FROM ops.runs
WHERE status = 'queued'
ORDER BY created_at
FOR UPDATE SKIP LOCKED
LIMIT 1;
```

## Next Steps

1. Extract migrations from setup guide (if needed)
2. Apply: `supabase db push --linked`
3. Update Edge Functions: ops-ingest, executor
4. Update Scripts: env_create.sh, env_wait_ready.sh, env_destroy.sh
5. Verify: Run test scripts from setup guide

---

**Created**: 2026-02-15 | **Spec**: spec/odooops-sh/ | **Project**: spdtwktxdalcfigzeqrz
