# Supabase ops.* Schema Setup - Executive Summary

## Overview

Complete Supabase schema setup for the OdooOps Sh control plane (Odoo.sh replacement for self-hosted environments).

**Created**: 2026-02-15
**Project**: spdtwktxdalcfigzeqrz
**Spec Bundle**: `spec/odooops-sh/`
**Complete Guide**: `docs/implementation/supabase-ops-setup.md` (1,486 lines)

---

## What Was Created

### 1. Comprehensive Setup Guide
**File**: `docs/implementation/supabase-ops-setup.md`

**Contents**:
- 5 migration files (DDL, RPC, RLS, indexes)
- 9 ops.* table schemas
- 6 RPC functions for worker queue
- Complete RLS policy templates
- Setup verification commands
- Rollback procedures
- Concurrency test scripts
- Full lifecycle test examples

**Sections**:
1. Prerequisites & environment setup
2. Step 1: Breaking change migration (rename agent tables) ✅ **Already exists**
3. Step 2: Core schema (9 tables)
4. Step 3: RPC functions (worker queue & lifecycle)
5. Step 4: Row-level security policies
6. Step 5: Indexes & constraints
7. Complete setup script (bash)
8. Verification & testing
9. Rollback procedures

---

## Schema Architecture

### 9 Tables

| Table | Purpose | Key Features |
|-------|---------|--------------|
| `ops.projects` | Workspace containers | workspace_key, slug, odoo_version, status |
| `ops.workflows` | Workflow definitions | workflow_type (build\|test\|deploy\|backup\|upgrade) |
| `ops.runs` | Main execution queue | Worker claim pattern (SELECT FOR UPDATE SKIP LOCKED) |
| `ops.run_events` | Append-only event log | State changes, errors, warnings, info |
| `ops.run_artifacts` | Build output metadata | S3-style keys, checksums, expiry dates |
| `ops.run_logs` | Structured log lines | Full-text search, log levels |
| `ops.tools` | Docker image registry | Tool versions, image references |
| `ops.upgrade_advisories` | Breaking change warnings | Version pairs, severity, migration guides |
| `ops.project_memberships` | User access control | Roles: owner\|admin\|developer\|viewer |

### 6 RPC Functions

| Function | Purpose |
|----------|---------|
| `ops.claim_next_run(worker_id)` | Atomically claim next queued run |
| `ops.start_workflow_run(run_id, worker_id)` | Mark claimed run as running |
| `ops.complete_workflow_run(run_id, exit_code, error)` | Mark run as succeeded/failed |
| `ops.append_run_log(run_id, level, message, metadata)` | Append structured log entry |
| `ops.add_run_artifact(run_id, key, url, ...)` | Store artifact metadata |
| `ops.list_queued_runs()` | Admin queue view |

---

## State Machine

```
queued → claimed → running → succeeded
                         ↓
                      failed
                         ↓
                     canceled
```

**State Transitions**:
- **queued**: Created, waiting for worker
- **claimed**: Worker called `ops.claim_next_run()`
- **running**: Worker called `ops.start_workflow_run()`
- **succeeded**: Exit code 0, artifacts uploaded
- **failed**: Non-zero exit code or error
- **canceled**: Manual stop (future)

**Enforced by**: Trigger `enforce_run_status_transition`

---

## Security Model

**RLS Policies**:
- **Project Isolation**: Users can only access their project's data
- **Role Hierarchy**: owner > admin > developer > viewer
- **Service Role Bypass**: Edge Functions use service role (bypasses RLS)

**Helper Functions**:
- `ops.current_user_id()` - Get authenticated user ID
- `ops.current_user_role(project_id)` - Get user's role in project

**Policy Examples**:
- Members can view all data in their projects (SELECT)
- Developers+ can create runs and workflows (INSERT)
- Owners can modify project settings (UPDATE)
- All authenticated users can view tools and advisories (global read-only)

---

## Migration Timeline

| Migration | Purpose | Status |
|-----------|---------|--------|
| `20260213_000001` | Rename agent tables (breaking change) | ✅ **EXISTS** |
| `20260213_000100` | Create 9 ops.* tables | 📝 **READY** |
| `20260213_000200` | Create 6 RPC functions | 📝 **READY** |
| `20260213_000300` | Create RLS policies | 📝 **READY** |
| `20260213_000400` | Create indexes & constraints | 📝 **READY** |

---

## Quick Start

### Apply Migrations

```bash
# Navigate to project
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo

# Link to Supabase
supabase link --project-ref spdtwktxdalcfigzeqrz

# Apply all migrations
supabase db push --linked
```

### Verify Schema

```bash
# List all ops.* tables
psql "$SUPABASE_URL" -c "SELECT tablename FROM pg_tables WHERE schemaname='ops' ORDER BY tablename;"

# Expected output: 9 tables
#  projects
#  workflows
#  runs
#  run_events
#  run_artifacts
#  run_logs
#  tools
#  upgrade_advisories
#  project_memberships

# List RPC functions
psql "$SUPABASE_URL" -c "\df ops.*"

# Expected: 6+ functions (including helper functions)
```

### Test Worker Queue

```bash
# Create test project, workflow, run (see full guide for script)

# Claim run (atomic operation)
psql "$SUPABASE_URL" -c "SELECT ops.claim_next_run('test-worker');"

# Expected: JSON response with run_id, project_id, workflow_id
```

---

## Next Steps

### 1. Edge Function Updates (Required)

**2 Edge Functions need table reference updates**:

```bash
# Update ops-ingest function
supabase functions deploy ops-ingest
# Changes: ops.runs → ops.agent_runs

# Update executor function
supabase functions deploy executor
# Changes: ops.run_logs → ops.agent_run_logs
```

### 2. Script Integration

**Update 3 scripts** in `scripts/odooops/`:

```bash
# env_create.sh: Insert into ops.runs
# env_wait_ready.sh: Query run status
# env_destroy.sh: Mark run as canceled
```

### 3. Documentation

**Create additional documentation**:

```bash
# ERD diagram
spec/odooops-sh/schema.mmd

# DBML schema
spec/odooops-sh/schema.dbml

# Prisma schema (for Next.js console)
supabase gen types typescript --linked > lib/database.types.ts
```

### 4. CI Integration

**Create workflow**: `.github/workflows/odooops-sh-spec-gates.yml`

**Validation jobs**:
1. validate-spec-kit: Check 4 spec files exist
2. validate-schema: Migration syntax, DBML, ERD presence
3. validate-prisma: Schema validation, TypeScript generation
4. validate-docs: 5 documentation files, markdown link check

---

## Reference Documentation

| File | Purpose |
|------|---------|
| `docs/implementation/supabase-ops-setup.md` | Complete setup guide (this summary's source) |
| `spec/odooops-sh/constitution.md` | Core principles and SSOT boundaries |
| `spec/odooops-sh/prd.md` | Product requirements and user stories |
| `spec/odooops-sh/plan.md` | 6-week implementation timeline |
| `docs/odooops-sh/ARCHITECTURE.md` | System architecture layers |
| `docs/odooops-sh/RUN_LIFECYCLE.md` | Run state machine documentation |
| `docs/odooops-sh/SECURITY.md` | RLS policy explanations |

---

## Verification Checklist

- [x] Setup guide created (`docs/implementation/supabase-ops-setup.md`)
- [x] Migration file structures defined (5 files)
- [x] Breaking change migration exists (`20260213_000001`)
- [x] RLS policy templates created
- [x] Setup verification commands documented
- [x] Rollback procedures documented
- [x] Concurrency test script provided
- [x] Full lifecycle test example provided
- [ ] Migrations applied to Supabase (pending)
- [ ] Edge Functions updated (pending)
- [ ] Scripts integrated (pending)
- [ ] CI workflow created (pending)

---

**Created**: 2026-02-15
**Status**: Complete documentation ✅
**Next Action**: Apply migrations to Supabase `spdtwktxdalcfigzeqrz`
