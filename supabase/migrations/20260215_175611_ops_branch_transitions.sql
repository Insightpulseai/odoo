-- Migration: Branch Transitions & Policies (Phase 2 - Branches Lane)
-- Creates schema for blue-green deployment workflow with policy enforcement

-- =====================================================
-- TABLE: ops.branch_transitions
-- Tracks promotion/rollback requests and their lifecycle
-- =====================================================
CREATE TABLE IF NOT EXISTS ops.branch_transitions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES ops.projects(id) ON DELETE CASCADE,
  branch_id UUID NOT NULL REFERENCES ops.branches(id) ON DELETE CASCADE,
  from_stage TEXT CHECK (from_stage IN ('dev', 'staging', 'production')),
  to_stage TEXT NOT NULL CHECK (to_stage IN ('dev', 'staging', 'production')),
  requested_by UUID NOT NULL,
  reason TEXT,
  status TEXT NOT NULL CHECK (status IN ('requested', 'approved', 'rejected', 'completed', 'failed')) DEFAULT 'requested',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  resolved_at TIMESTAMPTZ,
  resolved_build_id UUID REFERENCES ops.builds(id),
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Indexes for query optimization
CREATE INDEX IF NOT EXISTS idx_branch_transitions_project ON ops.branch_transitions(project_id);
CREATE INDEX IF NOT EXISTS idx_branch_transitions_branch ON ops.branch_transitions(branch_id);
CREATE INDEX IF NOT EXISTS idx_branch_transitions_status ON ops.branch_transitions(status);
CREATE INDEX IF NOT EXISTS idx_branch_transitions_created ON ops.branch_transitions(created_at DESC);

-- =====================================================
-- TABLE: ops.policies
-- Project-level policies for promotion gates and cleanup
-- =====================================================
CREATE TABLE IF NOT EXISTS ops.policies (
  project_id UUID PRIMARY KEY REFERENCES ops.projects(id) ON DELETE CASCADE,
  require_green_for_promotion BOOLEAN NOT NULL DEFAULT true,
  staging_ttl_days INTEGER NOT NULL DEFAULT 14,
  max_active_dev_branches INTEGER NOT NULL DEFAULT 10,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================================================
-- RLS POLICIES
-- Tenant isolation using ops.my_org_ids() pattern
-- =====================================================

-- Enable RLS
ALTER TABLE ops.branch_transitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.policies ENABLE ROW LEVEL SECURITY;

-- Branch Transitions RLS
CREATE POLICY "Users can view transitions in their orgs"
  ON ops.branch_transitions
  FOR SELECT
  USING (
    project_id IN (
      SELECT p.id FROM ops.projects p
      WHERE p.org_id IN (SELECT ops.my_org_ids())
    )
  );

CREATE POLICY "Users can create transitions in their orgs"
  ON ops.branch_transitions
  FOR INSERT
  WITH CHECK (
    project_id IN (
      SELECT p.id FROM ops.projects p
      WHERE p.org_id IN (SELECT ops.my_org_ids())
    )
  );

CREATE POLICY "Users can update transitions in their orgs"
  ON ops.branch_transitions
  FOR UPDATE
  USING (
    project_id IN (
      SELECT p.id FROM ops.projects p
      WHERE p.org_id IN (SELECT ops.my_org_ids())
    )
  );

-- Policies RLS
CREATE POLICY "Users can view policies in their orgs"
  ON ops.policies
  FOR SELECT
  USING (
    project_id IN (
      SELECT p.id FROM ops.projects p
      WHERE p.org_id IN (SELECT ops.my_org_ids())
    )
  );

CREATE POLICY "Users can manage policies in their orgs"
  ON ops.policies
  FOR ALL
  USING (
    project_id IN (
      SELECT p.id FROM ops.projects p
      WHERE p.org_id IN (SELECT ops.my_org_ids())
    )
  );

-- =====================================================
-- RPC: ops_list_branches_with_latest_build
-- Returns branches with their latest build and status
-- =====================================================
CREATE OR REPLACE FUNCTION ops_list_branches_with_latest_build(project_uuid UUID)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result JSONB;
BEGIN
  -- Verify project access
  IF NOT EXISTS (
    SELECT 1 FROM ops.projects p
    WHERE p.id = project_uuid
      AND p.org_id IN (SELECT ops.my_org_ids())
  ) THEN
    RETURN jsonb_build_object('error', 'Project not found or access denied');
  END IF;

  -- Build result with latest build per branch
  SELECT jsonb_build_object(
    'project_id', project_uuid,
    'branches', jsonb_agg(
      jsonb_build_object(
        'branch_id', b.id,
        'name', b.name,
        'stage', b.stage,
        'latest_build', CASE
          WHEN lb.id IS NOT NULL THEN jsonb_build_object(
            'build_id', lb.id,
            'build_number', lb.build_number,
            'status', lb.status,
            'started_at', lb.started_at,
            'completed_at', lb.completed_at,
            'commit_sha', lb.commit_sha
          )
          ELSE NULL
        END
      ) ORDER BY b.stage DESC, b.name
    )
  ) INTO result
  FROM ops.branches b
  LEFT JOIN LATERAL (
    SELECT id, build_number, status, started_at, completed_at, commit_sha
    FROM ops.builds
    WHERE branch_id = b.id
    ORDER BY build_number DESC
    LIMIT 1
  ) lb ON true
  WHERE b.project_id = project_uuid;

  RETURN result;
END;
$$;

-- =====================================================
-- RPC: ops_request_promotion
-- Create a promotion request with policy validation
-- =====================================================
CREATE OR REPLACE FUNCTION ops_request_promotion(
  project_uuid UUID,
  branch_uuid UUID,
  target_stage TEXT,
  reason TEXT DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  current_stage TEXT;
  latest_build_status TEXT;
  policy_record RECORD;
  transition_id UUID;
BEGIN
  -- Verify project access
  IF NOT EXISTS (
    SELECT 1 FROM ops.projects p
    WHERE p.id = project_uuid
      AND p.org_id IN (SELECT ops.my_org_ids())
  ) THEN
    RETURN jsonb_build_object('error', 'Project not found or access denied');
  END IF;

  -- Verify branch exists and get current stage
  SELECT stage INTO current_stage
  FROM ops.branches
  WHERE id = branch_uuid AND project_id = project_uuid;

  IF current_stage IS NULL THEN
    RETURN jsonb_build_object('error', 'Branch not found');
  END IF;

  -- Validate stage transition
  IF target_stage NOT IN ('dev', 'staging', 'production') THEN
    RETURN jsonb_build_object('error', 'Invalid target stage');
  END IF;

  IF current_stage = target_stage THEN
    RETURN jsonb_build_object('error', 'Branch already in target stage');
  END IF;

  -- Get project policies
  SELECT * INTO policy_record
  FROM ops.policies
  WHERE project_id = project_uuid;

  -- If no policy exists, create default
  IF policy_record IS NULL THEN
    INSERT INTO ops.policies (project_id)
    VALUES (project_uuid)
    RETURNING * INTO policy_record;
  END IF;

  -- Check latest build status if policy requires green builds
  IF policy_record.require_green_for_promotion AND target_stage IN ('staging', 'production') THEN
    SELECT status INTO latest_build_status
    FROM ops.builds
    WHERE branch_id = branch_uuid
    ORDER BY build_number DESC
    LIMIT 1;

    IF latest_build_status IS NULL THEN
      RETURN jsonb_build_object('error', 'No builds found for branch');
    END IF;

    IF latest_build_status != 'success' THEN
      RETURN jsonb_build_object(
        'error', 'Latest build status is not success',
        'build_status', latest_build_status
      );
    END IF;
  END IF;

  -- Create transition request
  INSERT INTO ops.branch_transitions (
    project_id,
    branch_id,
    from_stage,
    to_stage,
    requested_by,
    reason,
    status
  ) VALUES (
    project_uuid,
    branch_uuid,
    current_stage,
    target_stage,
    auth.uid(),
    reason,
    'requested'
  )
  RETURNING id INTO transition_id;

  RETURN jsonb_build_object(
    'success', true,
    'transition_id', transition_id,
    'from_stage', current_stage,
    'to_stage', target_stage
  );
END;
$$;

-- =====================================================
-- RPC: ops_request_rebuild
-- Create a rebuild request for a branch
-- =====================================================
CREATE OR REPLACE FUNCTION ops_request_rebuild(
  project_uuid UUID,
  branch_uuid UUID
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  branch_stage TEXT;
  latest_build_id UUID;
  latest_build_number INTEGER;
  transition_id UUID;
BEGIN
  -- Verify project access
  IF NOT EXISTS (
    SELECT 1 FROM ops.projects p
    WHERE p.id = project_uuid
      AND p.org_id IN (SELECT ops.my_org_ids())
  ) THEN
    RETURN jsonb_build_object('error', 'Project not found or access denied');
  END IF;

  -- Verify branch exists and get stage
  SELECT stage INTO branch_stage
  FROM ops.branches
  WHERE id = branch_uuid AND project_id = project_uuid;

  IF branch_stage IS NULL THEN
    RETURN jsonb_build_object('error', 'Branch not found');
  END IF;

  -- Get latest build info
  SELECT id, build_number INTO latest_build_id, latest_build_number
  FROM ops.builds
  WHERE branch_id = branch_uuid
  ORDER BY build_number DESC
  LIMIT 1;

  -- Create rebuild transition (same stage to same stage)
  INSERT INTO ops.branch_transitions (
    project_id,
    branch_id,
    from_stage,
    to_stage,
    requested_by,
    reason,
    status,
    metadata
  ) VALUES (
    project_uuid,
    branch_uuid,
    branch_stage,
    branch_stage,
    auth.uid(),
    'Rebuild request',
    'requested',
    jsonb_build_object(
      'rebuild', true,
      'previous_build_id', latest_build_id,
      'previous_build_number', latest_build_number
    )
  )
  RETURNING id INTO transition_id;

  RETURN jsonb_build_object(
    'success', true,
    'transition_id', transition_id,
    'rebuild', true,
    'stage', branch_stage
  );
END;
$$;

-- =====================================================
-- RPC: ops_request_rollback
-- Create a rollback request for production branch
-- =====================================================
CREATE OR REPLACE FUNCTION ops_request_rollback(
  project_uuid UUID,
  production_branch_uuid UUID,
  build_uuid UUID,
  reason TEXT DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  branch_stage TEXT;
  build_exists BOOLEAN;
  transition_id UUID;
BEGIN
  -- Verify project access
  IF NOT EXISTS (
    SELECT 1 FROM ops.projects p
    WHERE p.id = project_uuid
      AND p.org_id IN (SELECT ops.my_org_ids())
  ) THEN
    RETURN jsonb_build_object('error', 'Project not found or access denied');
  END IF;

  -- Verify branch is production
  SELECT stage INTO branch_stage
  FROM ops.branches
  WHERE id = production_branch_uuid AND project_id = project_uuid;

  IF branch_stage IS NULL THEN
    RETURN jsonb_build_object('error', 'Branch not found');
  END IF;

  IF branch_stage != 'production' THEN
    RETURN jsonb_build_object('error', 'Rollback only allowed for production branches');
  END IF;

  -- Verify build exists for this branch
  SELECT EXISTS (
    SELECT 1 FROM ops.builds
    WHERE id = build_uuid
      AND branch_id = production_branch_uuid
      AND status = 'success'
  ) INTO build_exists;

  IF NOT build_exists THEN
    RETURN jsonb_build_object('error', 'Build not found or not successful');
  END IF;

  -- Create rollback transition
  INSERT INTO ops.branch_transitions (
    project_id,
    branch_id,
    from_stage,
    to_stage,
    requested_by,
    reason,
    status,
    resolved_build_id,
    metadata
  ) VALUES (
    project_uuid,
    production_branch_uuid,
    'production',
    'production',
    auth.uid(),
    COALESCE(reason, 'Rollback request'),
    'requested',
    build_uuid,
    jsonb_build_object('rollback', true)
  )
  RETURNING id INTO transition_id;

  RETURN jsonb_build_object(
    'success', true,
    'transition_id', transition_id,
    'rollback', true,
    'target_build_id', build_uuid
  );
END;
$$;

-- =====================================================
-- GRANTS
-- Ensure authenticated users can execute RPCs
-- =====================================================
GRANT EXECUTE ON FUNCTION ops_list_branches_with_latest_build(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION ops_request_promotion(UUID, UUID, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION ops_request_rebuild(UUID, UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION ops_request_rollback(UUID, UUID, UUID, TEXT) TO authenticated;
