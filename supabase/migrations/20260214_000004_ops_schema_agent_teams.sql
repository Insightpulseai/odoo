-- Migration: OdooOps Control Plane Schema - Agent Teams
-- Purpose: Add multi-agent coordination and team-based task claiming

-- Agents table
CREATE TABLE IF NOT EXISTS ops.agents (
    agent_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT,
    capabilities JSONB NOT NULL DEFAULT '[]'::jsonb,
    status TEXT NOT NULL CHECK (status IN ('idle', 'running', 'disabled', 'error')) DEFAULT 'idle',
    last_heartbeat TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE ops.agents IS 'Worker agents that execute runs/tasks';
COMMENT ON COLUMN ops.agents.capabilities IS 'Array of capability strings: build, deploy, test, backup, etc.';
COMMENT ON COLUMN ops.agents.last_heartbeat IS 'Last heartbeat timestamp for health monitoring';

CREATE INDEX idx_agents_status ON ops.agents(status) WHERE status IN ('idle', 'running');
CREATE INDEX idx_agents_heartbeat ON ops.agents(last_heartbeat DESC) WHERE status != 'disabled';

-- Agent teams table
CREATE TABLE IF NOT EXISTS ops.agent_teams (
    team_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

COMMENT ON TABLE ops.agent_teams IS 'Logical groupings of agents with shared goals/roles';

-- Agent team members table
CREATE TABLE IF NOT EXISTS ops.agent_team_members (
    team_id TEXT NOT NULL REFERENCES ops.agent_teams(team_id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL REFERENCES ops.agents(agent_id) ON DELETE CASCADE,
    role TEXT,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (team_id, agent_id)
);

COMMENT ON TABLE ops.agent_team_members IS 'Team membership for agents';
COMMENT ON COLUMN ops.agent_team_members.role IS 'Agent role within team: executor, coordinator, etc.';

CREATE INDEX idx_agent_team_members_agent ON ops.agent_team_members(agent_id);

-- Agent tasks table (for team-based work queues)
CREATE TABLE IF NOT EXISTS ops.agent_tasks (
    task_id TEXT PRIMARY KEY DEFAULT 'task-' || gen_random_uuid()::text,
    team_id TEXT NOT NULL REFERENCES ops.agent_teams(team_id) ON DELETE CASCADE,
    task_type TEXT NOT NULL CHECK (task_type IN ('build', 'deploy', 'test', 'backup', 'restore', 'upgrade', 'cleanup')),
    status TEXT NOT NULL CHECK (status IN ('pending', 'assigned', 'running', 'complete', 'failed', 'cancelled')) DEFAULT 'pending',
    payload JSONB NOT NULL,
    result JSONB,
    claimed_by TEXT REFERENCES ops.agents(agent_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ
);

COMMENT ON TABLE ops.agent_tasks IS 'Task queue for agent teams';
COMMENT ON COLUMN ops.agent_tasks.task_type IS 'Type of task to execute';
COMMENT ON COLUMN ops.agent_tasks.payload IS 'Task input/parameters';
COMMENT ON COLUMN ops.agent_tasks.result IS 'Task output/result';

CREATE INDEX idx_agent_tasks_team_status ON ops.agent_tasks(team_id, status, created_at) WHERE status IN ('pending', 'assigned', 'running');
CREATE INDEX idx_agent_tasks_claimed_by ON ops.agent_tasks(claimed_by) WHERE claimed_by IS NOT NULL;

-- Agent events table (audit trail for agent actions)
CREATE TABLE IF NOT EXISTS ops.agent_events (
    event_id TEXT PRIMARY KEY DEFAULT 'aevt-' || gen_random_uuid()::text,
    agent_id TEXT REFERENCES ops.agents(agent_id) ON DELETE CASCADE,
    team_id TEXT REFERENCES ops.agent_teams(team_id) ON DELETE CASCADE,
    task_id TEXT REFERENCES ops.agent_tasks(task_id) ON DELETE CASCADE,
    level TEXT NOT NULL CHECK (level IN ('debug', 'info', 'warn', 'error')),
    message TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE ops.agent_events IS 'Event log for agent/team activities';

CREATE INDEX idx_agent_events_agent ON ops.agent_events(agent_id, created_at DESC);
CREATE INDEX idx_agent_events_team ON ops.agent_events(team_id, created_at DESC);
CREATE INDEX idx_agent_events_task ON ops.agent_events(task_id, created_at DESC);
CREATE INDEX idx_agent_events_level ON ops.agent_events(level) WHERE level IN ('warn', 'error');

-- Triggers for updated_at
CREATE TRIGGER agents_updated_at BEFORE UPDATE ON ops.agents
    FOR EACH ROW EXECUTE FUNCTION ops.update_updated_at();

CREATE TRIGGER agent_tasks_updated_at BEFORE UPDATE ON ops.agent_tasks
    FOR EACH ROW EXECUTE FUNCTION ops.update_updated_at();

-- Function to update agent heartbeat
CREATE OR REPLACE FUNCTION ops.agent_heartbeat(p_agent_id TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE ops.agents
    SET last_heartbeat = NOW(),
        updated_at = NOW()
    WHERE agent_id = p_agent_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION ops.agent_heartbeat IS 'Update agent heartbeat timestamp';

-- Function to claim next task for agent
CREATE OR REPLACE FUNCTION ops.claim_next_task(
    p_agent_id TEXT,
    p_team_id TEXT DEFAULT NULL
) RETURNS TABLE (
    task_id TEXT,
    task_type TEXT,
    payload JSONB
) AS $$
DECLARE
    v_task_id TEXT;
BEGIN
    -- Find and claim next pending task (with row-level locking)
    SELECT t.task_id INTO v_task_id
    FROM ops.agent_tasks t
    WHERE t.status = 'pending'
      AND (p_team_id IS NULL OR t.team_id = p_team_id)
    ORDER BY t.created_at
    LIMIT 1
    FOR UPDATE SKIP LOCKED;

    IF v_task_id IS NULL THEN
        RETURN;
    END IF;

    -- Claim the task
    UPDATE ops.agent_tasks
    SET status = 'assigned',
        claimed_by = p_agent_id,
        updated_at = NOW()
    WHERE ops.agent_tasks.task_id = v_task_id;

    -- Update agent status
    UPDATE ops.agents
    SET status = 'running',
        last_heartbeat = NOW(),
        updated_at = NOW()
    WHERE agent_id = p_agent_id;

    -- Return claimed task
    RETURN QUERY
    SELECT t.task_id, t.task_type, t.payload
    FROM ops.agent_tasks t
    WHERE t.task_id = v_task_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION ops.claim_next_task IS 'Claim next pending task for an agent';

-- Insert default teams
INSERT INTO ops.agent_teams (team_id, name, description) VALUES
    ('runner-team', 'Runner Team', 'Agents that perform builds and deploys'),
    ('backup-team', 'Backup Team', 'Agents that perform backups'),
    ('restore-team', 'Restore Team', 'Agents that execute restore operations'),
    ('upgrade-team', 'Upgrade Team', 'Agents that run upgrade previews'),
    ('test-team', 'Test Team', 'Agents that run smoke and automated tests')
ON CONFLICT (team_id) DO NOTHING;
