-- Migration: OdooOps Control Plane Schema - RBAC (Roles and Permissions)
-- Purpose: Add role-based access control for projects and environments

-- Roles table
CREATE TABLE IF NOT EXISTS ops.roles (
    role_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE ops.roles IS 'Role definitions with permissions';
COMMENT ON COLUMN ops.roles.permissions IS 'Array of permission strings';

-- Insert default roles
INSERT INTO ops.roles (role_id, name, description, permissions) VALUES
    ('owner', 'Owner', 'Full access to project', '["*"]'::jsonb),
    ('admin', 'Admin', 'Project administration', '["project:*", "env:*", "run:*", "backup:*", "restore:staging"]'::jsonb),
    ('developer', 'Developer', 'Development access', '["project:read", "env:read", "run:create", "run:read", "run:logs", "backup:read"]'::jsonb),
    ('viewer', 'Viewer', 'Read-only access', '["project:read", "env:read", "run:read", "backup:read"]'::jsonb),
    ('auditor', 'Auditor', 'Audit access', '["project:read", "env:read", "run:read", "run:audit", "backup:read", "approval:read"]'::jsonb)
ON CONFLICT (role_id) DO NOTHING;

-- Project members table
CREATE TABLE IF NOT EXISTS ops.project_members (
    project_id TEXT NOT NULL REFERENCES ops.projects(project_id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    role_id TEXT NOT NULL REFERENCES ops.roles(role_id),
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (project_id, user_id)
);

COMMENT ON TABLE ops.project_members IS 'Project membership and role assignments';
COMMENT ON COLUMN ops.project_members.user_id IS 'User identifier (Supabase auth.users.id or external ID)';

CREATE INDEX idx_project_members_user ON ops.project_members(user_id);
CREATE INDEX idx_project_members_role ON ops.project_members(role_id);

-- Environment permissions table (granular env-specific overrides)
CREATE TABLE IF NOT EXISTS ops.env_permissions (
    env_id TEXT NOT NULL REFERENCES ops.environments(env_id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    permissions JSONB NOT NULL DEFAULT '[]'::jsonb,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (env_id, user_id)
);

COMMENT ON TABLE ops.env_permissions IS 'Environment-specific permission overrides';
COMMENT ON COLUMN ops.env_permissions.permissions IS 'Additional permissions for this environment';

CREATE INDEX idx_env_permissions_user ON ops.env_permissions(user_id);

-- Function to check if user has permission
CREATE OR REPLACE FUNCTION ops.user_has_permission(
    p_user_id TEXT,
    p_project_id TEXT,
    p_permission TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    v_role_permissions JSONB;
    v_has_permission BOOLEAN := FALSE;
BEGIN
    -- Check if user is project member and get role permissions
    SELECT r.permissions INTO v_role_permissions
    FROM ops.project_members pm
    JOIN ops.roles r ON pm.role_id = r.role_id
    WHERE pm.project_id = p_project_id AND pm.user_id = p_user_id;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    -- Check for wildcard permission
    IF v_role_permissions ? '*' THEN
        RETURN TRUE;
    END IF;

    -- Check for exact permission match
    IF v_role_permissions ? p_permission THEN
        RETURN TRUE;
    END IF;

    -- Check for prefix wildcard (e.g., "run:*" matches "run:create")
    SELECT EXISTS(
        SELECT 1
        FROM jsonb_array_elements_text(v_role_permissions) AS perm
        WHERE perm LIKE '%:*' AND p_permission LIKE REPLACE(perm, '*', '%')
    ) INTO v_has_permission;

    RETURN v_has_permission;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION ops.user_has_permission IS 'Check if user has a specific permission on a project';
