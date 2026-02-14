# OdooOps Sh Implementation Plan

## Overview

6-week phased rollout of Odoo.sh-style control plane for self-hosted Odoo environments.

## Week 1: Breaking Changes + Spec Kit

**Deliverables**:
- Migration 20260213_000001: Rename agent tables (ops.runs → ops.agent_runs)
- Update 2 Edge Functions (ops-ingest, executor)
- Create Spec Kit bundle (4 files)
- Verify no data loss

**Risk**: Agent tracking disruption
**Mitigation**: Test Edge Functions before deploying

## Week 2: Core Schema Implementation

**Deliverables**:
- Migration 20260213_000100: Create 9 ops.* tables
- DBML schema documentation
- Mermaid ERD diagram
- Prisma schema for Next.js console

**Tables**:
1. ops.projects (workspace containers)
2. ops.workflows (workflow definitions)
3. ops.runs (main queue table)
4. ops.run_events (append-only log)
5. ops.run_artifacts (build outputs)
6. ops.run_logs (structured logs)
7. ops.tools (Docker registry)
8. ops.upgrade_advisories (breaking changes)
9. ops.project_memberships (user access)

**Verification**:
```bash
psql "$SUPABASE_DB_URL" -c "\d ops.projects"
psql "$SUPABASE_DB_URL" -c "SELECT tablename FROM pg_tables WHERE schemaname='ops' ORDER BY tablename;"
```

## Week 3: RPC Functions

**Deliverables**:
- Migration 20260213_000200: 6 RPC functions
- Concurrency test script
- Idempotency validation

**Functions**:
1. ops.claim_next_run(p_worker_id) - Worker queue claiming
2. ops.start_workflow_run(p_run_id, p_worker_id) - Mark as running
3. ops.complete_workflow_run(p_run_id, p_exit_code, p_error_message) - Finish run
4. ops.append_run_log(p_run_id, p_level, p_message, p_metadata) - Log entry
5. ops.add_run_artifact(p_run_id, p_artifact_key, p_s3_url, ...) - Store artifact
6. ops.list_queued_runs() - Admin queue view

**Concurrency Test**:
```sql
-- Insert 5 queued runs
-- 3 workers call ops.claim_next_run() concurrently
-- Verify each worker gets unique run, no collisions
```

## Week 4: CI Integration

**Deliverables**:
- .github/workflows/odooops-sh-spec-gates.yml
- scripts/validate_spec_kit_odooops.sh
- Integration with existing spec gates

**Validation Jobs**:
1. validate-spec-kit: Check 4 files exist
2. validate-schema: Migration syntax, DBML, ERD presence
3. validate-prisma: Schema validation, TypeScript generation
4. validate-docs: 5 documentation files, markdown link check

## Week 5: Documentation

**Deliverables**:
- docs/odooops-sh/ARCHITECTURE.md (5 layers)
- docs/odooops-sh/DATA_BOUNDARIES.md (Odoo vs Supabase)
- docs/odooops-sh/RUN_LIFECYCLE.md (state machine)
- docs/odooops-sh/CICD.md (workflow orchestration)
- docs/odooops-sh/SECURITY.md (RLS policies)

## Week 6: Integration Testing

**Deliverables**:
- Update scripts/odooops/env_create.sh (insert into ops.runs)
- Update scripts/odooops/env_wait_ready.sh (query run status)
- Update scripts/odooops/env_destroy.sh (mark canceled)
- End-to-end test suite

**Integration Points**:
```bash
# env_create.sh creates queued run
./scripts/odooops/env_create.sh my-project build main abc123
# Returns run_id

# Worker claims and executes
psql -c "SELECT * FROM ops.claim_next_run('worker-001');"

# env_wait_ready.sh polls status
./scripts/odooops/env_wait_ready.sh <run_id>

# Verify logs
psql -c "SELECT * FROM ops.run_logs WHERE run_id = '<run_id>' ORDER BY timestamp;"
```

## Timeline

```
Week 1: Breaking Changes + Spec Kit
Week 2: Core Schema (9 tables)
Week 3: RPC Functions (6 functions)
Week 4: CI Integration (2 workflows)
Week 5: Documentation (5 files)
Week 6: Integration Testing (3 scripts)
```

**Total Effort**: 6 weeks (120 hours)
