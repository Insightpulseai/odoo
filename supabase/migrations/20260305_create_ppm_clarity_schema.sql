-- PPM Clarity: Plane.so + Odoo Integration - SSOT Schema
-- Created: 2026-03-05
-- Purpose: Bidirectional ID mapping and append-only event ledger for Plane<>Odoo sync

-- Ensure ops schema exists
CREATE SCHEMA IF NOT EXISTS ops;

-- =============================================================================
-- TABLE: ops.work_item_links
-- Bidirectional ID mapping between Plane issues and Odoo tasks
-- =============================================================================

CREATE TABLE IF NOT EXISTS ops.work_item_links (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Plane identifiers (immutable)
    plane_project_id text NOT NULL,
    plane_issue_id text NOT NULL,

    -- Odoo identifiers (immutable after first sync)
    odoo_project_id integer,
    odoo_task_id integer,

    -- Sync state tracking
    sync_state text NOT NULL DEFAULT 'ok'
        CHECK (sync_state IN ('ok', 'needs_review', 'blocked')),

    -- Hash-based change detection
    last_plane_hash text,
    last_odoo_hash text,

    -- Timestamps
    last_synced_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),

    -- Uniqueness constraints
    UNIQUE (plane_project_id, plane_issue_id),
    UNIQUE (odoo_project_id, odoo_task_id)
);

CREATE INDEX IF NOT EXISTS idx_work_item_links_plane
    ON ops.work_item_links(plane_project_id, plane_issue_id);
CREATE INDEX IF NOT EXISTS idx_work_item_links_odoo
    ON ops.work_item_links(odoo_project_id, odoo_task_id);
CREATE INDEX IF NOT EXISTS idx_work_item_links_sync_state
    ON ops.work_item_links(sync_state) WHERE sync_state != 'ok';

ALTER TABLE ops.work_item_links ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role only" ON ops.work_item_links
    FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: ops.work_item_events
-- Append-only audit ledger for all sync operations
-- =============================================================================

CREATE TABLE IF NOT EXISTS ops.work_item_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    link_id uuid REFERENCES ops.work_item_links(id) ON DELETE SET NULL,

    event_type text NOT NULL CHECK (event_type IN (
        'plane_to_odoo', 'odoo_to_plane', 'reconciliation', 'conflict'
    )),

    source_system text NOT NULL CHECK (source_system IN ('plane', 'odoo', 'n8n')),

    event_data jsonb NOT NULL,

    idempotency_key text UNIQUE,

    success boolean NOT NULL,
    error_message text,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_work_item_events_link
    ON ops.work_item_events(link_id);
CREATE INDEX IF NOT EXISTS idx_work_item_events_type
    ON ops.work_item_events(event_type);
CREATE INDEX IF NOT EXISTS idx_work_item_events_created
    ON ops.work_item_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_work_item_events_idempotency
    ON ops.work_item_events(idempotency_key) WHERE idempotency_key IS NOT NULL;

ALTER TABLE ops.work_item_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role only" ON ops.work_item_events
    FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- RPC: upsert_work_item_link
-- =============================================================================

CREATE OR REPLACE FUNCTION ops.upsert_work_item_link(
    p_plane_project_id text,
    p_plane_issue_id text,
    p_odoo_project_id integer DEFAULT NULL,
    p_odoo_task_id integer DEFAULT NULL,
    p_sync_state text DEFAULT 'ok',
    p_last_plane_hash text DEFAULT NULL,
    p_last_odoo_hash text DEFAULT NULL
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ops, public
AS $$
DECLARE
    v_link_id uuid;
BEGIN
    IF p_sync_state NOT IN ('ok', 'needs_review', 'blocked') THEN
        RAISE EXCEPTION 'Invalid sync_state: %', p_sync_state;
    END IF;

    INSERT INTO ops.work_item_links (
        plane_project_id, plane_issue_id,
        odoo_project_id, odoo_task_id,
        sync_state, last_plane_hash, last_odoo_hash,
        last_synced_at, updated_at
    ) VALUES (
        p_plane_project_id, p_plane_issue_id,
        p_odoo_project_id, p_odoo_task_id,
        p_sync_state, p_last_plane_hash, p_last_odoo_hash,
        now(), now()
    )
    ON CONFLICT (plane_project_id, plane_issue_id)
    DO UPDATE SET
        odoo_project_id = COALESCE(EXCLUDED.odoo_project_id, ops.work_item_links.odoo_project_id),
        odoo_task_id = COALESCE(EXCLUDED.odoo_task_id, ops.work_item_links.odoo_task_id),
        sync_state = EXCLUDED.sync_state,
        last_plane_hash = COALESCE(EXCLUDED.last_plane_hash, ops.work_item_links.last_plane_hash),
        last_odoo_hash = COALESCE(EXCLUDED.last_odoo_hash, ops.work_item_links.last_odoo_hash),
        last_synced_at = EXCLUDED.last_synced_at,
        updated_at = now()
    RETURNING id INTO v_link_id;

    RETURN v_link_id;
END;
$$;

REVOKE ALL ON FUNCTION ops.upsert_work_item_link FROM PUBLIC;
GRANT EXECUTE ON FUNCTION ops.upsert_work_item_link TO service_role;

-- =============================================================================
-- RPC: append_work_item_event
-- =============================================================================

CREATE OR REPLACE FUNCTION ops.append_work_item_event(
    p_link_id uuid,
    p_event_type text,
    p_source_system text,
    p_event_data jsonb,
    p_idempotency_key text DEFAULT NULL,
    p_success boolean DEFAULT true,
    p_error_message text DEFAULT NULL
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ops, public
AS $$
DECLARE
    v_event_id uuid;
    v_existing_event_id uuid;
BEGIN
    IF p_event_type NOT IN ('plane_to_odoo', 'odoo_to_plane', 'reconciliation', 'conflict') THEN
        RAISE EXCEPTION 'Invalid event_type: %', p_event_type;
    END IF;

    IF p_source_system NOT IN ('plane', 'odoo', 'n8n') THEN
        RAISE EXCEPTION 'Invalid source_system: %', p_source_system;
    END IF;

    -- Idempotency check
    IF p_idempotency_key IS NOT NULL THEN
        SELECT id INTO v_existing_event_id
        FROM ops.work_item_events
        WHERE idempotency_key = p_idempotency_key;

        IF v_existing_event_id IS NOT NULL THEN
            RETURN v_existing_event_id;
        END IF;
    END IF;

    INSERT INTO ops.work_item_events (
        link_id, event_type, source_system,
        event_data, idempotency_key,
        success, error_message
    ) VALUES (
        p_link_id, p_event_type, p_source_system,
        p_event_data, p_idempotency_key,
        p_success, p_error_message
    )
    RETURNING id INTO v_event_id;

    RETURN v_event_id;
END;
$$;

REVOKE ALL ON FUNCTION ops.append_work_item_event FROM PUBLIC;
GRANT EXECUTE ON FUNCTION ops.append_work_item_event TO service_role;

-- =============================================================================
-- RPC: get_sync_conflicts
-- =============================================================================

CREATE OR REPLACE FUNCTION ops.get_sync_conflicts(
    p_limit integer DEFAULT 100
)
RETURNS TABLE (
    link_id uuid,
    plane_project_id text,
    plane_issue_id text,
    odoo_project_id integer,
    odoo_task_id integer,
    sync_state text,
    last_plane_hash text,
    last_odoo_hash text,
    last_synced_at timestamptz,
    recent_events jsonb
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ops, public
AS $$
BEGIN
    RETURN QUERY
    SELECT
        wil.id AS link_id,
        wil.plane_project_id,
        wil.plane_issue_id,
        wil.odoo_project_id,
        wil.odoo_task_id,
        wil.sync_state,
        wil.last_plane_hash,
        wil.last_odoo_hash,
        wil.last_synced_at,
        (
            SELECT jsonb_agg(
                jsonb_build_object(
                    'event_id', wie.id,
                    'event_type', wie.event_type,
                    'source_system', wie.source_system,
                    'success', wie.success,
                    'error_message', wie.error_message,
                    'created_at', wie.created_at
                ) ORDER BY wie.created_at DESC
            )
            FROM (
                SELECT *
                FROM ops.work_item_events sub
                WHERE sub.link_id = wil.id
                ORDER BY sub.created_at DESC
                LIMIT 10
            ) wie
        ) AS recent_events
    FROM ops.work_item_links wil
    WHERE wil.sync_state IN ('needs_review', 'blocked')
    ORDER BY wil.updated_at DESC
    LIMIT p_limit;
END;
$$;

REVOKE ALL ON FUNCTION ops.get_sync_conflicts FROM PUBLIC;
GRANT EXECUTE ON FUNCTION ops.get_sync_conflicts TO service_role;

-- =============================================================================
-- Table and column comments
-- =============================================================================

COMMENT ON TABLE ops.work_item_links IS
    'PPM Clarity: Bidirectional ID mapping between Plane.so issues and Odoo project tasks.';
COMMENT ON TABLE ops.work_item_events IS
    'PPM Clarity: Append-only audit ledger for all sync operations.';

COMMENT ON COLUMN ops.work_item_links.sync_state IS
    'ok = normal, needs_review = conflict detected, blocked = manual intervention required';
COMMENT ON COLUMN ops.work_item_links.last_plane_hash IS
    'SHA-256 of Plane-owned fields (title, description, priority, labels, cycle, state)';
COMMENT ON COLUMN ops.work_item_links.last_odoo_hash IS
    'SHA-256 of Odoo-owned fields (assigned users, timesheets, costs, attachments)';
COMMENT ON COLUMN ops.work_item_events.idempotency_key IS
    'Format: {source}:{event_type}:{entity_id}:{timestamp}. UNIQUE prevents duplicate processing.';
