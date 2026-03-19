# OdooOps Sh Product Requirements Document

## Problem Statement

Self-hosted Odoo deployments lack the developer experience of Odoo.sh SaaS:
- No centralized project management
- No automated workflow execution tracking
- No artifact storage for builds
- No upgrade advisory system

## Goals

1. **Developer Experience Parity**: Match Odoo.sh UX for self-hosted environments
2. **Queue-Based Execution**: Safe worker claim pattern with concurrency control
3. **Complete Audit Trail**: Every run state change logged immutably
4. **Artifact Management**: Build outputs stored and versioned

## User Stories

### Developer
- Create project with slug and workspace key
- Define workflows (build, test, deploy, backup)
- View run history and logs
- Download build artifacts

### DevOps
- Monitor workflow queue
- Restart failed runs
- Configure tool versions
- Receive upgrade advisories

### Platform Team
- Manage project memberships
- Configure RLS policies
- Monitor system health
- Generate compliance reports

## Features

### 1. ops.projects - Workspace Containers
- Unique workspace_key (e.g., ipai_workspace)
- Human-readable slug
- Odoo version tracking
- Status (active, archived)

### 2. ops.workflows - Workflow Definitions
- Type: build | test | deploy | backup | upgrade
- Per-project configuration (jsonb)
- Enable/disable toggle
- Git ref and commit tracking

### 3. ops.runs - Main Execution Queue
- Auto-incrementing run_number per project
- Status state machine (queued → claimed → running → succeeded|failed)
- Worker claim fields (claimed_by, claimed_at)
- Duration tracking (started_at, finished_at)
- Idempotency key

### 4. ops.run_events - Append-Only Event Log
- Event types: state_change, error, warning, info
- Timestamp precision (microseconds)
- JSON payload for extensibility

### 5. ops.run_artifacts - Build Output Metadata
- S3-style artifact keys
- Checksum (SHA-256)
- Content type and size
- Expiry date for cleanup

### 6. ops.run_logs - Structured Log Lines
- Log levels: debug | info | warn | error
- Message and metadata (jsonb)
- Full-text search support

### 7. ops.tools - Docker Image Registry
- Tool name and version
- Docker image reference
- Configuration (jsonb)

### 8. ops.upgrade_advisories - Breaking Change Warnings
- From/to version pairs
- Breaking change descriptions
- Migration guides
- Severity levels

### 9. ops.project_memberships - User Access Control
- Roles: owner | admin | developer | viewer
- RLS enforcement

## Run Lifecycle

```
queued → claimed → running → succeeded
                         ↓
                      failed
```

**State Transitions**:
- **queued**: Created, waiting for worker
- **claimed**: Worker called ops.claim_next_run()
- **running**: Worker called ops.start_workflow_run()
- **succeeded**: Exit code 0, artifacts uploaded
- **failed**: Non-zero exit code or error
- **canceled**: Manual stop (future)

## Definition of Done

- All 9 tables created with RLS policies
- ops.claim_next_run() function working for worker queue
- Spec Kit bundle passes all 7 existing spec gates
- No breaking changes to existing agent run tracking
- ERD diagram accurate and comprehensive
- Prisma schema generates TypeScript types correctly
- CI workflow validates Spec Kit structure on every PR
- Integration with scripts/odooops/*.sh verified
