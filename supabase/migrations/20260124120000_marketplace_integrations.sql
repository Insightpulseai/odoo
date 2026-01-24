-- Migration: Marketplace Integrations Schema
-- Description: Control plane for Google Workspace, Supabase, and external marketplace integrations
-- Author: Claude Agent
-- Date: 2026-01-24

-- ============================================================================
-- SCHEMA: marketplace
-- Purpose: Centralized integration management for external marketplaces
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS marketplace;

COMMENT ON SCHEMA marketplace IS 'Control plane for marketplace integrations (Google Workspace, Supabase, external APIs)';

-- ============================================================================
-- TABLE: marketplace.integrations
-- Purpose: Registry of configured integrations
-- ============================================================================

CREATE TABLE IF NOT EXISTS marketplace.integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,  -- 'google_workspace', 'supabase', 'github', 's3', 'slack', 'notion'
    category TEXT NOT NULL,  -- 'content', 'storage', 'automation', 'communication', 'analytics'
    config JSONB NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'disabled', 'error')),
    health_status TEXT DEFAULT 'unknown' CHECK (health_status IN ('healthy', 'degraded', 'unhealthy', 'unknown')),
    last_health_check TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID,
    CONSTRAINT valid_provider CHECK (provider IN (
        'google_workspace', 'google_drive', 'google_docs', 'google_sheets', 'gmail',
        'supabase', 'github', 'aws_s3', 'cloudflare_r2', 'slack', 'notion',
        'n8n', 'mattermost', 'figma', 'vercel', 'digitalocean'
    ))
);

CREATE INDEX IF NOT EXISTS idx_integrations_provider ON marketplace.integrations(provider);
CREATE INDEX IF NOT EXISTS idx_integrations_status ON marketplace.integrations(status);
CREATE INDEX IF NOT EXISTS idx_integrations_category ON marketplace.integrations(category);

COMMENT ON TABLE marketplace.integrations IS 'Registry of configured marketplace integrations';
COMMENT ON COLUMN marketplace.integrations.slug IS 'URL-safe unique identifier';
COMMENT ON COLUMN marketplace.integrations.provider IS 'External service provider';
COMMENT ON COLUMN marketplace.integrations.config IS 'Provider-specific configuration (non-sensitive)';

-- ============================================================================
-- TABLE: marketplace.oauth_tokens
-- Purpose: Secure storage for OAuth credentials (references Vault for encryption)
-- ============================================================================

CREATE TABLE IF NOT EXISTS marketplace.oauth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID NOT NULL REFERENCES marketplace.integrations(id) ON DELETE CASCADE,
    user_id UUID,  -- NULL for service accounts
    token_type TEXT NOT NULL DEFAULT 'bearer',
    -- Actual tokens stored in Vault, these are references
    access_token_vault_id TEXT,  -- Vault secret ID
    refresh_token_vault_id TEXT, -- Vault secret ID
    scopes TEXT[] NOT NULL DEFAULT '{}',
    expires_at TIMESTAMPTZ,
    refresh_expires_at TIMESTAMPTZ,
    last_refreshed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (integration_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_oauth_tokens_integration ON marketplace.oauth_tokens(integration_id);
CREATE INDEX IF NOT EXISTS idx_oauth_tokens_user ON marketplace.oauth_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_oauth_tokens_expires ON marketplace.oauth_tokens(expires_at);

COMMENT ON TABLE marketplace.oauth_tokens IS 'OAuth token references (actual tokens in Vault)';
COMMENT ON COLUMN marketplace.oauth_tokens.access_token_vault_id IS 'Reference to Vault secret for access token';
COMMENT ON COLUMN marketplace.oauth_tokens.refresh_token_vault_id IS 'Reference to Vault secret for refresh token';

-- ============================================================================
-- TABLE: marketplace.webhook_events
-- Purpose: Incoming webhook event log from external services
-- ============================================================================

CREATE TABLE IF NOT EXISTS marketplace.webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID REFERENCES marketplace.integrations(id) ON DELETE SET NULL,
    source TEXT NOT NULL,  -- Provider name
    event_type TEXT NOT NULL,
    event_id TEXT,  -- External event ID for deduplication
    payload JSONB NOT NULL DEFAULT '{}',
    headers JSONB DEFAULT '{}',
    signature TEXT,  -- Webhook signature for verification
    verified BOOLEAN DEFAULT FALSE,
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    processed_at TIMESTAMPTZ,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (source, event_id)
);

CREATE INDEX IF NOT EXISTS idx_webhook_events_source ON marketplace.webhook_events(source);
CREATE INDEX IF NOT EXISTS idx_webhook_events_event_type ON marketplace.webhook_events(event_type);
CREATE INDEX IF NOT EXISTS idx_webhook_events_processed ON marketplace.webhook_events(processed) WHERE NOT processed;
CREATE INDEX IF NOT EXISTS idx_webhook_events_created ON marketplace.webhook_events(created_at);

COMMENT ON TABLE marketplace.webhook_events IS 'Incoming webhook events from external services';
COMMENT ON COLUMN marketplace.webhook_events.event_id IS 'External event ID for deduplication';
COMMENT ON COLUMN marketplace.webhook_events.verified IS 'Whether webhook signature was verified';

-- ============================================================================
-- TABLE: marketplace.artifact_syncs
-- Purpose: Track artifact synchronization between services
-- ============================================================================

CREATE TABLE IF NOT EXISTS marketplace.artifact_syncs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_provider TEXT NOT NULL,
    source_path TEXT NOT NULL,
    source_ref TEXT,  -- commit SHA, workflow run ID, etc.
    destination_provider TEXT NOT NULL,
    destination_path TEXT NOT NULL,
    destination_ref TEXT,  -- Drive file ID, S3 object key, etc.
    artifact_type TEXT NOT NULL,  -- 'zip', 'pdf', 'json', 'markdown', 'image'
    artifact_name TEXT NOT NULL,
    size_bytes BIGINT,
    checksum TEXT,  -- SHA256 for integrity verification
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'syncing', 'completed', 'failed', 'skipped')),
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    triggered_by TEXT,  -- 'webhook', 'cron', 'manual', 'agent'
    job_run_id UUID,  -- Reference to ops.job_runs or mcp_jobs.job_runs
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    UNIQUE (source_provider, source_path, source_ref, destination_provider)
);

CREATE INDEX IF NOT EXISTS idx_artifact_syncs_source ON marketplace.artifact_syncs(source_provider, source_path);
CREATE INDEX IF NOT EXISTS idx_artifact_syncs_destination ON marketplace.artifact_syncs(destination_provider, destination_path);
CREATE INDEX IF NOT EXISTS idx_artifact_syncs_status ON marketplace.artifact_syncs(status);
CREATE INDEX IF NOT EXISTS idx_artifact_syncs_created ON marketplace.artifact_syncs(created_at);

COMMENT ON TABLE marketplace.artifact_syncs IS 'Track artifact synchronization between services';
COMMENT ON COLUMN marketplace.artifact_syncs.source_ref IS 'Source reference (commit SHA, run ID, etc.)';
COMMENT ON COLUMN marketplace.artifact_syncs.checksum IS 'SHA256 checksum for integrity verification';

-- ============================================================================
-- TABLE: marketplace.sync_rules
-- Purpose: Define automatic sync rules between services
-- ============================================================================

CREATE TABLE IF NOT EXISTS marketplace.sync_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    source_integration_id UUID REFERENCES marketplace.integrations(id) ON DELETE CASCADE,
    source_pattern TEXT NOT NULL,  -- Glob pattern or path prefix
    destination_integration_id UUID REFERENCES marketplace.integrations(id) ON DELETE CASCADE,
    destination_template TEXT NOT NULL,  -- Path template with variables
    artifact_types TEXT[] DEFAULT '{}',  -- Filter by artifact type
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    schedule_cron TEXT,  -- Optional cron for scheduled syncs
    on_webhook BOOLEAN NOT NULL DEFAULT TRUE,  -- Trigger on webhook events
    transform_config JSONB DEFAULT '{}',  -- Optional transformations
    priority INTEGER NOT NULL DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sync_rules_source ON marketplace.sync_rules(source_integration_id);
CREATE INDEX IF NOT EXISTS idx_sync_rules_destination ON marketplace.sync_rules(destination_integration_id);
CREATE INDEX IF NOT EXISTS idx_sync_rules_enabled ON marketplace.sync_rules(enabled) WHERE enabled;

COMMENT ON TABLE marketplace.sync_rules IS 'Automatic sync rules between services';
COMMENT ON COLUMN marketplace.sync_rules.source_pattern IS 'Glob pattern for matching source paths';
COMMENT ON COLUMN marketplace.sync_rules.destination_template IS 'Path template with variables like {date}, {name}';

-- ============================================================================
-- TABLE: marketplace.api_quotas
-- Purpose: Track API quota usage per integration
-- ============================================================================

CREATE TABLE IF NOT EXISTS marketplace.api_quotas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID NOT NULL REFERENCES marketplace.integrations(id) ON DELETE CASCADE,
    quota_type TEXT NOT NULL,  -- 'requests', 'bandwidth', 'storage'
    period TEXT NOT NULL DEFAULT 'daily' CHECK (period IN ('hourly', 'daily', 'monthly')),
    limit_value BIGINT NOT NULL,
    used_value BIGINT NOT NULL DEFAULT 0,
    reset_at TIMESTAMPTZ NOT NULL,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (integration_id, quota_type, period)
);

CREATE INDEX IF NOT EXISTS idx_api_quotas_integration ON marketplace.api_quotas(integration_id);
CREATE INDEX IF NOT EXISTS idx_api_quotas_reset ON marketplace.api_quotas(reset_at);

COMMENT ON TABLE marketplace.api_quotas IS 'Track API quota usage per integration';

-- ============================================================================
-- FUNCTIONS: Core operations
-- ============================================================================

-- Function: Register a new integration
CREATE OR REPLACE FUNCTION marketplace.register_integration(
    p_slug TEXT,
    p_name TEXT,
    p_provider TEXT,
    p_category TEXT,
    p_config JSONB DEFAULT '{}'
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO marketplace.integrations (slug, name, provider, category, config)
    VALUES (p_slug, p_name, p_provider, p_category, p_config)
    ON CONFLICT (slug) DO UPDATE SET
        name = EXCLUDED.name,
        config = marketplace.integrations.config || EXCLUDED.config,
        updated_at = NOW()
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Log a webhook event
CREATE OR REPLACE FUNCTION marketplace.log_webhook_event(
    p_source TEXT,
    p_event_type TEXT,
    p_event_id TEXT,
    p_payload JSONB,
    p_headers JSONB DEFAULT '{}',
    p_signature TEXT DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
    v_integration_id UUID;
BEGIN
    -- Find matching integration
    SELECT id INTO v_integration_id
    FROM marketplace.integrations
    WHERE provider = p_source AND status = 'active'
    LIMIT 1;

    -- Insert event (upsert on event_id)
    INSERT INTO marketplace.webhook_events (
        integration_id, source, event_type, event_id, payload, headers, signature
    )
    VALUES (v_integration_id, p_source, p_event_type, p_event_id, p_payload, p_headers, p_signature)
    ON CONFLICT (source, event_id) DO UPDATE SET
        payload = EXCLUDED.payload,
        headers = EXCLUDED.headers
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Mark webhook event as processed
CREATE OR REPLACE FUNCTION marketplace.mark_event_processed(
    p_event_id UUID,
    p_error_message TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    UPDATE marketplace.webhook_events
    SET
        processed = TRUE,
        processed_at = NOW(),
        error_message = p_error_message,
        retry_count = CASE WHEN p_error_message IS NOT NULL THEN retry_count + 1 ELSE retry_count END
    WHERE id = p_event_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Create artifact sync record
CREATE OR REPLACE FUNCTION marketplace.create_artifact_sync(
    p_source_provider TEXT,
    p_source_path TEXT,
    p_source_ref TEXT,
    p_destination_provider TEXT,
    p_destination_path TEXT,
    p_artifact_type TEXT,
    p_artifact_name TEXT,
    p_triggered_by TEXT DEFAULT 'webhook',
    p_metadata JSONB DEFAULT '{}'
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO marketplace.artifact_syncs (
        source_provider, source_path, source_ref,
        destination_provider, destination_path,
        artifact_type, artifact_name, triggered_by, metadata
    )
    VALUES (
        p_source_provider, p_source_path, p_source_ref,
        p_destination_provider, p_destination_path,
        p_artifact_type, p_artifact_name, p_triggered_by, p_metadata
    )
    ON CONFLICT (source_provider, source_path, source_ref, destination_provider) DO UPDATE SET
        status = 'pending',
        error_message = NULL,
        updated_at = NOW()
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Update artifact sync status
CREATE OR REPLACE FUNCTION marketplace.update_sync_status(
    p_sync_id UUID,
    p_status TEXT,
    p_destination_ref TEXT DEFAULT NULL,
    p_size_bytes BIGINT DEFAULT NULL,
    p_checksum TEXT DEFAULT NULL,
    p_error_message TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    UPDATE marketplace.artifact_syncs
    SET
        status = p_status,
        destination_ref = COALESCE(p_destination_ref, destination_ref),
        size_bytes = COALESCE(p_size_bytes, size_bytes),
        checksum = COALESCE(p_checksum, checksum),
        error_message = p_error_message,
        completed_at = CASE WHEN p_status IN ('completed', 'failed', 'skipped') THEN NOW() ELSE NULL END
    WHERE id = p_sync_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get pending webhook events for processing
CREATE OR REPLACE FUNCTION marketplace.get_pending_events(
    p_source TEXT DEFAULT NULL,
    p_limit INTEGER DEFAULT 10
) RETURNS TABLE (
    id UUID,
    integration_id UUID,
    source TEXT,
    event_type TEXT,
    payload JSONB,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        we.id,
        we.integration_id,
        we.source,
        we.event_type,
        we.payload,
        we.created_at
    FROM marketplace.webhook_events we
    WHERE NOT we.processed
      AND (p_source IS NULL OR we.source = p_source)
      AND we.retry_count < 5
    ORDER BY we.created_at ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get matching sync rules for a source event
CREATE OR REPLACE FUNCTION marketplace.get_matching_sync_rules(
    p_source_provider TEXT,
    p_source_path TEXT,
    p_artifact_type TEXT DEFAULT NULL
) RETURNS TABLE (
    id UUID,
    name TEXT,
    destination_integration_id UUID,
    destination_template TEXT,
    transform_config JSONB,
    priority INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        sr.id,
        sr.name,
        sr.destination_integration_id,
        sr.destination_template,
        sr.transform_config,
        sr.priority
    FROM marketplace.sync_rules sr
    JOIN marketplace.integrations si ON sr.source_integration_id = si.id
    WHERE si.provider = p_source_provider
      AND sr.enabled
      AND sr.on_webhook
      AND p_source_path LIKE REPLACE(REPLACE(sr.source_pattern, '*', '%'), '?', '_')
      AND (p_artifact_type IS NULL OR sr.artifact_types = '{}' OR p_artifact_type = ANY(sr.artifact_types))
    ORDER BY sr.priority DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- VIEWS: Monitoring and observability
-- ============================================================================

-- View: Integration health summary
CREATE OR REPLACE VIEW marketplace.v_integration_health AS
SELECT
    i.id,
    i.slug,
    i.name,
    i.provider,
    i.status,
    i.health_status,
    i.last_health_check,
    i.error_message,
    COALESCE(we.pending_events, 0) AS pending_events,
    COALESCE(we.failed_events_24h, 0) AS failed_events_24h,
    COALESCE(s.pending_syncs, 0) AS pending_syncs,
    COALESCE(s.failed_syncs_24h, 0) AS failed_syncs_24h
FROM marketplace.integrations i
LEFT JOIN LATERAL (
    SELECT
        COUNT(*) FILTER (WHERE NOT processed) AS pending_events,
        COUNT(*) FILTER (WHERE error_message IS NOT NULL AND created_at > NOW() - INTERVAL '24 hours') AS failed_events_24h
    FROM marketplace.webhook_events
    WHERE integration_id = i.id
) we ON TRUE
LEFT JOIN LATERAL (
    SELECT
        COUNT(*) FILTER (WHERE status = 'pending') AS pending_syncs,
        COUNT(*) FILTER (WHERE status = 'failed' AND created_at > NOW() - INTERVAL '24 hours') AS failed_syncs_24h
    FROM marketplace.artifact_syncs
    WHERE source_provider = i.provider OR destination_provider = i.provider
) s ON TRUE;

COMMENT ON VIEW marketplace.v_integration_health IS 'Integration health summary with event and sync metrics';

-- View: Recent sync activity
CREATE OR REPLACE VIEW marketplace.v_recent_syncs AS
SELECT
    s.id,
    s.source_provider,
    s.source_path,
    s.destination_provider,
    s.destination_path,
    s.artifact_type,
    s.artifact_name,
    s.status,
    s.size_bytes,
    s.triggered_by,
    s.created_at,
    s.completed_at,
    EXTRACT(EPOCH FROM (s.completed_at - s.created_at)) AS duration_seconds
FROM marketplace.artifact_syncs s
WHERE s.created_at > NOW() - INTERVAL '7 days'
ORDER BY s.created_at DESC;

COMMENT ON VIEW marketplace.v_recent_syncs IS 'Recent artifact sync activity (last 7 days)';

-- View: Quota status
CREATE OR REPLACE VIEW marketplace.v_quota_status AS
SELECT
    i.slug AS integration_slug,
    i.name AS integration_name,
    i.provider,
    q.quota_type,
    q.period,
    q.limit_value,
    q.used_value,
    ROUND((q.used_value::NUMERIC / NULLIF(q.limit_value, 0)) * 100, 2) AS usage_percent,
    q.reset_at,
    CASE
        WHEN q.used_value >= q.limit_value THEN 'exhausted'
        WHEN q.used_value >= q.limit_value * 0.9 THEN 'critical'
        WHEN q.used_value >= q.limit_value * 0.75 THEN 'warning'
        ELSE 'healthy'
    END AS quota_status
FROM marketplace.api_quotas q
JOIN marketplace.integrations i ON q.integration_id = i.id
ORDER BY usage_percent DESC;

COMMENT ON VIEW marketplace.v_quota_status IS 'API quota usage status per integration';

-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE marketplace.integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketplace.oauth_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketplace.webhook_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketplace.artifact_syncs ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketplace.sync_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketplace.api_quotas ENABLE ROW LEVEL SECURITY;

-- Service role: full access
CREATE POLICY "service_role_all" ON marketplace.integrations FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON marketplace.oauth_tokens FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON marketplace.webhook_events FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON marketplace.artifact_syncs FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON marketplace.sync_rules FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON marketplace.api_quotas FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Authenticated users: read-only on non-sensitive tables
CREATE POLICY "authenticated_read" ON marketplace.integrations FOR SELECT TO authenticated
    USING (status != 'disabled');
CREATE POLICY "authenticated_read" ON marketplace.webhook_events FOR SELECT TO authenticated
    USING (true);
CREATE POLICY "authenticated_read" ON marketplace.artifact_syncs FOR SELECT TO authenticated
    USING (true);
CREATE POLICY "authenticated_read" ON marketplace.sync_rules FOR SELECT TO authenticated
    USING (true);
CREATE POLICY "authenticated_read" ON marketplace.api_quotas FOR SELECT TO authenticated
    USING (true);

-- OAuth tokens: only service role (no authenticated access)
-- Already covered by service_role_all policy

-- ============================================================================
-- SEED DATA: Default integrations
-- ============================================================================

INSERT INTO marketplace.integrations (slug, name, provider, category, config)
VALUES
    ('github-actions', 'GitHub Actions', 'github', 'automation',
     '{"api_base": "https://api.github.com", "default_org": "Insightpulseai-net"}'::JSONB),
    ('google-drive', 'Google Drive', 'google_drive', 'storage',
     '{"api_base": "https://www.googleapis.com/drive/v3"}'::JSONB),
    ('aws-s3', 'AWS S3', 'aws_s3', 'storage',
     '{"region": "us-east-1"}'::JSONB),
    ('cloudflare-r2', 'Cloudflare R2', 'cloudflare_r2', 'storage',
     '{"account_id": ""}'::JSONB),
    ('n8n-automation', 'n8n Automation', 'n8n', 'automation',
     '{"webhook_base": ""}'::JSONB),
    ('slack-workspace', 'Slack Workspace', 'slack', 'communication',
     '{"api_base": "https://slack.com/api"}'::JSONB),
    ('notion-workspace', 'Notion Workspace', 'notion', 'content',
     '{"api_base": "https://api.notion.com/v1"}'::JSONB)
ON CONFLICT (slug) DO NOTHING;

-- Seed sync rules: GitHub artifacts to Drive/S3
INSERT INTO marketplace.sync_rules (name, description, source_integration_id, source_pattern, destination_integration_id, destination_template, artifact_types, priority)
SELECT
    'GitHub Artifacts to Drive',
    'Mirror GitHub Actions artifacts to Google Drive',
    (SELECT id FROM marketplace.integrations WHERE slug = 'github-actions'),
    'artifacts/*',
    (SELECT id FROM marketplace.integrations WHERE slug = 'google-drive'),
    'CI-Artifacts/{date}/{workflow}/{name}',
    ARRAY['zip', 'pdf', 'json'],
    5
WHERE EXISTS (SELECT 1 FROM marketplace.integrations WHERE slug = 'github-actions')
  AND EXISTS (SELECT 1 FROM marketplace.integrations WHERE slug = 'google-drive')
ON CONFLICT DO NOTHING;

INSERT INTO marketplace.sync_rules (name, description, source_integration_id, source_pattern, destination_integration_id, destination_template, artifact_types, priority)
SELECT
    'GitHub Artifacts to S3',
    'Mirror GitHub Actions artifacts to AWS S3',
    (SELECT id FROM marketplace.integrations WHERE slug = 'github-actions'),
    'artifacts/*',
    (SELECT id FROM marketplace.integrations WHERE slug = 'aws-s3'),
    'ci-artifacts/{date}/{workflow}/{name}',
    ARRAY['zip', 'pdf', 'json'],
    4
WHERE EXISTS (SELECT 1 FROM marketplace.integrations WHERE slug = 'github-actions')
  AND EXISTS (SELECT 1 FROM marketplace.integrations WHERE slug = 'aws-s3')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify tables created
DO $$
BEGIN
    ASSERT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'marketplace' AND table_name = 'integrations'),
        'Table marketplace.integrations not created';
    ASSERT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'marketplace' AND table_name = 'oauth_tokens'),
        'Table marketplace.oauth_tokens not created';
    ASSERT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'marketplace' AND table_name = 'webhook_events'),
        'Table marketplace.webhook_events not created';
    ASSERT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'marketplace' AND table_name = 'artifact_syncs'),
        'Table marketplace.artifact_syncs not created';
    ASSERT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'marketplace' AND table_name = 'sync_rules'),
        'Table marketplace.sync_rules not created';
    ASSERT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'marketplace' AND table_name = 'api_quotas'),
        'Table marketplace.api_quotas not created';

    RAISE NOTICE 'All marketplace tables created successfully';
END $$;

-- Verify functions created
DO $$
BEGIN
    ASSERT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'register_integration' AND pronamespace = 'marketplace'::regnamespace),
        'Function marketplace.register_integration not created';
    ASSERT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'log_webhook_event' AND pronamespace = 'marketplace'::regnamespace),
        'Function marketplace.log_webhook_event not created';
    ASSERT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'create_artifact_sync' AND pronamespace = 'marketplace'::regnamespace),
        'Function marketplace.create_artifact_sync not created';

    RAISE NOTICE 'All marketplace functions created successfully';
END $$;

-- Verify seed data
DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count FROM marketplace.integrations;
    ASSERT v_count >= 7, 'Expected at least 7 seed integrations, found ' || v_count;

    RAISE NOTICE 'Seed data verified: % integrations', v_count;
END $$;
