# OdooOps Sh Task Breakdown

## P0 Tasks (Must Have - Week 1-3)

### Breaking Changes (Week 1)
- [x] Create migration 20260213_000001_ops_rename_agent_tables.sql
- [ ] Test migration on local Supabase
- [x] Update supabase/functions/ops-ingest/index.ts (5 references)
- [x] Update supabase/functions/executor/index.ts (1 reference)
- [ ] Verify Edge Functions work after rename
- [ ] Deploy to staging
- [ ] Verify no data loss
- [ ] Deploy to production

### Spec Kit Bundle (Week 1)
- [x] Create spec/odooops-sh/constitution.md (25 lines)
- [x] Create spec/odooops-sh/prd.md (111 lines)
- [x] Create spec/odooops-sh/plan.md (309 lines)
- [x] Create spec/odooops-sh/tasks.md (337 lines)
- [ ] Validate with scripts/validate_spec_kit.py
- [ ] Pass existing 7 spec gates

### Core Schema (Week 2)
- [ ] Create migration 20260213_000100_odooops_control_plane_core.sql
- [ ] Define ops.projects table with indexes
- [ ] Define ops.workflows table with unique constraint
- [ ] Define ops.runs table with queue indexes
- [ ] Define ops.run_events table with timestamp index
- [ ] Define ops.run_artifacts table with unique constraint
- [ ] Define ops.run_logs table with level index
- [ ] Define ops.tools table with unique name
- [ ] Define ops.upgrade_advisories table with version pair unique
- [ ] Define ops.project_memberships table with RBAC
- [ ] Create RLS policies for all 9 tables
- [ ] Test migration on local Supabase
- [ ] Verify all tables created
- [ ] Generate DBML schema
- [ ] Generate Mermaid ERD
- [ ] Update prisma/schema.prisma with 9 models
- [ ] Test Prisma type generation
- [ ] Deploy to staging
- [ ] Deploy to production

### RPC Functions (Week 3)
- [ ] Create migration 20260213_000200_odooops_rpc_functions.sql
- [ ] Define ops.claim_next_run(p_worker_id) function
- [ ] Define ops.start_workflow_run(p_run_id, p_worker_id) function
- [ ] Define ops.complete_workflow_run(p_run_id, p_exit_code, p_error_message) function
- [ ] Define ops.append_run_log(p_run_id, p_level, p_message, p_metadata) function
- [ ] Define ops.add_run_artifact(p_run_id, p_artifact_key, p_s3_url, ...) function
- [ ] Define ops.list_queued_runs() function
- [ ] Test SELECT FOR UPDATE SKIP LOCKED concurrency
- [ ] Verify idempotency key enforcement
- [ ] Write concurrency test script
- [ ] Deploy to staging
- [ ] Run concurrency test on staging
- [ ] Deploy to production

## P1 Tasks (Should Have - Week 4-5)

### CI Integration (Week 4)
- [ ] Create .github/workflows/odooops-sh-spec-gates.yml
- [ ] Add validate-spec-kit job (4 files exist)
- [ ] Add validate-schema job (migration syntax, DBML, ERD)
- [ ] Add validate-prisma job (schema validation, TypeScript generation)
- [ ] Add validate-docs job (5 files, markdown links)
- [ ] Create scripts/validate_spec_kit_odooops.sh
- [ ] Test workflow on PR
- [ ] Integrate with existing spec gates

### Documentation (Week 5)
- [ ] Write docs/odooops-sh/ARCHITECTURE.md (5-layer architecture)
- [ ] Write docs/odooops-sh/DATA_BOUNDARIES.md (Odoo vs Supabase SoR split)
- [ ] Write docs/odooops-sh/RUN_LIFECYCLE.md (state machine documentation)
- [ ] Write docs/odooops-sh/CICD.md (workflow orchestration)
- [ ] Write docs/odooops-sh/SECURITY.md (RLS policies, SECURITY DEFINER functions)
- [ ] Validate markdown links
- [ ] Add to repository documentation index

## P2 Tasks (Nice to Have - Week 6)

### Integration Testing (Week 6)
- [ ] Update scripts/odooops/env_create.sh (insert into ops.runs)
- [ ] Update scripts/odooops/env_wait_ready.sh (query run status)
- [ ] Update scripts/odooops/env_destroy.sh (mark canceled)
- [ ] Write end-to-end test script
- [ ] Test full workflow: create → claim → start → complete
- [ ] Verify artifact storage
- [ ] Verify log streaming
- [ ] Test worker heartbeat
- [ ] Test retry logic for failed runs

## P3 Tasks (Future Enhancements)

### Console UI (Future)
- [ ] Create web/odooops-console/ Next.js app
- [ ] Build project dashboard page
- [ ] Build run history viewer
- [ ] Build log streaming UI
- [ ] Build artifact browser
- [ ] Implement Supabase Auth + RLS
- [ ] Deploy to Vercel

### Advanced Features (Future)
- [ ] Run cancellation support
- [ ] Worker heartbeat monitoring
- [ ] Automated retry logic
- [ ] Artifact expiry cleanup
- [ ] Upgrade advisory system
- [ ] Tool version pinning
