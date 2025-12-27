-- Migration: Database Webhooks Configuration
-- Automatically trigger n8n workflows on database changes

-- ============================================================================
-- WEBHOOK CONFIGURATION TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS database_webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    table_name TEXT NOT NULL,
    events TEXT[] NOT NULL DEFAULT ARRAY['INSERT', 'UPDATE', 'DELETE'],
    webhook_url TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    include_old_record BOOLEAN DEFAULT FALSE,
    include_new_record BOOLEAN DEFAULT TRUE,
    filter_columns TEXT[], -- Only trigger if these columns changed
    headers JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_webhooks_table ON database_webhooks(table_name);
CREATE INDEX idx_webhooks_enabled ON database_webhooks(enabled);

-- ============================================================================
-- WEBHOOK LOGS
-- ============================================================================

CREATE TABLE IF NOT EXISTS database_webhook_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID REFERENCES database_webhooks(id),
    table_name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    record_id TEXT,
    payload JSONB,
    response_code INTEGER,
    response_body TEXT,
    success BOOLEAN,
    duration_ms INTEGER,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_webhook_logs_webhook ON database_webhook_logs(webhook_id, created_at DESC);
CREATE INDEX idx_webhook_logs_success ON database_webhook_logs(success, created_at DESC);

-- Auto-cleanup old logs
CREATE INDEX idx_webhook_logs_cleanup ON database_webhook_logs(created_at)
    WHERE created_at < NOW() - INTERVAL '7 days';

-- ============================================================================
-- GITHUB-MATTERMOST MESSAGE LOG
-- ============================================================================

CREATE TABLE IF NOT EXISTS github_mattermost_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_id TEXT NOT NULL UNIQUE,
    event_type TEXT NOT NULL,
    action TEXT,
    repository TEXT,
    sender TEXT,
    channel TEXT NOT NULL,
    message_text TEXT,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_gh_mm_messages_repo ON github_mattermost_messages(repository, sent_at DESC);

-- ============================================================================
-- GENERIC WEBHOOK TRIGGER FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION trigger_database_webhook()
RETURNS TRIGGER AS $$
DECLARE
    v_webhook RECORD;
    v_payload JSONB;
    v_response RECORD;
    v_start_time TIMESTAMPTZ;
BEGIN
    v_start_time := clock_timestamp();

    -- Find matching webhooks
    FOR v_webhook IN
        SELECT * FROM database_webhooks
        WHERE table_name = TG_TABLE_NAME
          AND enabled = TRUE
          AND TG_OP = ANY(events)
    LOOP
        -- Build payload
        v_payload := jsonb_build_object(
            'event', TG_OP,
            'table', TG_TABLE_NAME,
            'schema', TG_TABLE_SCHEMA,
            'timestamp', NOW(),
            'webhook_id', v_webhook.id
        );

        IF v_webhook.include_new_record AND (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
            v_payload := v_payload || jsonb_build_object('new', row_to_json(NEW));
        END IF;

        IF v_webhook.include_old_record AND (TG_OP = 'UPDATE' OR TG_OP = 'DELETE') THEN
            v_payload := v_payload || jsonb_build_object('old', row_to_json(OLD));
        END IF;

        -- Queue the webhook call (async via pg_net)
        -- Note: This uses Supabase's pg_net extension
        PERFORM net.http_post(
            url := v_webhook.webhook_url,
            headers := v_webhook.headers || '{"Content-Type": "application/json"}'::jsonb,
            body := v_payload::text
        );

        -- Log the webhook
        INSERT INTO database_webhook_logs (
            webhook_id, table_name, event_type,
            record_id, payload, success
        ) VALUES (
            v_webhook.id, TG_TABLE_NAME, TG_OP,
            CASE
                WHEN TG_OP = 'DELETE' THEN (OLD.id)::TEXT
                ELSE (NEW.id)::TEXT
            END,
            v_payload,
            TRUE
        );
    END LOOP;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- SEED DEFAULT WEBHOOKS
-- ============================================================================

INSERT INTO database_webhooks (name, description, table_name, events, webhook_url) VALUES
(
    'mcp_job_completed',
    'Notify n8n when MCP job completes',
    'mcp_job_queue',
    ARRAY['UPDATE'],
    'https://n8n.insightpulseai.net/webhook/mcp-job-status'
),
(
    'github_webhook_received',
    'Process GitHub webhooks via n8n',
    'github_webhook_events',
    ARRAY['INSERT'],
    'https://n8n.insightpulseai.net/webhook/github-event'
),
(
    'cron_job_failed',
    'Alert on cron job failures',
    'cron_executions',
    ARRAY['INSERT', 'UPDATE'],
    'https://n8n.insightpulseai.net/webhook/cron-alert'
),
(
    'sync_event_broadcast',
    'Broadcast sync events to realtime',
    'sync_events',
    ARRAY['INSERT'],
    'https://n8n.insightpulseai.net/webhook/sync-broadcast'
)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- CREATE TRIGGERS FOR WATCHED TABLES
-- ============================================================================

-- MCP Job Queue changes
DROP TRIGGER IF EXISTS trg_webhook_mcp_job_queue ON mcp_job_queue;
CREATE TRIGGER trg_webhook_mcp_job_queue
    AFTER INSERT OR UPDATE ON mcp_job_queue
    FOR EACH ROW
    WHEN (NEW.status IN ('completed', 'failed'))
    EXECUTE FUNCTION trigger_database_webhook();

-- GitHub webhook events
DROP TRIGGER IF EXISTS trg_webhook_github_events ON github_webhook_events;
CREATE TRIGGER trg_webhook_github_events
    AFTER INSERT ON github_webhook_events
    FOR EACH ROW
    EXECUTE FUNCTION trigger_database_webhook();

-- Cron execution failures
DROP TRIGGER IF EXISTS trg_webhook_cron_failures ON cron_executions;
CREATE TRIGGER trg_webhook_cron_failures
    AFTER INSERT OR UPDATE ON cron_executions
    FOR EACH ROW
    WHEN (NEW.status = 'failed')
    EXECUTE FUNCTION trigger_database_webhook();

-- ============================================================================
-- VAULT INTEGRATION (Secret Management)
-- ============================================================================

-- Note: Supabase Vault stores secrets encrypted. Use these functions to
-- store and retrieve sensitive data like API keys and tokens.

-- Store a secret
CREATE OR REPLACE FUNCTION store_secret(
    p_name TEXT,
    p_secret TEXT,
    p_description TEXT DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO vault.secrets (name, secret, description)
    VALUES (p_name, p_secret, p_description)
    ON CONFLICT (name) DO UPDATE SET secret = EXCLUDED.secret
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Retrieve a secret (for use in functions only)
CREATE OR REPLACE FUNCTION get_secret(p_name TEXT)
RETURNS TEXT AS $$
DECLARE
    v_secret TEXT;
BEGIN
    SELECT decrypted_secret INTO v_secret
    FROM vault.decrypted_secrets
    WHERE name = p_name;

    RETURN v_secret;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- SEED SECRETS (Run manually with actual values)
-- ============================================================================

-- Example: Store GitHub App private key
-- SELECT store_secret('github_app_private_key', '-----BEGIN RSA PRIVATE KEY-----...', 'Pulser Hub GitHub App');
-- SELECT store_secret('github_client_secret', 'your_secret_here', 'Pulser Hub OAuth Secret');
-- SELECT store_secret('mattermost_webhook_url', 'https://mattermost.example.com/hooks/xxx', 'GitHub notifications');
-- SELECT store_secret('n8n_api_key', 'your_n8n_api_key', 'n8n API access');

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

ALTER TABLE database_webhooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE database_webhook_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE github_mattermost_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access" ON database_webhooks FOR ALL TO service_role USING (TRUE);
CREATE POLICY "Service role full access" ON database_webhook_logs FOR ALL TO service_role USING (TRUE);
CREATE POLICY "Service role full access" ON github_mattermost_messages FOR ALL TO service_role USING (TRUE);
