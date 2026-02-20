-- Odoo.sh Platform Tables Migration
-- Creates tables for CI/CD, builds, and deployment tracking

-- ============================================================================
-- ops.builds — Build tracking for CI/CD pipeline
-- ============================================================================

CREATE TABLE IF NOT EXISTS ops.builds (
    build_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES ops.projects(id) ON DELETE CASCADE,

    -- Git metadata
    git_sha TEXT NOT NULL CHECK (git_sha ~ '^[a-f0-9]{40}$'), -- Full 40-char SHA
    branch_name TEXT NOT NULL,
    pr_number INTEGER, -- NULL for non-PR builds

    -- Build tracking
    status TEXT NOT NULL DEFAULT 'building' CHECK (status IN (
        'building',
        'testing',
        'success',
        'failed',
        'tests_failed',
        'deploy_failed'
    )),

    -- Deployment artifacts
    docker_image_sha256 TEXT, -- Docker image digest
    deployment_url TEXT, -- Where this build was deployed

    -- Test results
    test_results JSONB DEFAULT '{}'::jsonb, -- { passed: N, failed: N, skipped: N, coverage: N }

    -- Timing
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb, -- Build logs path, git event type, etc.

    UNIQUE (project_id, git_sha)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_builds_project_branch ON ops.builds(project_id, branch_name);
CREATE INDEX IF NOT EXISTS idx_builds_status ON ops.builds(status) WHERE status IN ('building', 'testing');
CREATE INDEX IF NOT EXISTS idx_builds_pr ON ops.builds(pr_number) WHERE pr_number IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_builds_created ON ops.builds(created_at DESC);

-- ============================================================================
-- ops.deployments — Deployment tracking and history
-- ============================================================================

CREATE TABLE IF NOT EXISTS ops.deployments (
    deployment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES ops.projects(id) ON DELETE CASCADE,
    environment_id UUID NOT NULL REFERENCES ops.environments(id) ON DELETE CASCADE,
    build_id UUID REFERENCES ops.builds(build_id) ON DELETE SET NULL,

    -- Deployment metadata
    git_sha TEXT NOT NULL,
    deployment_type TEXT NOT NULL CHECK (deployment_type IN (
        'automatic', -- GitHub webhook
        'manual', -- User-triggered
        'promotion', -- Staging → Production
        'rollback' -- Revert to previous
    )),

    -- Status tracking
    status TEXT NOT NULL DEFAULT 'deploying' CHECK (status IN (
        'deploying',
        'smoke_testing',
        'active',
        'failed',
        'rolled_back'
    )),

    -- Deployment target
    deployment_url TEXT NOT NULL,
    deployment_platform TEXT NOT NULL CHECK (deployment_platform IN (
        'vercel',
        'digitalocean_app_platform',
        'docker_compose',
        'kubernetes'
    )),

    -- Health checks
    health_check_passed BOOLEAN,
    health_check_results JSONB,

    -- Timing
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deployed_at TIMESTAMPTZ, -- When deployment became active

    -- Previous deployment (for rollback)
    previous_deployment_id UUID REFERENCES ops.deployments(deployment_id),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb, -- Platform-specific config, smoke test logs, etc.

    UNIQUE (environment_id, git_sha)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_deployments_environment ON ops.deployments(environment_id, status);
CREATE INDEX IF NOT EXISTS idx_deployments_project ON ops.deployments(project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_deployments_active ON ops.deployments(environment_id)
    WHERE status = 'active';

-- ============================================================================
-- ops.build_logs — Real-time build log streaming
-- ============================================================================

CREATE TABLE IF NOT EXISTS ops.build_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    build_id UUID NOT NULL REFERENCES ops.builds(build_id) ON DELETE CASCADE,

    -- Log entry
    step_name TEXT NOT NULL, -- e.g., 'git_clone', 'install_deps', 'run_tests'
    severity TEXT NOT NULL CHECK (severity IN ('debug', 'info', 'warning', 'error')),
    message TEXT NOT NULL,

    -- Timing
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb -- Stack traces, exit codes, etc.
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_build_logs_build ON ops.build_logs(build_id, created_at);
CREATE INDEX IF NOT EXISTS idx_build_logs_severity ON ops.build_logs(build_id, severity)
    WHERE severity IN ('error', 'warning');

-- ============================================================================
-- RLS Policies
-- ============================================================================

-- Enable RLS
ALTER TABLE ops.builds ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.deployments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.build_logs ENABLE ROW LEVEL SECURITY;

-- Service role has full access
CREATE POLICY "Service role full access to builds"
    ON ops.builds
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role full access to deployments"
    ON ops.deployments
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role full access to build logs"
    ON ops.build_logs
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Authenticated users can read builds/deployments for their projects
CREATE POLICY "Users can read builds for their projects"
    ON ops.builds
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM ops.project_members
            WHERE project_members.project_id = builds.project_id
              AND project_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can read deployments for their projects"
    ON ops.deployments
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM ops.project_members
            WHERE project_members.project_id = deployments.project_id
              AND project_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can read build logs for their builds"
    ON ops.build_logs
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM ops.builds
            JOIN ops.project_members ON builds.project_id = project_members.project_id
            WHERE builds.build_id = build_logs.build_id
              AND project_members.user_id = auth.uid()
        )
    );

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Generate build ID with timestamp prefix
CREATE OR REPLACE FUNCTION ops.gen_build_id()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN 'build_' || TO_CHAR(NOW(), 'YYYYMMDD_HH24MISS') || '_' || SUBSTR(gen_random_uuid()::text, 1, 8);
END;
$$;

-- Get latest successful build for branch
CREATE OR REPLACE FUNCTION ops.get_latest_build(p_project_id UUID, p_branch_name TEXT)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_build_id UUID;
BEGIN
    SELECT build_id INTO v_build_id
    FROM ops.builds
    WHERE project_id = p_project_id
      AND branch_name = p_branch_name
      AND status = 'success'
    ORDER BY created_at DESC
    LIMIT 1;

    RETURN v_build_id;
END;
$$;

-- Get active deployment for environment
CREATE OR REPLACE FUNCTION ops.get_active_deployment(p_environment_id UUID)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_deployment_id UUID;
BEGIN
    SELECT deployment_id INTO v_deployment_id
    FROM ops.deployments
    WHERE environment_id = p_environment_id
      AND status = 'active'
    ORDER BY deployed_at DESC
    LIMIT 1;

    RETURN v_deployment_id;
END;
$$;

-- ============================================================================
-- Seed Data for Testing
-- ============================================================================

-- Insert test project (if not exists)
INSERT INTO ops.projects (id, name, github_repo_url, created_at)
VALUES (
    'c0000000-0000-0000-0000-000000000001'::uuid,
    'odoo-ce',
    'https://github.com/Insightpulseai/odoo',
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Insert test environments
INSERT INTO ops.environments (id, project_id, name, type, status, metadata)
VALUES
    (
        'd0000000-0000-0000-0000-000000000001'::uuid,
        'c0000000-0000-0000-0000-000000000001'::uuid,
        'production',
        'production',
        'active',
        '{"auto_cleanup_days": null}'::jsonb
    ),
    (
        'd0000000-0000-0000-0000-000000000002'::uuid,
        'c0000000-0000-0000-0000-000000000001'::uuid,
        'staging',
        'staging',
        'active',
        '{"auto_cleanup_days": 14}'::jsonb
    ),
    (
        'd0000000-0000-0000-0000-000000000003'::uuid,
        'c0000000-0000-0000-0000-000000000001'::uuid,
        'dev-feat-multi-tenant',
        'development',
        'active',
        '{"auto_cleanup_days": 7, "branch_name": "feat/multi-tenant-saas"}'::jsonb
    )
ON CONFLICT (id) DO NOTHING;

-- Insert test build
INSERT INTO ops.builds (
    build_id,
    project_id,
    git_sha,
    branch_name,
    status,
    docker_image_sha256,
    deployment_url,
    test_results,
    created_at,
    completed_at,
    metadata
)
VALUES (
    'b0000000-0000-0000-0000-000000000001'::uuid,
    'c0000000-0000-0000-0000-000000000001'::uuid,
    '52b63b1a2f8e3d4c5b6a7f8e9d0c1b2a3f4e5d6c',
    'feat/multi-tenant-saas',
    'success',
    'sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
    'https://dev-feat-multi-tenant.app.insightpulseai.com',
    '{"passed": 42, "failed": 0, "skipped": 3, "coverage": 87.5}'::jsonb,
    NOW() - INTERVAL '2 hours',
    NOW() - INTERVAL '1 hour 50 minutes',
    '{"git_event_type": "push", "build_duration_seconds": 600}'::jsonb
)
ON CONFLICT (build_id) DO NOTHING;

-- Insert test deployment
INSERT INTO ops.deployments (
    deployment_id,
    project_id,
    environment_id,
    build_id,
    git_sha,
    deployment_type,
    status,
    deployment_url,
    deployment_platform,
    health_check_passed,
    created_at,
    deployed_at,
    metadata
)
VALUES (
    'e0000000-0000-0000-0000-000000000001'::uuid,
    'c0000000-0000-0000-0000-000000000001'::uuid,
    'd0000000-0000-0000-0000-000000000003'::uuid,
    'b0000000-0000-0000-0000-000000000001'::uuid,
    '52b63b1a2f8e3d4c5b6a7f8e9d0c1b2a3f4e5d6c',
    'automatic',
    'active',
    'https://dev-feat-multi-tenant.app.insightpulseai.com',
    'vercel',
    true,
    NOW() - INTERVAL '1 hour 50 minutes',
    NOW() - INTERVAL '1 hour 45 minutes',
    '{"vercel_deployment_id": "dpl_test123", "smoke_tests_passed": true}'::jsonb
)
ON CONFLICT (deployment_id) DO NOTHING;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ops.builds TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ops.deployments TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ops.build_logs TO service_role;
GRANT SELECT ON ops.builds TO authenticated;
GRANT SELECT ON ops.deployments TO authenticated;
GRANT SELECT ON ops.build_logs TO authenticated;
