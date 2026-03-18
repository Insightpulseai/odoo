-- Migration: OdooOps Control Plane Schema - Row Level Security
-- Purpose: Add RLS policies for all ops tables with project/team-based access control

-- Enable RLS on all ops tables
ALTER TABLE ops.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.environments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.run_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.backups ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.restores ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.project_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.env_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.agent_teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.agent_team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.agent_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.agent_events ENABLE ROW LEVEL SECURITY;

-- Helper function to get current user's project memberships
CREATE OR REPLACE FUNCTION ops.current_user_projects()
RETURNS SETOF TEXT AS $$
BEGIN
    RETURN QUERY
    SELECT project_id
    FROM ops.project_members
    WHERE user_id = auth.uid()::text;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper function to check if user is project member
CREATE OR REPLACE FUNCTION ops.is_project_member(p_project_id TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM ops.project_members
        WHERE project_id = p_project_id
          AND user_id = auth.uid()::text
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper function to check if user is agent team member
CREATE OR REPLACE FUNCTION ops.is_team_member(p_team_id TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM ops.agent_team_members atm
        JOIN ops.agents a ON atm.agent_id = a.agent_id
        WHERE atm.team_id = p_team_id
          AND a.metadata->>'user_id' = auth.uid()::text
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Projects: Members can view their projects
CREATE POLICY projects_select ON ops.projects
    FOR SELECT
    USING (project_id IN (SELECT ops.current_user_projects()));

CREATE POLICY projects_insert ON ops.projects
    FOR INSERT
    WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY projects_update ON ops.projects
    FOR UPDATE
    USING (ops.user_has_permission(auth.uid()::text, project_id, 'project:update'));

-- Environments: Members can view their project environments
CREATE POLICY environments_select ON ops.environments
    FOR SELECT
    USING (ops.is_project_member(project_id));

CREATE POLICY environments_insert ON ops.environments
    FOR INSERT
    WITH CHECK (ops.user_has_permission(auth.uid()::text, project_id, 'env:create'));

CREATE POLICY environments_update ON ops.environments
    FOR UPDATE
    USING (ops.user_has_permission(auth.uid()::text, project_id, 'env:update'));

-- Runs: Members can view their project runs
CREATE POLICY runs_select ON ops.runs
    FOR SELECT
    USING (ops.is_project_member(project_id));

CREATE POLICY runs_insert ON ops.runs
    FOR INSERT
    WITH CHECK (ops.user_has_permission(auth.uid()::text, project_id, 'run:create'));

CREATE POLICY runs_update ON ops.runs
    FOR UPDATE
    USING (
        ops.user_has_permission(auth.uid()::text, project_id, 'run:update')
        OR claimed_by = auth.uid()::text
    );

-- Run Events: Members can view events for their project runs
CREATE POLICY run_events_select ON ops.run_events
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM ops.runs r
            WHERE r.run_id = ops.run_events.run_id
              AND ops.is_project_member(r.project_id)
        )
    );

CREATE POLICY run_events_insert ON ops.run_events
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM ops.runs r
            WHERE r.run_id = ops.run_events.run_id
              AND (
                  ops.user_has_permission(auth.uid()::text, r.project_id, 'run:logs')
                  OR r.claimed_by = auth.uid()::text
              )
        )
    );

-- Artifacts: Members can view artifacts for their project runs
CREATE POLICY artifacts_select ON ops.artifacts
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM ops.runs r
            WHERE r.run_id = ops.artifacts.run_id
              AND ops.is_project_member(r.project_id)
        )
    );

CREATE POLICY artifacts_insert ON ops.artifacts
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM ops.runs r
            WHERE r.run_id = ops.artifacts.run_id
              AND (
                  ops.user_has_permission(auth.uid()::text, r.project_id, 'run:create')
                  OR r.claimed_by = auth.uid()::text
              )
        )
    );

-- Backups: Members can view their project backups
CREATE POLICY backups_select ON ops.backups
    FOR SELECT
    USING (ops.is_project_member(project_id));

CREATE POLICY backups_insert ON ops.backups
    FOR INSERT
    WITH CHECK (ops.user_has_permission(auth.uid()::text, project_id, 'backup:create'));

-- Restores: Members can view restores for their projects
CREATE POLICY restores_select ON ops.restores
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM ops.environments e
            WHERE e.env_id = ops.restores.target_env_id
              AND ops.is_project_member(e.project_id)
        )
    );

CREATE POLICY restores_insert ON ops.restores
    FOR INSERT
    WITH CHECK (
        requested_by = auth.uid()::text
        AND EXISTS (
            SELECT 1 FROM ops.environments e
            WHERE e.env_id = target_env_id
              AND ops.user_has_permission(auth.uid()::text, e.project_id, 'restore:staging')
        )
    );

CREATE POLICY restores_update ON ops.restores
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM ops.environments e
            WHERE e.env_id = target_env_id
              AND ops.user_has_permission(auth.uid()::text, e.project_id, 'restore:approve')
        )
    );

-- Approvals: Requesters and approvers can view
CREATE POLICY approvals_select ON ops.approvals
    FOR SELECT
    USING (
        requested_by = auth.uid()::text
        OR approved_by = auth.uid()::text
    );

CREATE POLICY approvals_insert ON ops.approvals
    FOR INSERT
    WITH CHECK (requested_by = auth.uid()::text);

CREATE POLICY approvals_update ON ops.approvals
    FOR UPDATE
    USING (approved_by = auth.uid()::text OR requested_by = auth.uid()::text);

-- Policies: Admins only (checked via user_has_permission in application layer)
CREATE POLICY policies_select ON ops.policies
    FOR SELECT
    USING (
        project_id IS NULL -- Org-wide policies visible to all
        OR ops.is_project_member(project_id)
    );

-- Roles: Read-only for all authenticated users
CREATE POLICY roles_select ON ops.roles
    FOR SELECT
    USING (auth.uid() IS NOT NULL);

-- Project Members: Users can see their own memberships
CREATE POLICY project_members_select ON ops.project_members
    FOR SELECT
    USING (
        user_id = auth.uid()::text
        OR ops.user_has_permission(auth.uid()::text, project_id, 'project:read')
    );

-- Environment Permissions: Users can see their own permissions
CREATE POLICY env_permissions_select ON ops.env_permissions
    FOR SELECT
    USING (
        user_id = auth.uid()::text
        OR EXISTS (
            SELECT 1 FROM ops.environments e
            WHERE e.env_id = ops.env_permissions.env_id
              AND ops.user_has_permission(auth.uid()::text, e.project_id, 'env:read')
        )
    );

-- Agents: Team members and system can view/update
CREATE POLICY agents_select ON ops.agents
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM ops.agent_team_members atm
            WHERE atm.agent_id = ops.agents.agent_id
              AND ops.is_team_member(atm.team_id)
        )
    );

CREATE POLICY agents_insert ON ops.agents
    FOR INSERT
    WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY agents_update ON ops.agents
    FOR UPDATE
    USING (agent_id = auth.uid()::text);

-- Agent Teams: Team members can view
CREATE POLICY agent_teams_select ON ops.agent_teams
    FOR SELECT
    USING (ops.is_team_member(team_id) OR auth.uid() IS NOT NULL);

-- Agent Team Members: Team members can view
CREATE POLICY agent_team_members_select ON ops.agent_team_members
    FOR SELECT
    USING (ops.is_team_member(team_id));

-- Agent Tasks: Team members can view and claim
CREATE POLICY agent_tasks_select ON ops.agent_tasks
    FOR SELECT
    USING (ops.is_team_member(team_id));

CREATE POLICY agent_tasks_insert ON ops.agent_tasks
    FOR INSERT
    WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY agent_tasks_update ON ops.agent_tasks
    FOR UPDATE
    USING (
        ops.is_team_member(team_id)
        OR claimed_by = auth.uid()::text
    );

-- Agent Events: Team members can view
CREATE POLICY agent_events_select ON ops.agent_events
    FOR SELECT
    USING (
        team_id IS NOT NULL AND ops.is_team_member(team_id)
        OR EXISTS (
            SELECT 1 FROM ops.agents a
            WHERE a.agent_id = ops.agent_events.agent_id
              AND a.metadata->>'user_id' = auth.uid()::text
        )
    );

CREATE POLICY agent_events_insert ON ops.agent_events
    FOR INSERT
    WITH CHECK (
        agent_id IS NOT NULL
        AND EXISTS (
            SELECT 1 FROM ops.agents a
            WHERE a.agent_id = ops.agent_events.agent_id
              AND a.metadata->>'user_id' = auth.uid()::text
        )
    );

-- Grant access to authenticated users
GRANT USAGE ON SCHEMA ops TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA ops TO authenticated;
GRANT INSERT ON ops.projects, ops.environments, ops.runs, ops.run_events, ops.artifacts TO authenticated;
GRANT INSERT ON ops.backups, ops.restores, ops.approvals TO authenticated;
GRANT INSERT ON ops.agents, ops.agent_tasks, ops.agent_events TO authenticated;
GRANT UPDATE ON ops.runs, ops.restores, ops.approvals, ops.agents, ops.agent_tasks TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ops TO authenticated;
