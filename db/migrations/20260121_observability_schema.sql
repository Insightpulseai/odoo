-- Unified Observability Schema for Platform Kit Integration
-- Provides job orchestration, agent monitoring, service health, and ecosystem topology
--
-- @see spec/supabase-platform-kit-observability/

-- Create schema for observability
CREATE SCHEMA IF NOT EXISTS observability;

-- ============ Jobs Table (Unified Job Queue) ============
-- Canonical job queue for all sources (n8n, Odoo, MCP, Control Room)
CREATE TABLE IF NOT EXISTS observability.jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,                    -- n8n, odoo, mcp, control-room
    job_type TEXT NOT NULL,                  -- discovery, sync, etl, validation, etc.
    payload JSONB NOT NULL DEFAULT '{}',
    context JSONB,                           -- tracing, correlation_id, etc.
    priority INTEGER NOT NULL DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'completed', 'failed', 'cancelled', 'dead_letter')),
    max_retries INTEGER NOT NULL DEFAULT 3,
    retry_count INTEGER NOT NULL DEFAULT 0,
    scheduled_at TIMESTAMPTZ,
    claimed_by TEXT,                         -- Worker/agent that claimed the job
    claimed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ                   -- Soft delete
);

-- Indexes for job queue operations
CREATE INDEX IF NOT EXISTS idx_obs_jobs_status ON observability.jobs (status);
CREATE INDEX IF NOT EXISTS idx_obs_jobs_source ON observability.jobs (source);
CREATE INDEX IF NOT EXISTS idx_obs_jobs_type ON observability.jobs (job_type);
CREATE INDEX IF NOT EXISTS idx_obs_jobs_queue ON observability.jobs (status, priority DESC, created_at)
    WHERE status = 'queued' AND deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_obs_jobs_created ON observability.jobs (created_at DESC);

-- ============ Job Runs Table (Execution History) ============
CREATE TABLE IF NOT EXISTS observability.job_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES observability.jobs(id) ON DELETE CASCADE,
    run_number INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    duration_ms INTEGER,
    worker_id TEXT,
    result JSONB,
    error JSONB,
    metrics JSONB,                           -- tokens_used, memory_mb, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_obs_job_runs_job ON observability.job_runs (job_id);
CREATE INDEX IF NOT EXISTS idx_obs_job_runs_status ON observability.job_runs (status);

-- ============ Job Events Table (Granular Event Log) ============
CREATE TABLE IF NOT EXISTS observability.job_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES observability.jobs(id) ON DELETE CASCADE,
    run_id UUID REFERENCES observability.job_runs(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL CHECK (event_type IN (
        'created', 'queued', 'claimed', 'started', 'progress',
        'completed', 'failed', 'retrying', 'cancelled', 'dead_letter'
    )),
    payload JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_obs_job_events_job ON observability.job_events (job_id);
CREATE INDEX IF NOT EXISTS idx_obs_job_events_run ON observability.job_events (run_id);
CREATE INDEX IF NOT EXISTS idx_obs_job_events_time ON observability.job_events (timestamp DESC);

-- ============ Dead Letter Queue ============
CREATE TABLE IF NOT EXISTS observability.dead_letter (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES observability.jobs(id) ON DELETE CASCADE,
    reason TEXT NOT NULL,
    last_error JSONB,
    retry_count INTEGER NOT NULL,
    moved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    resolved_by TEXT
);

CREATE INDEX IF NOT EXISTS idx_obs_dlq_resolved ON observability.dead_letter (resolved) WHERE NOT resolved;

-- ============ Services Table (Service Registry) ============
CREATE TABLE IF NOT EXISTS observability.services (
    id TEXT PRIMARY KEY,                     -- odoo-core, n8n, mcp-coordinator, etc.
    name TEXT NOT NULL,
    description TEXT,
    service_type TEXT NOT NULL CHECK (service_type IN ('application', 'database', 'queue', 'external')),
    endpoint TEXT,
    health_endpoint TEXT,
    protocol TEXT NOT NULL DEFAULT 'http' CHECK (protocol IN ('http', 'grpc', 'tcp', 'websocket')),
    port INTEGER,
    status TEXT NOT NULL DEFAULT 'unknown' CHECK (status IN ('healthy', 'degraded', 'unhealthy', 'offline', 'unknown')),
    last_check TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============ Service Health Table (Historical Health Samples) ============
CREATE TABLE IF NOT EXISTS observability.service_health (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id TEXT NOT NULL REFERENCES observability.services(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('healthy', 'degraded', 'unhealthy', 'offline')),
    response_time_ms INTEGER,
    status_code INTEGER,
    error_message TEXT,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_obs_health_service ON observability.service_health (service_id);
CREATE INDEX IF NOT EXISTS idx_obs_health_time ON observability.service_health (checked_at DESC);

-- Partition by time (keep 30 days of history)
-- Note: In production, add proper partitioning

-- ============ Ecosystem Edges Table (Topology Graph) ============
CREATE TABLE IF NOT EXISTS observability.edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id TEXT NOT NULL,                 -- Service or agent ID
    source_type TEXT NOT NULL CHECK (source_type IN ('service', 'agent', 'database', 'external')),
    target_id TEXT NOT NULL,
    target_type TEXT NOT NULL CHECK (target_type IN ('service', 'agent', 'database', 'external')),
    edge_type TEXT NOT NULL CHECK (edge_type IN ('data_flow', 'health_dependency', 'agent_delegation', 'api_call')),
    direction TEXT NOT NULL DEFAULT 'outbound' CHECK (direction IN ('outbound', 'inbound', 'bidirectional')),
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_obs_edges_source ON observability.edges (source_id, source_type);
CREATE INDEX IF NOT EXISTS idx_obs_edges_target ON observability.edges (target_id, target_type);

-- ============ Metrics Table (Aggregated Stats) ============
CREATE TABLE IF NOT EXISTS observability.metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_type TEXT NOT NULL,               -- job_stats, agent_stats, service_stats
    dimensions JSONB NOT NULL,               -- {source, job_type, status} etc.
    values JSONB NOT NULL,                   -- {count, avg_duration_ms, p95_duration_ms}
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_obs_metrics_type ON observability.metrics (metric_type);
CREATE INDEX IF NOT EXISTS idx_obs_metrics_period ON observability.metrics (period_start, period_end);

-- ============ RPC Functions ============

-- Enqueue a new job
CREATE OR REPLACE FUNCTION observability.enqueue_job(
    p_source TEXT,
    p_job_type TEXT,
    p_payload JSONB DEFAULT '{}',
    p_context JSONB DEFAULT NULL,
    p_priority INTEGER DEFAULT 5,
    p_scheduled_at TIMESTAMPTZ DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_job_id UUID;
BEGIN
    INSERT INTO observability.jobs (source, job_type, payload, context, priority, scheduled_at)
    VALUES (p_source, p_job_type, p_payload, p_context, p_priority, COALESCE(p_scheduled_at, NOW()))
    RETURNING id INTO v_job_id;

    -- Log creation event
    INSERT INTO observability.job_events (job_id, event_type, payload)
    VALUES (v_job_id, 'created', jsonb_build_object('source', p_source, 'job_type', p_job_type));

    INSERT INTO observability.job_events (job_id, event_type)
    VALUES (v_job_id, 'queued');

    RETURN v_job_id;
END;
$$ LANGUAGE plpgsql;

-- Claim next job from queue (atomic with SKIP LOCKED)
CREATE OR REPLACE FUNCTION observability.claim_next_job(
    p_worker_id TEXT,
    p_source TEXT DEFAULT NULL,
    p_job_type TEXT DEFAULT NULL
) RETURNS observability.jobs AS $$
DECLARE
    v_job observability.jobs;
    v_run_id UUID;
BEGIN
    SELECT * INTO v_job
    FROM observability.jobs
    WHERE status = 'queued'
      AND deleted_at IS NULL
      AND (scheduled_at IS NULL OR scheduled_at <= NOW())
      AND (p_source IS NULL OR source = p_source)
      AND (p_job_type IS NULL OR job_type = p_job_type)
    ORDER BY priority DESC, created_at ASC
    LIMIT 1
    FOR UPDATE SKIP LOCKED;

    IF v_job.id IS NOT NULL THEN
        UPDATE observability.jobs
        SET status = 'processing',
            claimed_by = p_worker_id,
            claimed_at = NOW(),
            updated_at = NOW()
        WHERE id = v_job.id;

        -- Create run record
        INSERT INTO observability.job_runs (job_id, run_number, worker_id)
        VALUES (v_job.id, v_job.retry_count + 1, p_worker_id)
        RETURNING id INTO v_run_id;

        -- Log events
        INSERT INTO observability.job_events (job_id, run_id, event_type, payload)
        VALUES
            (v_job.id, v_run_id, 'claimed', jsonb_build_object('worker_id', p_worker_id)),
            (v_job.id, v_run_id, 'started', NULL);

        v_job.status := 'processing';
        v_job.claimed_by := p_worker_id;
        v_job.claimed_at := NOW();
    END IF;

    RETURN v_job;
END;
$$ LANGUAGE plpgsql;

-- Complete a job
CREATE OR REPLACE FUNCTION observability.complete_job(
    p_job_id UUID,
    p_result JSONB DEFAULT NULL,
    p_metrics JSONB DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    v_run_id UUID;
    v_started_at TIMESTAMPTZ;
BEGIN
    -- Get current run
    SELECT id, started_at INTO v_run_id, v_started_at
    FROM observability.job_runs
    WHERE job_id = p_job_id AND status = 'running'
    ORDER BY run_number DESC
    LIMIT 1;

    -- Update run
    UPDATE observability.job_runs
    SET status = 'completed',
        ended_at = NOW(),
        duration_ms = EXTRACT(EPOCH FROM (NOW() - started_at)) * 1000,
        result = p_result,
        metrics = p_metrics
    WHERE id = v_run_id;

    -- Update job
    UPDATE observability.jobs
    SET status = 'completed',
        completed_at = NOW(),
        updated_at = NOW()
    WHERE id = p_job_id AND status = 'processing';

    -- Log event
    INSERT INTO observability.job_events (job_id, run_id, event_type, payload)
    VALUES (p_job_id, v_run_id, 'completed', p_result);

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Fail a job (with retry or dead letter)
CREATE OR REPLACE FUNCTION observability.fail_job(
    p_job_id UUID,
    p_error JSONB
) RETURNS TEXT AS $$
DECLARE
    v_job observability.jobs;
    v_run_id UUID;
    v_new_status TEXT;
BEGIN
    SELECT * INTO v_job FROM observability.jobs WHERE id = p_job_id;

    -- Get current run
    SELECT id INTO v_run_id
    FROM observability.job_runs
    WHERE job_id = p_job_id AND status = 'running'
    ORDER BY run_number DESC
    LIMIT 1;

    -- Update run
    UPDATE observability.job_runs
    SET status = 'failed',
        ended_at = NOW(),
        duration_ms = EXTRACT(EPOCH FROM (NOW() - started_at)) * 1000,
        error = p_error
    WHERE id = v_run_id;

    IF v_job.retry_count < v_job.max_retries THEN
        -- Retry: re-queue the job
        UPDATE observability.jobs
        SET status = 'queued',
            retry_count = retry_count + 1,
            claimed_by = NULL,
            claimed_at = NULL,
            updated_at = NOW()
        WHERE id = p_job_id;

        INSERT INTO observability.job_events (job_id, run_id, event_type, payload)
        VALUES (p_job_id, v_run_id, 'retrying', jsonb_build_object('retry_count', v_job.retry_count + 1));

        v_new_status := 'retrying';
    ELSE
        -- Max retries: move to dead letter
        UPDATE observability.jobs
        SET status = 'dead_letter',
            updated_at = NOW()
        WHERE id = p_job_id;

        INSERT INTO observability.dead_letter (job_id, reason, last_error, retry_count)
        VALUES (p_job_id, 'max_retries_exceeded', p_error, v_job.retry_count);

        INSERT INTO observability.job_events (job_id, run_id, event_type, payload)
        VALUES (p_job_id, v_run_id, 'dead_letter', p_error);

        v_new_status := 'dead_letter';
    END IF;

    RETURN v_new_status;
END;
$$ LANGUAGE plpgsql;

-- Retry a dead letter job
CREATE OR REPLACE FUNCTION observability.retry_dead_letter(
    p_job_id UUID
) RETURNS BOOLEAN AS $$
BEGIN
    -- Reset job
    UPDATE observability.jobs
    SET status = 'queued',
        retry_count = 0,
        claimed_by = NULL,
        claimed_at = NULL,
        updated_at = NOW()
    WHERE id = p_job_id AND status = 'dead_letter';

    -- Mark DLQ entry resolved
    UPDATE observability.dead_letter
    SET resolved = TRUE,
        resolved_at = NOW()
    WHERE job_id = p_job_id AND NOT resolved;

    -- Log event
    INSERT INTO observability.job_events (job_id, event_type, payload)
    VALUES (p_job_id, 'queued', jsonb_build_object('source', 'dlq_retry'));

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Update service health
CREATE OR REPLACE FUNCTION observability.record_health(
    p_service_id TEXT,
    p_status TEXT,
    p_response_time_ms INTEGER DEFAULT NULL,
    p_status_code INTEGER DEFAULT NULL,
    p_error_message TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    -- Update service status
    UPDATE observability.services
    SET status = p_status,
        last_check = NOW(),
        updated_at = NOW()
    WHERE id = p_service_id;

    -- Record health sample
    INSERT INTO observability.service_health (service_id, status, response_time_ms, status_code, error_message)
    VALUES (p_service_id, p_status, p_response_time_ms, p_status_code, p_error_message);
END;
$$ LANGUAGE plpgsql;

-- Get aggregated health status
CREATE OR REPLACE FUNCTION observability.get_health_summary()
RETURNS TABLE (
    total_services BIGINT,
    healthy_count BIGINT,
    degraded_count BIGINT,
    unhealthy_count BIGINT,
    offline_count BIGINT,
    overall_status TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH counts AS (
        SELECT
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE status = 'healthy') as healthy,
            COUNT(*) FILTER (WHERE status = 'degraded') as degraded,
            COUNT(*) FILTER (WHERE status = 'unhealthy') as unhealthy,
            COUNT(*) FILTER (WHERE status = 'offline') as offline
        FROM observability.services
    )
    SELECT
        counts.total,
        counts.healthy,
        counts.degraded,
        counts.unhealthy,
        counts.offline,
        CASE
            WHEN counts.unhealthy > 0 OR counts.offline > 0 THEN 'unhealthy'
            WHEN counts.degraded > 0 THEN 'degraded'
            ELSE 'healthy'
        END::TEXT
    FROM counts;
END;
$$ LANGUAGE plpgsql;

-- Get job statistics
CREATE OR REPLACE FUNCTION observability.get_job_stats(
    p_since TIMESTAMPTZ DEFAULT NOW() - INTERVAL '24 hours'
)
RETURNS TABLE (
    source TEXT,
    job_type TEXT,
    total_count BIGINT,
    completed_count BIGINT,
    failed_count BIGINT,
    processing_count BIGINT,
    queued_count BIGINT,
    avg_duration_ms NUMERIC,
    success_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        j.source,
        j.job_type,
        COUNT(*)::BIGINT,
        COUNT(*) FILTER (WHERE j.status = 'completed')::BIGINT,
        COUNT(*) FILTER (WHERE j.status IN ('failed', 'dead_letter'))::BIGINT,
        COUNT(*) FILTER (WHERE j.status = 'processing')::BIGINT,
        COUNT(*) FILTER (WHERE j.status = 'queued')::BIGINT,
        ROUND(AVG(
            CASE WHEN j.completed_at IS NOT NULL
            THEN EXTRACT(EPOCH FROM (j.completed_at - j.created_at)) * 1000
            END
        ), 2),
        ROUND(
            COUNT(*) FILTER (WHERE j.status = 'completed')::NUMERIC /
            NULLIF(COUNT(*) FILTER (WHERE j.status IN ('completed', 'failed', 'dead_letter')), 0) * 100,
            2
        )
    FROM observability.jobs j
    WHERE j.created_at >= p_since
      AND j.deleted_at IS NULL
    GROUP BY j.source, j.job_type
    ORDER BY COUNT(*) DESC;
END;
$$ LANGUAGE plpgsql;

-- Get topology graph
CREATE OR REPLACE FUNCTION observability.get_topology()
RETURNS TABLE (
    nodes JSONB,
    edges JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (
            SELECT jsonb_agg(jsonb_build_object(
                'id', s.id,
                'type', 'service',
                'name', s.name,
                'status', s.status,
                'service_type', s.service_type
            ))
            FROM observability.services s
        ) ||
        (
            SELECT COALESCE(jsonb_agg(jsonb_build_object(
                'id', a.id,
                'type', 'agent',
                'name', a.name,
                'status', a.status,
                'capabilities', a.capabilities
            )), '[]'::jsonb)
            FROM agent_coordination.agent_registry a
            WHERE a.status != 'offline'
        ) as nodes,
        (
            SELECT COALESCE(jsonb_agg(jsonb_build_object(
                'id', e.id,
                'source', e.source_id,
                'target', e.target_id,
                'type', e.edge_type,
                'direction', e.direction
            )), '[]'::jsonb)
            FROM observability.edges e
        ) as edges;
END;
$$ LANGUAGE plpgsql;

-- ============ RLS Policies ============

-- Enable RLS on all tables
ALTER TABLE observability.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE observability.job_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE observability.job_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE observability.dead_letter ENABLE ROW LEVEL SECURITY;
ALTER TABLE observability.services ENABLE ROW LEVEL SECURITY;
ALTER TABLE observability.service_health ENABLE ROW LEVEL SECURITY;
ALTER TABLE observability.edges ENABLE ROW LEVEL SECURITY;
ALTER TABLE observability.metrics ENABLE ROW LEVEL SECURITY;

-- Service role has full access
CREATE POLICY "service_role_all" ON observability.jobs FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON observability.job_runs FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON observability.job_events FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON observability.dead_letter FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON observability.services FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON observability.service_health FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON observability.edges FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON observability.metrics FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Authenticated users can read
CREATE POLICY "authenticated_read" ON observability.jobs FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read" ON observability.job_runs FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read" ON observability.job_events FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read" ON observability.dead_letter FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read" ON observability.services FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read" ON observability.service_health FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read" ON observability.edges FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read" ON observability.metrics FOR SELECT TO authenticated USING (true);

-- Grant permissions
GRANT USAGE ON SCHEMA observability TO service_role, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA observability TO service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA observability TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA observability TO service_role, authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA observability TO service_role;

-- ============ Seed Default Services ============

INSERT INTO observability.services (id, name, description, service_type, endpoint, health_endpoint, port) VALUES
    ('odoo-core', 'Odoo CE Core', 'Main Odoo CE instance', 'application', 'http://localhost:8069', '/web/health', 8069),
    ('odoo-marketing', 'Odoo Marketing', 'Marketing edition instance', 'application', 'http://localhost:8070', '/web/health', 8070),
    ('odoo-accounting', 'Odoo Accounting', 'Accounting edition instance', 'application', 'http://localhost:8071', '/web/health', 8071),
    ('n8n', 'n8n Workflows', 'Workflow automation engine', 'application', 'http://localhost:5678', '/healthz', 5678),
    ('mcp-coordinator', 'MCP Coordinator', 'MCP routing and aggregation', 'application', 'http://localhost:8766', '/health', 8766),
    ('postgres', 'PostgreSQL', 'Primary database', 'database', 'localhost', NULL, 5432),
    ('supabase', 'Supabase', 'External BaaS', 'external', 'https://spdtwktxdalcfigzeqrz.supabase.co', '/rest/v1/', 443)
ON CONFLICT (id) DO NOTHING;

-- Seed default topology edges
INSERT INTO observability.edges (source_id, source_type, target_id, target_type, edge_type, direction) VALUES
    ('odoo-core', 'service', 'postgres', 'database', 'data_flow', 'outbound'),
    ('odoo-marketing', 'service', 'postgres', 'database', 'data_flow', 'outbound'),
    ('odoo-accounting', 'service', 'postgres', 'database', 'data_flow', 'outbound'),
    ('n8n', 'service', 'odoo-core', 'service', 'api_call', 'outbound'),
    ('n8n', 'service', 'supabase', 'external', 'api_call', 'outbound'),
    ('mcp-coordinator', 'service', 'odoo-core', 'service', 'api_call', 'outbound'),
    ('mcp-coordinator', 'service', 'supabase', 'external', 'api_call', 'outbound')
ON CONFLICT DO NOTHING;

-- Comments
COMMENT ON SCHEMA observability IS 'Unified observability schema for job orchestration, agent monitoring, and service health';
COMMENT ON TABLE observability.jobs IS 'Canonical job queue for all sources (n8n, Odoo, MCP, Control Room)';
COMMENT ON TABLE observability.job_runs IS 'Execution history for each job attempt';
COMMENT ON TABLE observability.job_events IS 'Granular event log for job lifecycle';
COMMENT ON TABLE observability.dead_letter IS 'Failed jobs after max retries for manual resolution';
COMMENT ON TABLE observability.services IS 'Registry of services with health status';
COMMENT ON TABLE observability.service_health IS 'Historical health samples for uptime tracking';
COMMENT ON TABLE observability.edges IS 'Topology graph edges for ecosystem visualization';
COMMENT ON TABLE observability.metrics IS 'Aggregated metrics for dashboards';
