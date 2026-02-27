-- =============================================================================
-- Migration: ops schema for LLM observability (Odoo → Supabase bridge)
-- Owner: Supabase (SSOT for orchestration / observability)
-- Source: Odoo SOR via ipai_llm_supabase_bridge webhook
-- =============================================================================

-- Schema
CREATE SCHEMA IF NOT EXISTS ops;

-- Enum types
DO $$ BEGIN
    CREATE TYPE ops.run_status AS ENUM (
        'pending', 'running', 'completed', 'failed', 'cancelled'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE ops.event_source AS ENUM (
        'odoo', 'supabase', 'n8n', 'manual'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- =============================================================================
-- ops.runs — Top-level execution tracking (threads, sync jobs, etc.)
-- =============================================================================
CREATE TABLE IF NOT EXISTS ops.runs (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    run_type        text NOT NULL,              -- 'llm_thread', 'sync_job', 'generation', etc.
    status          ops.run_status NOT NULL DEFAULT 'pending',
    source          ops.event_source NOT NULL DEFAULT 'odoo',

    -- Odoo linkage
    odoo_db         text,
    odoo_model      text,
    odoo_id         bigint,

    -- Metadata
    started_at      timestamptz DEFAULT now(),
    completed_at    timestamptz,
    duration_ms     integer GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (completed_at - started_at)) * 1000
    ) STORED,
    metadata        jsonb DEFAULT '{}',

    -- Audit
    created_by      uuid REFERENCES auth.users(id),
    created_at      timestamptz DEFAULT now(),
    updated_at      timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_runs_status ON ops.runs (status);
CREATE INDEX IF NOT EXISTS idx_runs_type ON ops.runs (run_type);
CREATE INDEX IF NOT EXISTS idx_runs_odoo ON ops.runs (odoo_db, odoo_model, odoo_id);
CREATE INDEX IF NOT EXISTS idx_runs_created ON ops.runs (created_at DESC);

-- =============================================================================
-- ops.run_events — Append-only event stream (immutable audit trail)
-- =============================================================================
CREATE TABLE IF NOT EXISTS ops.run_events (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          uuid REFERENCES ops.runs(id) ON DELETE CASCADE,

    event_type      text NOT NULL,              -- 'tool.call', 'tool.result', 'thread.create', etc.
    idempotency_key text UNIQUE,                -- Prevents duplicate ingestion
    source          ops.event_source NOT NULL DEFAULT 'odoo',

    -- Odoo linkage
    odoo_db         text,
    odoo_model      text,
    odoo_id         bigint,
    odoo_event_id   bigint,                     -- ipai.bridge.event.id

    -- Event data
    payload         jsonb NOT NULL DEFAULT '{}',
    timestamp       timestamptz NOT NULL DEFAULT now(),

    -- Audit
    ingested_at     timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_run_events_run ON ops.run_events (run_id);
CREATE INDEX IF NOT EXISTS idx_run_events_type ON ops.run_events (event_type);
CREATE INDEX IF NOT EXISTS idx_run_events_ts ON ops.run_events (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_run_events_odoo ON ops.run_events (odoo_db, odoo_model, odoo_id);

-- =============================================================================
-- ops.artifacts — Output references (reports, exports, Storage pointers)
-- =============================================================================
CREATE TABLE IF NOT EXISTS ops.artifacts (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          uuid REFERENCES ops.runs(id) ON DELETE SET NULL,
    artifact_type   text NOT NULL,              -- 'json', 'pdf', 'csv', 'storage_ref'
    name            text,
    content         jsonb,                      -- Inline JSON or storage metadata
    storage_path    text,                       -- Supabase Storage path if applicable
    created_at      timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_artifacts_run ON ops.artifacts (run_id);

-- =============================================================================
-- RLS Policies
-- =============================================================================
ALTER TABLE ops.runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.run_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.artifacts ENABLE ROW LEVEL SECURITY;

-- Service role (Edge Functions) can do everything
CREATE POLICY "service_role_all" ON ops.runs
    FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON ops.run_events
    FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON ops.artifacts
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Authenticated users can read their own runs (created_by = auth.uid())
CREATE POLICY "users_read_own_runs" ON ops.runs
    FOR SELECT TO authenticated
    USING (created_by = auth.uid() OR created_by IS NULL);

CREATE POLICY "users_read_own_events" ON ops.run_events
    FOR SELECT TO authenticated
    USING (
        run_id IN (SELECT id FROM ops.runs WHERE created_by = auth.uid() OR created_by IS NULL)
    );

CREATE POLICY "users_read_own_artifacts" ON ops.artifacts
    FOR SELECT TO authenticated
    USING (
        run_id IN (SELECT id FROM ops.runs WHERE created_by = auth.uid() OR created_by IS NULL)
    );

-- =============================================================================
-- Helper function: upsert event with idempotency
-- =============================================================================
CREATE OR REPLACE FUNCTION ops.ingest_bridge_event(
    p_event_type text,
    p_idempotency_key text,
    p_odoo_db text,
    p_odoo_model text,
    p_odoo_id bigint,
    p_odoo_event_id bigint,
    p_payload jsonb,
    p_timestamp timestamptz DEFAULT now()
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_event_id uuid;
    v_run_id uuid;
BEGIN
    -- Idempotency check
    SELECT id INTO v_event_id
    FROM ops.run_events
    WHERE idempotency_key = p_idempotency_key;

    IF v_event_id IS NOT NULL THEN
        RETURN v_event_id;  -- Already ingested
    END IF;

    -- Auto-create or find run for thread-scoped events
    IF p_event_type IN ('thread.create', 'generation.start', 'generation.complete') THEN
        SELECT id INTO v_run_id
        FROM ops.runs
        WHERE odoo_db = p_odoo_db
          AND odoo_model = p_odoo_model
          AND odoo_id = p_odoo_id
          AND status IN ('pending', 'running')
        ORDER BY created_at DESC
        LIMIT 1;

        IF v_run_id IS NULL THEN
            INSERT INTO ops.runs (run_type, status, source, odoo_db, odoo_model, odoo_id)
            VALUES ('llm_thread', 'running', 'odoo', p_odoo_db, p_odoo_model, p_odoo_id)
            RETURNING id INTO v_run_id;
        END IF;

        -- Mark complete if generation.complete
        IF p_event_type = 'generation.complete' THEN
            UPDATE ops.runs
            SET status = 'completed', completed_at = p_timestamp, updated_at = now()
            WHERE id = v_run_id;
        END IF;
    END IF;

    -- Insert the event
    INSERT INTO ops.run_events (
        run_id, event_type, idempotency_key, source,
        odoo_db, odoo_model, odoo_id, odoo_event_id,
        payload, timestamp
    ) VALUES (
        v_run_id, p_event_type, p_idempotency_key, 'odoo',
        p_odoo_db, p_odoo_model, p_odoo_id, p_odoo_event_id,
        p_payload, p_timestamp
    )
    RETURNING id INTO v_event_id;

    RETURN v_event_id;
END;
$$;

-- Grant execute to service_role (Edge Functions)
GRANT USAGE ON SCHEMA ops TO service_role;
GRANT ALL ON ALL TABLES IN SCHEMA ops TO service_role;
GRANT EXECUTE ON FUNCTION ops.ingest_bridge_event TO service_role;

-- Grant read to authenticated
GRANT USAGE ON SCHEMA ops TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA ops TO authenticated;
