-- Migration: OdooOps Control Plane Schema - Backups, Restores, Approvals, Policies
-- Purpose: Add backup management, restore workflows, approval gates, and policies

-- Backups table
CREATE TABLE IF NOT EXISTS ops.backups (
    backup_id TEXT PRIMARY KEY DEFAULT 'bak-' || gen_random_uuid()::text,
    project_id TEXT NOT NULL REFERENCES ops.projects(project_id) ON DELETE CASCADE,
    env_id TEXT NOT NULL REFERENCES ops.environments(env_id) ON DELETE CASCADE,
    backup_type TEXT NOT NULL CHECK (backup_type IN ('daily', 'weekly', 'monthly', 'manual')),
    db_dump_path TEXT NOT NULL,
    filestore_path TEXT,
    logs_path TEXT,
    size_bytes BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

COMMENT ON TABLE ops.backups IS 'Backup metadata with retention tracking';
COMMENT ON COLUMN ops.backups.backup_type IS 'Backup type: daily (7), weekly (4), monthly (3), manual';
COMMENT ON COLUMN ops.backups.db_dump_path IS 'Storage path for database dump';
COMMENT ON COLUMN ops.backups.filestore_path IS 'Storage path for filestore tar.gz';
COMMENT ON COLUMN ops.backups.expires_at IS 'Expiration date for retention enforcement';

CREATE INDEX idx_backups_project_env ON ops.backups(project_id, env_id, created_at DESC);
CREATE INDEX idx_backups_type ON ops.backups(backup_type, created_at DESC);
CREATE INDEX idx_backups_expires_at ON ops.backups(expires_at) WHERE expires_at IS NOT NULL;

-- Restores table
CREATE TABLE IF NOT EXISTS ops.restores (
    restore_id TEXT PRIMARY KEY DEFAULT 'rst-' || gen_random_uuid()::text,
    backup_id TEXT NOT NULL REFERENCES ops.backups(backup_id) ON DELETE CASCADE,
    target_env_id TEXT NOT NULL REFERENCES ops.environments(env_id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'running', 'success', 'failed', 'cancelled')),
    requested_by TEXT NOT NULL,
    approved_by TEXT,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

COMMENT ON TABLE ops.restores IS 'Restore operation tracking with approval workflow';
COMMENT ON COLUMN ops.restores.requested_by IS 'User who requested the restore';
COMMENT ON COLUMN ops.restores.approved_by IS 'User who approved the restore (required for prod)';

CREATE INDEX idx_restores_backup_id ON ops.restores(backup_id);
CREATE INDEX idx_restores_target_env ON ops.restores(target_env_id, created_at DESC);
CREATE INDEX idx_restores_status ON ops.restores(status) WHERE status IN ('pending', 'approved', 'running');

-- Approvals table
CREATE TABLE IF NOT EXISTS ops.approvals (
    approval_id TEXT PRIMARY KEY DEFAULT 'appr-' || gen_random_uuid()::text,
    approval_type TEXT NOT NULL CHECK (approval_type IN ('deploy_prod', 'restore_prod', 'upgrade_prod')),
    resource_id TEXT NOT NULL,
    requested_by TEXT NOT NULL,
    approved_by TEXT,
    status TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'denied', 'expired')),
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '24 hours',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

COMMENT ON TABLE ops.approvals IS 'Approval gates for production operations';
COMMENT ON COLUMN ops.approvals.approval_type IS 'Type of operation requiring approval';
COMMENT ON COLUMN ops.approvals.resource_id IS 'ID of the resource (run_id, restore_id, etc.)';

CREATE INDEX idx_approvals_resource ON ops.approvals(resource_id);
CREATE INDEX idx_approvals_status ON ops.approvals(status) WHERE status = 'pending';
CREATE INDEX idx_approvals_expires_at ON ops.approvals(expires_at) WHERE status = 'pending';

-- Policies table
CREATE TABLE IF NOT EXISTS ops.policies (
    policy_id TEXT PRIMARY KEY DEFAULT 'pol-' || gen_random_uuid()::text,
    policy_type TEXT NOT NULL CHECK (policy_type IN ('branch_deploy', 'backup_retention', 'approval_required', 'shell_access')),
    project_id TEXT REFERENCES ops.projects(project_id) ON DELETE CASCADE,
    env_type TEXT CHECK (env_type IN ('dev', 'staging', 'prod')),
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    rules JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE ops.policies IS 'Environment policies and rules';
COMMENT ON COLUMN ops.policies.policy_type IS 'Policy type: branch_deploy, backup_retention, approval_required, shell_access';
COMMENT ON COLUMN ops.policies.project_id IS 'Project-specific policy (NULL = org-wide)';
COMMENT ON COLUMN ops.policies.rules IS 'Policy rules as JSON';

CREATE INDEX idx_policies_project ON ops.policies(project_id) WHERE project_id IS NOT NULL;
CREATE INDEX idx_policies_type ON ops.policies(policy_type, enabled);

-- Triggers for updated_at
CREATE TRIGGER restores_updated_at BEFORE UPDATE ON ops.restores
    FOR EACH ROW EXECUTE FUNCTION ops.update_updated_at();

CREATE TRIGGER policies_updated_at BEFORE UPDATE ON ops.policies
    FOR EACH ROW EXECUTE FUNCTION ops.update_updated_at();

-- Function to automatically set backup expiration based on type
CREATE OR REPLACE FUNCTION ops.set_backup_expiration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.expires_at IS NULL THEN
        NEW.expires_at := CASE NEW.backup_type
            WHEN 'daily' THEN NEW.created_at + INTERVAL '7 days'
            WHEN 'weekly' THEN NEW.created_at + INTERVAL '28 days'
            WHEN 'monthly' THEN NEW.created_at + INTERVAL '90 days'
            ELSE NULL  -- manual backups don't auto-expire
        END;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER backups_set_expiration BEFORE INSERT ON ops.backups
    FOR EACH ROW EXECUTE FUNCTION ops.set_backup_expiration();
