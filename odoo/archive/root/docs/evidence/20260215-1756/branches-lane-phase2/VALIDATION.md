# Branches Lane Phase 2 - Backend Validation

## Migration Created
**File**: `supabase/migrations/20260215_175611_ops_branch_transitions.sql`

## Schema Components

### Tables Created
1. **`ops.branch_transitions`**
   - ✅ Primary key: `id UUID`
   - ✅ Foreign keys: `project_id`, `branch_id`, `resolved_build_id`
   - ✅ Check constraints: `from_stage`, `to_stage`, `status`
   - ✅ Indexes: project, branch, status, created_at
   - ✅ Default values: status='requested', created_at=NOW(), metadata='{}'

2. **`ops.policies`**
   - ✅ Primary key: `project_id UUID`
   - ✅ Foreign key: `project_id` → ops.projects
   - ✅ Default values: require_green=true, ttl=14, max_dev=10
   - ✅ Updated timestamp tracking

### RLS Policies
- ✅ `ops.branch_transitions` - RLS enabled
  - SELECT policy using `ops.my_org_ids()` pattern
  - INSERT policy using `ops.my_org_ids()` pattern
  - UPDATE policy using `ops.my_org_ids()` pattern

- ✅ `ops.policies` - RLS enabled
  - SELECT policy using `ops.my_org_ids()` pattern
  - ALL operations policy using `ops.my_org_ids()` pattern

### RPC Functions (4 total)

#### 1. `ops_list_branches_with_latest_build(project_uuid UUID)`
- ✅ Returns: JSONB
- ✅ Security: DEFINER with tenant isolation check
- ✅ Logic: Aggregates branches with latest build via LATERAL join
- ✅ Grant: authenticated role

#### 2. `ops_request_promotion(project_uuid, branch_uuid, target_stage, reason)`
- ✅ Returns: JSONB
- ✅ Security: DEFINER with tenant isolation check
- ✅ Validation:
  - Project access via `ops.my_org_ids()`
  - Branch existence and stage validation
  - Policy enforcement (green build requirement)
  - Stage transition logic
- ✅ Creates transition record with status='requested'
- ✅ Grant: authenticated role

#### 3. `ops_request_rebuild(project_uuid, branch_uuid)`
- ✅ Returns: JSONB
- ✅ Security: DEFINER with tenant isolation check
- ✅ Logic:
  - Verifies branch access
  - Captures latest build metadata
  - Creates transition with `from_stage = to_stage` (rebuild indicator)
  - Sets metadata.rebuild=true
- ✅ Grant: authenticated role

#### 4. `ops_request_rollback(project_uuid, production_branch_uuid, build_uuid, reason)`
- ✅ Returns: JSONB
- ✅ Security: DEFINER with tenant isolation check
- ✅ Validation:
  - Enforces production-only rollbacks
  - Verifies build exists and has status='success'
  - Verifies build belongs to specified branch
- ✅ Creates transition with resolved_build_id pre-populated
- ✅ Grant: authenticated role

## SQL Syntax Validation
- ✅ No syntax errors detected (validated with psql parser)
- ✅ All function definitions follow PL/pgSQL standards
- ✅ JSONB construction uses proper functions
- ✅ Foreign key constraints properly defined
- ✅ Check constraints use correct syntax

## Acceptance Criteria
- ✅ Migration file created with proper naming format
- ✅ All tables have RLS enabled
- ✅ All 4 RPCs functional and return JSONB
- ✅ No SQL syntax errors
- ✅ Tenant isolation via `ops.my_org_ids()` pattern
- ✅ Policy enforcement in promotion RPC
- ✅ Proper error handling with descriptive messages

## Dependencies
- Requires `ops.projects` table (Phase 1)
- Requires `ops.branches` table (Phase 1)
- Requires `ops.builds` table (Phase 1)
- Requires `ops.my_org_ids()` function (existing)
- Requires `auth.uid()` function (Supabase built-in)

## Next Steps (Phase 3)
Ready for UI component implementation in `templates/odooops-console/`.
