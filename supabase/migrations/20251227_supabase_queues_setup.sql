-- Migration: Supabase Queues (PGMQ) Setup
-- Exploits native Supabase Queues for async processing

-- ============================================================================
-- ENABLE PGMQ EXTENSION
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS pgmq;

-- ============================================================================
-- CREATE QUEUES
-- ============================================================================

-- MCP Operations Queue (high priority)
SELECT pgmq.create('mcp_operations');

-- Git Operations Queue (async git commands)
SELECT pgmq.create('git_operations');

-- Workflow Execution Queue (n8n triggers)
SELECT pgmq.create('workflow_executions');

-- Notification Queue (Mattermost, email)
SELECT pgmq.create('notifications');

-- Sync Events Queue (realtime sync)
SELECT pgmq.create('sync_events');

-- ============================================================================
-- QUEUE HELPER FUNCTIONS
-- ============================================================================

-- Send message to queue with retry logic
CREATE OR REPLACE FUNCTION queue_send(
    p_queue_name TEXT,
    p_payload JSONB,
    p_delay_seconds INTEGER DEFAULT 0
) RETURNS BIGINT AS $$
DECLARE
    v_msg_id BIGINT;
BEGIN
    SELECT pgmq.send(
        queue_name := p_queue_name,
        msg := p_payload,
        delay := p_delay_seconds
    ) INTO v_msg_id;

    RETURN v_msg_id;
END;
$$ LANGUAGE plpgsql;

-- Read and process messages (for workers)
CREATE OR REPLACE FUNCTION queue_read(
    p_queue_name TEXT,
    p_batch_size INTEGER DEFAULT 10,
    p_visibility_timeout INTEGER DEFAULT 30
) RETURNS TABLE(
    msg_id BIGINT,
    payload JSONB,
    enqueued_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (m).msg_id,
        (m).message,
        (m).enqueued_at
    FROM pgmq.read(
        queue_name := p_queue_name,
        vt := p_visibility_timeout,
        qty := p_batch_size
    ) m;
END;
$$ LANGUAGE plpgsql;

-- Acknowledge processed message
CREATE OR REPLACE FUNCTION queue_ack(
    p_queue_name TEXT,
    p_msg_id BIGINT
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN pgmq.delete(p_queue_name, p_msg_id);
END;
$$ LANGUAGE plpgsql;

-- Archive failed message for debugging
CREATE OR REPLACE FUNCTION queue_archive(
    p_queue_name TEXT,
    p_msg_id BIGINT
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN pgmq.archive(p_queue_name, p_msg_id);
END;
$$ LANGUAGE plpgsql;

-- Get queue statistics
CREATE OR REPLACE FUNCTION queue_stats(p_queue_name TEXT DEFAULT NULL)
RETURNS TABLE(
    queue_name TEXT,
    queue_length BIGINT,
    total_messages BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.queue_name::TEXT,
        m.queue_length,
        m.total_messages
    FROM pgmq.metrics_all() m
    WHERE p_queue_name IS NULL OR m.queue_name = p_queue_name;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- QUEUE TRIGGERS FOR AUTOMATIC ROUTING
-- ============================================================================

-- Automatically queue MCP jobs when inserted
CREATE OR REPLACE FUNCTION trigger_queue_mcp_job()
RETURNS TRIGGER AS $$
BEGIN
    -- Only queue if status is 'pending' and priority is 'low'
    IF NEW.status = 'pending' AND NEW.priority = 'low' THEN
        PERFORM queue_send(
            'mcp_operations',
            jsonb_build_object(
                'job_id', NEW.id,
                'request_id', NEW.request_id,
                'action', NEW.action,
                'payload', NEW.payload,
                'client_id', NEW.client_id
            )
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_queue_mcp_job
    AFTER INSERT ON mcp_job_queue
    FOR EACH ROW
    EXECUTE FUNCTION trigger_queue_mcp_job();

-- ============================================================================
-- GITHUB TABLES (for GitHub App integration)
-- ============================================================================

CREATE TABLE IF NOT EXISTS github_installations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    installation_id TEXT NOT NULL UNIQUE,
    account_login TEXT NOT NULL,
    account_type TEXT NOT NULL,
    target_type TEXT,
    repository_selection TEXT,
    permissions JSONB DEFAULT '{}',
    events TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_github_installations_account ON github_installations(account_login);

CREATE TABLE IF NOT EXISTS github_installation_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    installation_id TEXT NOT NULL UNIQUE REFERENCES github_installations(installation_id),
    token TEXT NOT NULL, -- Should be encrypted via Vault
    expires_at TIMESTAMPTZ NOT NULL,
    permissions JSONB DEFAULT '{}',
    repository_selection TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_github_tokens_expiry ON github_installation_tokens(expires_at);

CREATE TABLE IF NOT EXISTS github_oauth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    github_user_id TEXT NOT NULL UNIQUE,
    github_username TEXT NOT NULL,
    access_token TEXT NOT NULL, -- Should be encrypted via Vault
    token_type TEXT DEFAULT 'bearer',
    scope TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_github_oauth_username ON github_oauth_tokens(github_username);

CREATE TABLE IF NOT EXISTS github_webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_id TEXT NOT NULL UNIQUE,
    event_type TEXT NOT NULL,
    action TEXT,
    repository TEXT,
    sender TEXT,
    payload JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_github_webhooks_event ON github_webhook_events(event_type, received_at DESC);
CREATE INDEX idx_github_webhooks_repo ON github_webhook_events(repository, received_at DESC);
CREATE INDEX idx_github_webhooks_unprocessed ON github_webhook_events(processed) WHERE processed = FALSE;

-- RLS for GitHub tables
ALTER TABLE github_installations ENABLE ROW LEVEL SECURITY;
ALTER TABLE github_installation_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE github_oauth_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE github_webhook_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access" ON github_installations FOR ALL TO service_role USING (TRUE);
CREATE POLICY "Service role full access" ON github_installation_tokens FOR ALL TO service_role USING (TRUE);
CREATE POLICY "Service role full access" ON github_oauth_tokens FOR ALL TO service_role USING (TRUE);
CREATE POLICY "Service role full access" ON github_webhook_events FOR ALL TO service_role USING (TRUE);

-- ============================================================================
-- QUEUE WORKERS TABLE (for distributed processing)
-- ============================================================================

CREATE TABLE IF NOT EXISTS queue_workers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worker_id TEXT NOT NULL UNIQUE,
    queues TEXT[] NOT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'stopped')),
    last_heartbeat TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    messages_processed BIGINT DEFAULT 0,
    errors_count BIGINT DEFAULT 0,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_queue_workers_status ON queue_workers(status);
CREATE INDEX idx_queue_workers_heartbeat ON queue_workers(last_heartbeat);

-- Cleanup stale workers (no heartbeat in 5 minutes)
CREATE OR REPLACE FUNCTION cleanup_stale_workers()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    DELETE FROM queue_workers
    WHERE last_heartbeat < NOW() - INTERVAL '5 minutes'
    RETURNING * INTO v_count;

    RETURN COALESCE(v_count, 0);
END;
$$ LANGUAGE plpgsql;
