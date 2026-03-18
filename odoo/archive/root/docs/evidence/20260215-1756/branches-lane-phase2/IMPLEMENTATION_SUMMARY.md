# Branches Lane Phase 2 - Backend Implementation Complete

## Deliverable
**Migration File**: `supabase/migrations/20260215_175611_ops_branch_transitions.sql`

## Implementation Summary

### Database Schema

#### 1. `ops.branch_transitions` Table
Complete lifecycle tracking for promotion, rebuild, and rollback requests.

**Columns**:
- `id` - UUID primary key
- `project_id` - Foreign key to ops.projects (CASCADE delete)
- `branch_id` - Foreign key to ops.branches (CASCADE delete)
- `from_stage` - Source stage (dev/staging/production)
- `to_stage` - Target stage (dev/staging/production)
- `requested_by` - User UUID who initiated transition
- `reason` - Optional justification text
- `status` - Workflow state (requested/approved/rejected/completed/failed)
- `created_at` - Request timestamp
- `resolved_at` - Completion timestamp
- `resolved_build_id` - Foreign key to ops.builds (for rollback target)
- `metadata` - Flexible JSONB for additional context

**Indexes**:
- `idx_branch_transitions_project` - Query by project
- `idx_branch_transitions_branch` - Query by branch
- `idx_branch_transitions_status` - Filter active transitions
- `idx_branch_transitions_created` - Chronological ordering

#### 2. `ops.policies` Table
Project-level governance and automation policies.

**Columns**:
- `project_id` - Primary key, foreign key to ops.projects
- `require_green_for_promotion` - Enforce passing builds (default: true)
- `staging_ttl_days` - Auto-cleanup threshold (default: 14)
- `max_active_dev_branches` - Concurrent dev limit (default: 10)
- `updated_at` - Last policy modification

### Row-Level Security

**Tenant Isolation Pattern**: All policies use `ops.my_org_ids()` for multi-tenant security.

**branch_transitions**:
- SELECT: View transitions in your organizations
- INSERT: Create transitions in your organizations
- UPDATE: Modify transitions in your organizations

**policies**:
- SELECT: View policies in your organizations
- ALL: Manage policies in your organizations

### RPC Functions (4)

#### 1. `ops_list_branches_with_latest_build(project_uuid)`
**Purpose**: Fetch all branches with their most recent build status.

**Returns**:
```json
{
  "project_id": "uuid",
  "branches": [
    {
      "branch_id": "uuid",
      "name": "main",
      "stage": "production",
      "latest_build": {
        "build_id": "uuid",
        "build_number": 42,
        "status": "success",
        "started_at": "timestamp",
        "completed_at": "timestamp",
        "commit_sha": "abc123"
      }
    }
  ]
}
```

**Security**: Validates project access via `ops.my_org_ids()`.

#### 2. `ops_request_promotion(project_uuid, branch_uuid, target_stage, reason?)`
**Purpose**: Request branch promotion with policy enforcement.

**Validation**:
- Project access verification
- Branch existence and stage validation
- Target stage validation (dev/staging/production)
- Policy enforcement (green build requirement for staging/production)
- Latest build status check

**Returns**:
```json
{
  "success": true,
  "transition_id": "uuid",
  "from_stage": "staging",
  "to_stage": "production"
}
```

**Error Example**:
```json
{
  "error": "Latest build status is not success",
  "build_status": "failed"
}
```

#### 3. `ops_request_rebuild(project_uuid, branch_uuid)`
**Purpose**: Request rebuild of current branch.

**Behavior**:
- Creates transition with `from_stage = to_stage` (rebuild indicator)
- Captures previous build metadata in `metadata.rebuild=true`
- No policy enforcement (rebuilds allowed at any time)

**Returns**:
```json
{
  "success": true,
  "transition_id": "uuid",
  "rebuild": true,
  "stage": "staging"
}
```

#### 4. `ops_request_rollback(project_uuid, production_branch_uuid, build_uuid, reason?)`
**Purpose**: Request rollback to a previous successful build.

**Validation**:
- Production-only enforcement (rejects non-production branches)
- Build existence and success status check
- Build-branch ownership verification

**Returns**:
```json
{
  "success": true,
  "transition_id": "uuid",
  "rollback": true,
  "target_build_id": "uuid"
}
```

**Error Example**:
```json
{
  "error": "Rollback only allowed for production branches"
}
```

## Quality Verification

### Acceptance Criteria ✅
- [x] Migration file created with proper naming (`20260215_175611_ops_branch_transitions.sql`)
- [x] All tables have RLS enabled (both `branch_transitions` and `policies`)
- [x] All 4 RPCs functional and return JSONB
- [x] No SQL syntax errors (validated with psql parser)
- [x] Tenant isolation using `ops.my_org_ids()` pattern
- [x] Policy enforcement in promotion RPC
- [x] Proper error handling with descriptive messages

### SQL Quality
- ✅ IF NOT EXISTS guards for idempotent migrations
- ✅ Proper CASCADE delete semantics
- ✅ CHECK constraints for enum-like columns
- ✅ Comprehensive indexing strategy
- ✅ SECURITY DEFINER with proper access checks
- ✅ LATERAL joins for efficient latest-build queries
- ✅ JSONB aggregation for complex result structures

### Security Hardening
- ✅ All RPCs validate tenant isolation first
- ✅ RLS policies prevent cross-tenant data leaks
- ✅ Foreign key constraints ensure referential integrity
- ✅ Status and stage enums prevent invalid states
- ✅ Build verification before rollback approval

## Dependencies Met
- `ops.projects` table ✅
- `ops.branches` table ✅
- `ops.builds` table ✅
- `ops.my_org_ids()` function ✅
- `auth.uid()` function ✅ (Supabase built-in)

## Migration Sequence
Previous: `20260215_000001_ops_add_supabase_project_ref.sql`
Current: `20260215_175611_ops_branch_transitions.sql`
Next: Phase 3 UI components

## Ready for Phase 3
Backend schema and RPCs complete. UI can now consume:
- `ops_list_branches_with_latest_build()` for branch listing
- `ops_request_promotion()` for lane transitions
- `ops_request_rebuild()` for refresh actions
- `ops_request_rollback()` for production rollbacks

All backend logic tested for SQL correctness and semantic validity.
