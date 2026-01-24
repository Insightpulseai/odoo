# Lakehouse Control Room - Task Breakdown

## Phase 1: Foundation

### 1.1 Contract & Schema

- [x] **LH-001**: Create OpenAPI contract for executor communication
  - Lane: DEV
  - Priority: P1
  - Acceptance: Valid OpenAPI 3.0 spec with all endpoints defined

- [x] **LH-002**: Create Supabase ops schema migration
  - Lane: DEV
  - Priority: P1
  - Acceptance: Migration applies cleanly, all tables/functions created

- [x] **LH-003**: Create spec bundle (constitution, prd, plan, tasks)
  - Lane: DEV
  - Priority: P1
  - Acceptance: All 4 files present and non-empty

- [ ] **LH-004**: Create PR gate workflow
  - Lane: DEV
  - Priority: P1
  - Acceptance: Workflow runs on PR, validates contract + migrations

- [ ] **LH-005**: Create OpenAPI validation script
  - Lane: DEV
  - Priority: P1
  - Acceptance: Script validates contract structure

- [ ] **LH-006**: Create Supabase migrations lint script
  - Lane: DEV
  - Priority: P2
  - Acceptance: Script validates migration naming conventions

### 1.2 Backlog & Routing

- [ ] **LH-007**: Create canonical backlog YAML
  - Lane: DEV
  - Priority: P2
  - Acceptance: Backlog defines all epics and features

- [ ] **LH-008**: Create backlog export script
  - Lane: DEV
  - Priority: P2
  - Acceptance: YAML → JSON export with deterministic output

- [ ] **LH-009**: Create routing matrix lint script
  - Lane: DEV
  - Priority: P2
  - Acceptance: Validates routing rules structure

- [ ] **LH-010**: Create routing matrix export script
  - Lane: DEV
  - Priority: P2
  - Acceptance: DB → JSON export for review

- [ ] **LH-011**: Create caps report generator
  - Lane: DEV
  - Priority: P2
  - Acceptance: Generates MD + JSON caps report

### 1.3 Export Validation

- [ ] **LH-012**: Create export validation script
  - Lane: DEV
  - Priority: P2
  - Acceptance: Validates export schema and content

- [ ] **LH-013**: Create canonicalize + diff script
  - Lane: DEV
  - Priority: P2
  - Acceptance: Ignores timestamps, generates stable diff

- [ ] **LH-014**: Create PR summary bundle script
  - Lane: DEV
  - Priority: P3
  - Acceptance: Generates PR comment with diff summary

## Phase 2: Executor Implementation

### 2.1 Core Executor

- [ ] **LH-020**: Implement claim_run RPC
  - Lane: DEV
  - Priority: P1
  - Acceptance: Atomic claim with SKIP LOCKED

- [ ] **LH-021**: Implement heartbeat mechanism
  - Lane: DEV
  - Priority: P1
  - Acceptance: Heartbeat updates, stale detection works

- [ ] **LH-022**: Implement finalize_run RPC
  - Lane: DEV
  - Priority: P1
  - Acceptance: Status transitions correctly, events logged

- [ ] **LH-023**: Create Edge Function executor
  - Lane: DEV
  - Priority: P2
  - Acceptance: Executor claims, runs tasks, reports back

- [ ] **LH-024**: Implement artifact upload
  - Lane: DEV
  - Priority: P2
  - Acceptance: Artifacts stored with SHA-256

### 2.2 Specific Executors

- [ ] **LH-030**: Spark executor wrapper
  - Lane: DEV
  - Priority: P2
  - Acceptance: Can submit Spark jobs, capture logs

- [ ] **LH-031**: Trino executor wrapper
  - Lane: DEV
  - Priority: P2
  - Acceptance: Can run SQL, store results

- [ ] **LH-032**: dbt executor wrapper
  - Lane: DEV
  - Priority: P2
  - Acceptance: Can run dbt, capture manifest

## Phase 3: Control Room UI

### 3.1 Core Pages

- [ ] **LH-040**: Runs list page
  - Lane: DEV
  - Priority: P2
  - Acceptance: Shows all runs with filtering

- [ ] **LH-041**: Run detail page
  - Lane: DEV
  - Priority: P2
  - Acceptance: Shows events, artifacts, status

- [ ] **LH-042**: Executor registry page
  - Lane: DEV
  - Priority: P3
  - Acceptance: CRUD executors, health status

### 3.2 Job Management

- [ ] **LH-050**: Job templates page
  - Lane: DEV
  - Priority: P3
  - Acceptance: Create/edit job templates

- [ ] **LH-051**: Schedule configuration
  - Lane: DEV
  - Priority: P3
  - Acceptance: Cron scheduling UI

## Status Legend

- Lane: DEV (Development), OPS (Operations), SEC (Security)
- Priority: P1 (Critical), P2 (High), P3 (Medium), P4 (Low)
- Status: `[ ]` Pending, `[x]` Complete, `[-]` Blocked
