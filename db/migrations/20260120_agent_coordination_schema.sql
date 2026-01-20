-- Agent Coordination Schema for A2A Communication
-- Implements the service discovery and message routing pattern
-- Based on Microsoft's A2A on MCP architecture
--
-- @see https://developer.microsoft.com/blog/can-you-build-agent2agent-communication-on-mcp-yes

-- Create schema for agent coordination
CREATE SCHEMA IF NOT EXISTS agent_coordination;

-- ============ Agent Registry Table ============
-- Stores metadata about registered agents
CREATE TABLE IF NOT EXISTS agent_coordination.agent_registry (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    description TEXT NOT NULL,
    capabilities TEXT[] NOT NULL DEFAULT '{}',
    transport TEXT NOT NULL CHECK (transport IN ('stdio', 'http', 'grpc', 'websocket')),
    endpoint TEXT,
    mcp_server TEXT,
    tools TEXT[] DEFAULT '{}',
    input_schema JSONB,
    output_schema JSONB,
    timeout_ms INTEGER NOT NULL DEFAULT 30000,
    max_concurrent INTEGER NOT NULL DEFAULT 5,
    retry_policy JSONB,
    tags TEXT[] DEFAULT '{}',
    owner TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'idle', 'busy', 'offline', 'maintenance')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_heartbeat TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_agent_registry_capabilities ON agent_coordination.agent_registry USING GIN (capabilities);
CREATE INDEX IF NOT EXISTS idx_agent_registry_status ON agent_coordination.agent_registry (status);
CREATE INDEX IF NOT EXISTS idx_agent_registry_tags ON agent_coordination.agent_registry USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_agent_registry_tools ON agent_coordination.agent_registry USING GIN (tools);
CREATE INDEX IF NOT EXISTS idx_agent_registry_heartbeat ON agent_coordination.agent_registry (last_heartbeat);

-- ============ Agent State Table ============
-- Runtime state for active agents
CREATE TABLE IF NOT EXISTS agent_coordination.agent_state (
    agent_id TEXT PRIMARY KEY REFERENCES agent_coordination.agent_registry(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'idle' CHECK (status IN ('active', 'idle', 'busy', 'offline', 'maintenance')),
    current_task_id TEXT,
    queue_depth INTEGER NOT NULL DEFAULT 0,
    last_heartbeat TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resource_usage JSONB,
    metrics JSONB,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============ Agent Messages Table ============
-- Inter-agent message log
CREATE TABLE IF NOT EXISTS agent_coordination.agent_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_agent_id TEXT NOT NULL,
    to_agent_id TEXT NOT NULL,
    request_type TEXT NOT NULL CHECK (request_type IN ('tool_call', 'query', 'stream', 'event', 'handoff', 'delegate')),
    payload JSONB NOT NULL,
    context JSONB,
    priority TEXT NOT NULL DEFAULT 'normal' CHECK (priority IN ('critical', 'high', 'normal', 'low')),
    timeout_ms INTEGER NOT NULL DEFAULT 30000,
    requires_ack BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Indexes for message queries
CREATE INDEX IF NOT EXISTS idx_agent_messages_from ON agent_coordination.agent_messages (from_agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_messages_to ON agent_coordination.agent_messages (to_agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_messages_created ON agent_coordination.agent_messages (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_messages_priority ON agent_coordination.agent_messages (priority) WHERE priority IN ('critical', 'high');

-- ============ Agent Responses Table ============
-- Responses to inter-agent messages
CREATE TABLE IF NOT EXISTS agent_coordination.agent_responses (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    in_reply_to UUID NOT NULL REFERENCES agent_coordination.agent_messages(message_id),
    from_agent_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('success', 'error', 'timeout', 'cancelled', 'partial')),
    result JSONB,
    error JSONB,
    execution_time_ms INTEGER,
    tokens_used INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_responses_reply ON agent_coordination.agent_responses (in_reply_to);

-- ============ Agent Jobs Table ============
-- Async job queue for agent tasks
CREATE TABLE IF NOT EXISTS agent_coordination.agent_jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_agent_id TEXT NOT NULL,
    target_agent_id TEXT NOT NULL,
    request_type TEXT NOT NULL DEFAULT 'tool_call',
    payload JSONB NOT NULL,
    context JSONB,
    priority TEXT NOT NULL DEFAULT 'normal' CHECK (priority IN ('critical', 'high', 'normal', 'low')),
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'completed', 'failed', 'cancelled')),
    result JSONB,
    error JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3
);

-- Indexes for job queue operations
CREATE INDEX IF NOT EXISTS idx_agent_jobs_target ON agent_coordination.agent_jobs (target_agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_jobs_status ON agent_coordination.agent_jobs (status);
CREATE INDEX IF NOT EXISTS idx_agent_jobs_queue ON agent_coordination.agent_jobs (status, priority, created_at)
    WHERE status = 'queued';

-- ============ RPC Functions ============

-- Register or update an agent
CREATE OR REPLACE FUNCTION agent_coordination.upsert_agent(
    p_id TEXT,
    p_name TEXT,
    p_version TEXT,
    p_description TEXT,
    p_capabilities TEXT[],
    p_transport TEXT,
    p_endpoint TEXT DEFAULT NULL,
    p_mcp_server TEXT DEFAULT NULL,
    p_tools TEXT[] DEFAULT '{}',
    p_timeout_ms INTEGER DEFAULT 30000,
    p_max_concurrent INTEGER DEFAULT 5,
    p_tags TEXT[] DEFAULT '{}'
) RETURNS agent_coordination.agent_registry AS $$
DECLARE
    v_result agent_coordination.agent_registry;
BEGIN
    INSERT INTO agent_coordination.agent_registry (
        id, name, version, description, capabilities, transport,
        endpoint, mcp_server, tools, timeout_ms, max_concurrent, tags
    ) VALUES (
        p_id, p_name, p_version, p_description, p_capabilities, p_transport,
        p_endpoint, p_mcp_server, p_tools, p_timeout_ms, p_max_concurrent, p_tags
    )
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        version = EXCLUDED.version,
        description = EXCLUDED.description,
        capabilities = EXCLUDED.capabilities,
        transport = EXCLUDED.transport,
        endpoint = EXCLUDED.endpoint,
        mcp_server = EXCLUDED.mcp_server,
        tools = EXCLUDED.tools,
        timeout_ms = EXCLUDED.timeout_ms,
        max_concurrent = EXCLUDED.max_concurrent,
        tags = EXCLUDED.tags,
        updated_at = NOW(),
        last_heartbeat = NOW()
    RETURNING * INTO v_result;

    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

-- Send heartbeat to keep agent alive
CREATE OR REPLACE FUNCTION agent_coordination.agent_heartbeat(
    p_agent_id TEXT
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE agent_coordination.agent_registry
    SET last_heartbeat = NOW(),
        status = 'active'
    WHERE id = p_agent_id;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Discover agents by criteria
CREATE OR REPLACE FUNCTION agent_coordination.discover_agents(
    p_capabilities TEXT[] DEFAULT NULL,
    p_status TEXT[] DEFAULT NULL,
    p_tags TEXT[] DEFAULT NULL,
    p_tools TEXT[] DEFAULT NULL,
    p_max_results INTEGER DEFAULT 50
) RETURNS SETOF agent_coordination.agent_registry AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM agent_coordination.agent_registry
    WHERE (p_capabilities IS NULL OR capabilities && p_capabilities)
      AND (p_status IS NULL OR status = ANY(p_status))
      AND (p_tags IS NULL OR tags && p_tags)
      AND (p_tools IS NULL OR tools && p_tools)
    ORDER BY last_heartbeat DESC NULLS LAST
    LIMIT p_max_results;
END;
$$ LANGUAGE plpgsql;

-- Claim next job from queue (atomic operation)
CREATE OR REPLACE FUNCTION agent_coordination.claim_next_job(
    p_agent_id TEXT
) RETURNS agent_coordination.agent_jobs AS $$
DECLARE
    v_job agent_coordination.agent_jobs;
BEGIN
    SELECT * INTO v_job
    FROM agent_coordination.agent_jobs
    WHERE target_agent_id = p_agent_id
      AND status = 'queued'
    ORDER BY
        CASE priority
            WHEN 'critical' THEN 1
            WHEN 'high' THEN 2
            WHEN 'normal' THEN 3
            WHEN 'low' THEN 4
        END,
        created_at ASC
    LIMIT 1
    FOR UPDATE SKIP LOCKED;

    IF v_job.job_id IS NOT NULL THEN
        UPDATE agent_coordination.agent_jobs
        SET status = 'processing',
            started_at = NOW()
        WHERE job_id = v_job.job_id;

        v_job.status := 'processing';
        v_job.started_at := NOW();
    END IF;

    RETURN v_job;
END;
$$ LANGUAGE plpgsql;

-- Complete a job
CREATE OR REPLACE FUNCTION agent_coordination.complete_job(
    p_job_id UUID,
    p_result JSONB
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE agent_coordination.agent_jobs
    SET status = 'completed',
        result = p_result,
        completed_at = NOW()
    WHERE job_id = p_job_id
      AND status = 'processing';

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Fail a job (with optional retry)
CREATE OR REPLACE FUNCTION agent_coordination.fail_job(
    p_job_id UUID,
    p_error JSONB
) RETURNS TEXT AS $$
DECLARE
    v_job agent_coordination.agent_jobs;
    v_new_status TEXT;
BEGIN
    SELECT * INTO v_job
    FROM agent_coordination.agent_jobs
    WHERE job_id = p_job_id;

    IF v_job.retry_count < v_job.max_retries THEN
        -- Retry: re-queue the job
        UPDATE agent_coordination.agent_jobs
        SET status = 'queued',
            retry_count = retry_count + 1,
            error = p_error,
            started_at = NULL
        WHERE job_id = p_job_id;
        v_new_status := 'queued';
    ELSE
        -- Max retries reached: mark as failed
        UPDATE agent_coordination.agent_jobs
        SET status = 'failed',
            error = p_error,
            completed_at = NOW()
        WHERE job_id = p_job_id;
        v_new_status := 'failed';
    END IF;

    RETURN v_new_status;
END;
$$ LANGUAGE plpgsql;

-- Mark stale agents as offline
CREATE OR REPLACE FUNCTION agent_coordination.mark_stale_offline(
    p_threshold_ms INTEGER DEFAULT 300000  -- 5 minutes
) RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    WITH updated AS (
        UPDATE agent_coordination.agent_registry
        SET status = 'offline'
        WHERE last_heartbeat < NOW() - (p_threshold_ms || ' milliseconds')::INTERVAL
          AND status != 'offline'
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_count FROM updated;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- Get registry statistics
CREATE OR REPLACE FUNCTION agent_coordination.get_stats()
RETURNS TABLE (
    total_agents BIGINT,
    active_agents BIGINT,
    idle_agents BIGINT,
    busy_agents BIGINT,
    offline_agents BIGINT,
    pending_jobs BIGINT,
    processing_jobs BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(*) FROM agent_coordination.agent_registry),
        (SELECT COUNT(*) FROM agent_coordination.agent_registry WHERE status = 'active'),
        (SELECT COUNT(*) FROM agent_coordination.agent_registry WHERE status = 'idle'),
        (SELECT COUNT(*) FROM agent_coordination.agent_registry WHERE status = 'busy'),
        (SELECT COUNT(*) FROM agent_coordination.agent_registry WHERE status = 'offline'),
        (SELECT COUNT(*) FROM agent_coordination.agent_jobs WHERE status = 'queued'),
        (SELECT COUNT(*) FROM agent_coordination.agent_jobs WHERE status = 'processing');
END;
$$ LANGUAGE plpgsql;

-- Grant permissions for service role
GRANT USAGE ON SCHEMA agent_coordination TO service_role;
GRANT ALL ON ALL TABLES IN SCHEMA agent_coordination TO service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA agent_coordination TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA agent_coordination TO service_role;

-- Comment for documentation
COMMENT ON SCHEMA agent_coordination IS 'Agent-to-Agent (A2A) coordination schema for MCP multi-agent communication';
COMMENT ON TABLE agent_coordination.agent_registry IS 'Registry of available agents with their capabilities and transport configuration';
COMMENT ON TABLE agent_coordination.agent_messages IS 'Inter-agent message log for A2A communication tracing';
COMMENT ON TABLE agent_coordination.agent_jobs IS 'Async job queue for agent task execution';
