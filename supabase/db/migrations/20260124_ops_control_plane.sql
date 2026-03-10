-- Control Plane Extension for Observability Schema
-- Adds operational views and helper functions for n8n/Supabase control plane pattern
--
-- @see db/migrations/20260121_observability_schema.sql (base schema)

-- ============ OPS Schema Alias ============
-- For backward compatibility with ops.events pattern
CREATE SCHEMA IF NOT EXISTS ops;

-- View: ops.events (alias to observability.jobs with event-like interface)
CREATE OR REPLACE VIEW ops.events AS
SELECT
    j.id,
    j.created_at,
    j.source,
    j.job_type AS event_type,
    (j.context->>'correlation_id')::TEXT AS correlation_id,
    j.payload,
    CASE j.status
        WHEN 'queued' THEN 'received'
        WHEN 'processing' THEN 'processing'
        WHEN 'completed' THEN 'ok'
        WHEN 'failed' THEN 'error'
        WHEN 'dead_letter' THEN 'error'
        ELSE j.status
    END AS status,
    CASE
        WHEN j.status IN ('failed', 'dead_letter')
        THEN (SELECT je.payload->>'error' FROM observability.job_events je
              WHERE je.job_id = j.id AND je.event_type = 'failed'
              ORDER BY je.timestamp DESC LIMIT 1)
        ELSE NULL
    END AS error
FROM observability.jobs j
WHERE j.deleted_at IS NULL;

COMMENT ON VIEW ops.events IS 'Backward-compatible view exposing jobs as events for n8n integration';

-- ============ Control Plane Functions ============

-- Record an event (thin wrapper for enqueue_job)
CREATE OR REPLACE FUNCTION ops.record_event(
    p_source TEXT,
    p_event_type TEXT,
    p_payload JSONB,
    p_correlation_id TEXT DEFAULT NULL
) RETURNS UUID AS $$
BEGIN
    RETURN observability.enqueue_job(
        p_source,
        p_event_type,
        p_payload,
        CASE WHEN p_correlation_id IS NOT NULL
             THEN jsonb_build_object('correlation_id', p_correlation_id)
             ELSE NULL
        END,
        5,  -- default priority
        NOW()
    );
END;
$$ LANGUAGE plpgsql;

-- Get correlation trace (all events in a chain)
CREATE OR REPLACE FUNCTION ops.get_trace(
    p_correlation_id TEXT
) RETURNS TABLE (
    id UUID,
    created_at TIMESTAMPTZ,
    source TEXT,
    event_type TEXT,
    status TEXT,
    duration_ms INTEGER,
    error TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        j.id,
        j.created_at,
        j.source,
        j.job_type,
        j.status,
        CASE WHEN j.completed_at IS NOT NULL
             THEN EXTRACT(EPOCH FROM (j.completed_at - j.created_at))::INTEGER * 1000
             ELSE NULL
        END,
        CASE WHEN j.status IN ('failed', 'dead_letter')
             THEN (SELECT je.payload->>'message' FROM observability.job_events je
                   WHERE je.job_id = j.id AND je.event_type IN ('failed', 'dead_letter')
                   ORDER BY je.timestamp DESC LIMIT 1)
             ELSE NULL
        END
    FROM observability.jobs j
    WHERE j.context->>'correlation_id' = p_correlation_id
       OR j.id::TEXT = p_correlation_id
    ORDER BY j.created_at ASC;
END;
$$ LANGUAGE plpgsql;

-- Get queue depth by source
CREATE OR REPLACE FUNCTION ops.get_queue_depth()
RETURNS TABLE (
    source TEXT,
    job_type TEXT,
    queued BIGINT,
    processing BIGINT,
    failed_24h BIGINT,
    dlq_unresolved BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH queue_stats AS (
        SELECT
            j.source,
            j.job_type,
            COUNT(*) FILTER (WHERE j.status = 'queued') as queued,
            COUNT(*) FILTER (WHERE j.status = 'processing') as processing,
            COUNT(*) FILTER (WHERE j.status IN ('failed', 'dead_letter')
                            AND j.created_at > NOW() - INTERVAL '24 hours') as failed_24h
        FROM observability.jobs j
        WHERE j.deleted_at IS NULL
        GROUP BY j.source, j.job_type
    ),
    dlq_stats AS (
        SELECT
            j.source,
            j.job_type,
            COUNT(*) as dlq_count
        FROM observability.dead_letter dl
        JOIN observability.jobs j ON dl.job_id = j.id
        WHERE NOT dl.resolved
        GROUP BY j.source, j.job_type
    )
    SELECT
        qs.source,
        qs.job_type,
        qs.queued,
        qs.processing,
        qs.failed_24h,
        COALESCE(ds.dlq_count, 0)
    FROM queue_stats qs
    LEFT JOIN dlq_stats ds ON qs.source = ds.source AND qs.job_type = ds.job_type
    ORDER BY qs.queued + qs.processing DESC;
END;
$$ LANGUAGE plpgsql;

-- ============ n8n Integration Views ============

-- View: Pending jobs for n8n polling
CREATE OR REPLACE VIEW ops.pending_jobs AS
SELECT
    j.id,
    j.source,
    j.job_type,
    j.payload,
    j.context,
    j.priority,
    j.retry_count,
    j.created_at,
    EXTRACT(EPOCH FROM (NOW() - j.created_at))::INTEGER as age_seconds
FROM observability.jobs j
WHERE j.status = 'queued'
  AND j.deleted_at IS NULL
  AND (j.scheduled_at IS NULL OR j.scheduled_at <= NOW())
ORDER BY j.priority DESC, j.created_at ASC;

-- View: Active jobs (being processed)
CREATE OR REPLACE VIEW ops.active_jobs AS
SELECT
    j.id,
    j.source,
    j.job_type,
    j.claimed_by AS worker,
    j.claimed_at,
    EXTRACT(EPOCH FROM (NOW() - j.claimed_at))::INTEGER as runtime_seconds,
    j.retry_count
FROM observability.jobs j
WHERE j.status = 'processing'
  AND j.deleted_at IS NULL
ORDER BY j.claimed_at ASC;

-- View: Dead letter queue for manual resolution
CREATE OR REPLACE VIEW ops.dlq AS
SELECT
    dl.id AS dlq_id,
    j.id AS job_id,
    j.source,
    j.job_type,
    dl.reason,
    dl.last_error,
    dl.retry_count,
    dl.moved_at,
    j.payload,
    j.context
FROM observability.dead_letter dl
JOIN observability.jobs j ON dl.job_id = j.id
WHERE NOT dl.resolved
ORDER BY dl.moved_at DESC;

-- ============ Grants ============
GRANT USAGE ON SCHEMA ops TO service_role, authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA ops TO service_role, authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ops TO service_role, authenticated;

-- Service role can insert/update via functions
GRANT INSERT, UPDATE ON ops.events TO service_role;

COMMENT ON SCHEMA ops IS 'Operational control plane views and functions for n8n integration';
