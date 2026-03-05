-- PPM Clarity: Plane.so + Odoo Integration - SSOT Schema
-- Created: 2026-03-05
-- Purpose: Bidirectional ID mapping and append-only event ledger for Plane↔Odoo sync

-- =============================================================================
-- SCHEMA: ops (existing schema for operational integrations)
-- =============================================================================

-- Ensure ops schema exists (should already exist from other migrations)
CREATE SCHEMA IF NOT EXISTS ops;

-- =============================================================================
-- TABLE: ops.work_item_links
-- Purpose: Bidirectional ID mapping between Plane issues and Odoo tasks
-- Governance: Immutable IDs, field ownership tracking via hashes
-- =============================================================================

CREATE TABLE IF NOT EXISTS ops.work_item_links (
    -- Primary key
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Plane identifiers (immutable)
    plane_project_id text NOT NULL,
    plane_issue_id text NOT NULL,

    -- Odoo identifiers (immutable after first sync)
    odoo_project_id integer,
    odoo_task_id integer,

    -- Sync state tracking
    sync_state text NOT NULL DEFAULT 'ok' CHECK (sync_state IN ('ok', 'needs_review', 'blocked')),

    -- Hash-based change detection (deterministic hashes of owned fields)
    last_plane_hash text,
    last_odoo_hash text,

    -- Timestamps
    last_synced_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),

    -- Uniqueness constraints (prevent duplicate mappings)
    UNIQUE (plane_project_id, plane_issue_id),
    UNIQUE (odoo_project_id, odoo_task_id)
);

-- Index for lookup performance
CREATE INDEX IF NOT EXISTS idx_work_item_links_plane ON ops.work_item_links(plane_project_id, plane_issue_id);
CREATE INDEX IF NOT EXISTS idx_work_item_links_odoo ON ops.work_item_links(odoo_project_id, odoo_task_id);
CREATE INDEX IF NOT EXISTS idx_work_item_links_sync_state ON ops.work_item_links(sync_state) WHERE sync_state != 'ok';

-- RLS: Only service_role can access (no direct user access to SSOT)
ALTER TABLE ops.work_item_links ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role only" ON ops.work_item_links FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: ops.work_item_events
-- Purpose: Append-only event ledger for 100% audit coverage
-- Governance: Idempotency via unique idempotency_key, immutable after insert
-- =============================================================================

CREATE TABLE IF NOT EXISTS ops.work_item_events (
    -- Primary key
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Link to work_item_links (nullable for orphaned events)
    link_id uuid REFERENCES ops.work_item_links(id) ON DELETE SET NULL,

    -- Event classification
    event_type text NOT NULL CHECK (event_type IN (
        'plane_to_odoo',    -- Plane commitment → Odoo task creation/update
        'odoo_to_plane',    -- Odoo completion → Plane state update
        'reconciliation',   -- Nightly drift repair
        'conflict'          -- Field ownership violation detected
    )),

    -- Event source
    source_system text NOT NULL CHECK (source_system IN ('plane', 'odoo', 'n8n')),

    -- Event payload (flexible JSONB for system-specific data)
    event_data jsonb NOT NULL,

    -- Idempotency enforcement (prevents duplicate processing)
    idempotency_key text UNIQUE,

    -- Execution result
    success boolean NOT NULL,
    error_message text,

    -- Timestamp (immutable)
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_work_item_events_link ON ops.work_item_events(link_id);
CREATE INDEX IF NOT EXISTS idx_work_item_events_type ON ops.work_item_events(event_type);
CREATE INDEX IF NOT EXISTS idx_work_item_events_source ON ops.work_item_events(source_system);
CREATE INDEX IF NOT EXISTS idx_work_item_events_created ON ops.work_item_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_work_item_events_idempotency ON ops.work_item_events(idempotency_key) WHERE idempotency_key IS NOT NULL;

-- RLS: Only service_role can access (no direct user access to audit log)
ALTER TABLE ops.work_item_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role only" ON ops.work_item_events FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- RPC FUNCTION: upsert_work_item_link
-- Purpose: Atomic mapping creation/update with automatic updated_at timestamp
-- Access: service_role only (called from Edge Functions or n8n)
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
    -- Validate sync_state
    IF p_sync_state NOT IN ('ok', 'needs_review', 'blocked') THEN
        RAISE EXCEPTION 'Invalid sync_state: %', p_sync_state;
    END IF;

    -- Upsert (insert or update)
    INSERT INTO ops.work_item_links (
        plane_project_id,
        plane_issue_id,
        odoo_project_id,
        odoo_task_id,
        sync_state,
        last_plane_hash,
        last_odoo_hash,
        last_synced_at,
        updated_at
    ) VALUES (
        p_plane_project_id,
        p_plane_issue_id,
        p_odoo_project_id,
        p_odoo_task_id,
        p_sync_state,
        p_last_plane_hash,
        p_last_odoo_hash,
        now(),
        now()
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

-- Grant execute to service_role only
REVOKE ALL ON FUNCTION ops.upsert_work_item_link FROM PUBLIC;
GRANT EXECUTE ON FUNCTION ops.upsert_work_item_link TO service_role;

-- =============================================================================
-- RPC FUNCTION: append_work_item_event
-- Purpose: Safe event logging with idempotency enforcement
-- Access: service_role only
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
    -- Validate event_type
    IF p_event_type NOT IN ('plane_to_odoo', 'odoo_to_plane', 'reconciliation', 'conflict') THEN
        RAISE EXCEPTION 'Invalid event_type: %', p_event_type;
    END IF;

    -- Validate source_system
    IF p_source_system NOT IN ('plane', 'odoo', 'n8n') THEN
        RAISE EXCEPTION 'Invalid source_system: %', p_source_system;
    END IF;

    -- Check idempotency (if key provided)
    IF p_idempotency_key IS NOT NULL THEN
        SELECT id INTO v_existing_event_id
        FROM ops.work_item_events
        WHERE idempotency_key = p_idempotency_key;

        -- Return existing event ID if already processed
        IF v_existing_event_id IS NOT NULL THEN
            RETURN v_existing_event_id;
        END IF;
    END IF;

    -- Insert new event (append-only)
    INSERT INTO ops.work_item_events (
        link_id,
        event_type,
        source_system,
        event_data,
        idempotency_key,
        success,
        error_message
    ) VALUES (
        p_link_id,
        p_event_type,
        p_source_system,
        p_event_data,
        p_idempotency_key,
        p_success,
        p_error_message
    )
    RETURNING id INTO v_event_id;

    RETURN v_event_id;
END;
$$;

-- Grant execute to service_role only
REVOKE ALL ON FUNCTION ops.append_work_item_event FROM PUBLIC;
GRANT EXECUTE ON FUNCTION ops.append_work_item_event TO service_role;

-- =============================================================================
-- RPC FUNCTION: get_sync_conflicts
-- Purpose: Query work items with sync_state='needs_review' for manual intervention
-- Access: service_role only
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
            FROM ops.work_item_events wie
            WHERE wie.link_id = wil.id
            LIMIT 10
        ) AS recent_events
    FROM ops.work_item_links wil
    WHERE wil.sync_state IN ('needs_review', 'blocked')
    ORDER BY wil.updated_at DESC
    LIMIT p_limit;
END;
$$;

-- Grant execute to service_role only
REVOKE ALL ON FUNCTION ops.get_sync_conflicts FROM PUBLIC;
GRANT EXECUTE ON FUNCTION ops.get_sync_conflicts TO service_role;

-- =============================================================================
-- COMMENTS (documentation for Supabase dashboard)
-- =============================================================================

COMMENT ON TABLE ops.work_item_links IS 'PPM Clarity: Bidirectional ID mapping between Plane.so issues and Odoo project tasks. Tracks sync state and field ownership via deterministic hashes.';
COMMENT ON TABLE ops.work_item_events IS 'PPM Clarity: Append-only audit ledger for all sync operations. Idempotency enforced via unique idempotency_key.';

COMMENT ON COLUMN ops.work_item_links.plane_project_id IS 'Plane project ID (immutable)';
COMMENT ON COLUMN ops.work_item_links.plane_issue_id IS 'Plane issue ID (immutable)';
COMMENT ON COLUMN ops.work_item_links.odoo_project_id IS 'Odoo project.project ID (immutable after first sync)';
COMMENT ON COLUMN ops.work_item_links.odoo_task_id IS 'Odoo project.task ID (immutable after first sync)';
COMMENT ON COLUMN ops.work_item_links.sync_state IS 'Sync health: ok (normal), needs_review (conflict detected), blocked (manual intervention required)';
COMMENT ON COLUMN ops.work_item_links.last_plane_hash IS 'Deterministic hash of Plane-owned fields (title, description, priority, labels, cycle, state)';
COMMENT ON COLUMN ops.work_item_links.last_odoo_hash IS 'Deterministic hash of Odoo-owned fields (assigned users, timesheets, costs, attachments)';

COMMENT ON COLUMN ops.work_item_events.event_type IS 'plane_to_odoo | odoo_to_plane | reconciliation | conflict';
COMMENT ON COLUMN ops.work_item_events.source_system IS 'System that triggered the event: plane | odoo | n8n';
COMMENT ON COLUMN ops.work_item_events.event_data IS 'Flexible JSONB payload with system-specific event details';
COMMENT ON COLUMN ops.work_item_events.idempotency_key IS 'Unique key to prevent duplicate event processing (nullable for non-idempotent events)';

COMMENT ON FUNCTION ops.upsert_work_item_link IS 'Atomic mapping creation/update. Returns link_id. Service role only.';
COMMENT ON FUNCTION ops.append_work_item_event IS 'Append event to audit ledger with idempotency check. Returns event_id. Service role only.';
COMMENT ON FUNCTION ops.get_sync_conflicts IS 'Query work items with sync conflicts (needs_review or blocked). Returns conflicts with recent event history. Service role only.';

-- =============================================================================
-- VERIFICATION QUERIES (for testing after migration)
-- =============================================================================

-- EXAMPLE: Insert test mapping
-- SELECT ops.upsert_work_item_link(
--     p_plane_project_id := 'proj-123',
--     p_plane_issue_id := 'issue-456',
--     p_odoo_project_id := 1,
--     p_odoo_task_id := 100,
--     p_sync_state := 'ok',
--     p_last_plane_hash := 'abc123',
--     p_last_odoo_hash := 'def456'
-- );

-- EXAMPLE: Append test event
-- SELECT ops.append_work_item_event(
--     p_link_id := '<link-id-from-above>',
--     p_event_type := 'plane_to_odoo',
--     p_source_system := 'n8n',
--     p_event_data := '{"action": "created_task", "task_id": 100}'::jsonb,
--     p_idempotency_key := 'test-key-123',
--     p_success := true
-- );

-- EXAMPLE: Get conflicts
-- SELECT * FROM ops.get_sync_conflicts(10);
