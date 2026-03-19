-- LIB Hybrid Brain - Supabase Shared Brain Schema
-- Namespace: lib_shared
-- Purpose: Multi-device file intelligence sync with CRDT conflict resolution

-- Create lib_shared schema
CREATE SCHEMA IF NOT EXISTS lib_shared;

-- Entities table (materialized current state)
CREATE TABLE lib_shared.entities (
    entity_type TEXT NOT NULL,
    entity_key TEXT NOT NULL,
    latest_event_ulid TEXT NOT NULL,
    latest_payload JSONB NOT NULL,
    vector_clock JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (entity_type, entity_key)
);

CREATE INDEX idx_entities_updated ON lib_shared.entities(updated_at DESC);
CREATE INDEX idx_entities_type ON lib_shared.entities(entity_type);

-- Events table (append-only SSOT)
CREATE TABLE lib_shared.events (
    id BIGSERIAL PRIMARY KEY,
    event_ulid TEXT NOT NULL UNIQUE,
    device_id TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK(event_type IN ('upsert_file', 'delete_file', 'initial_sync')),
    entity_type TEXT NOT NULL CHECK(entity_type IN ('file')),
    entity_key TEXT NOT NULL,
    payload JSONB NOT NULL,
    vector_clock JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_events_created_at ON lib_shared.events(created_at DESC);
CREATE INDEX idx_events_entity ON lib_shared.events(entity_type, entity_key);
CREATE INDEX idx_events_device ON lib_shared.events(device_id);
CREATE INDEX idx_events_ulid ON lib_shared.events(event_ulid);
CREATE INDEX idx_events_vector_clock ON lib_shared.events USING GIN(vector_clock);

-- Device webhooks registry for real-time sync notifications
CREATE TABLE lib_shared.device_webhooks (
    id BIGSERIAL PRIMARY KEY,
    device_id TEXT NOT NULL UNIQUE,
    webhook_url TEXT NOT NULL,
    secret TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    last_notified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_webhooks_device ON lib_shared.device_webhooks(device_id);
CREATE INDEX idx_webhooks_active ON lib_shared.device_webhooks(active) WHERE active = TRUE;

-- CRDT merge function: Compare vector clocks
CREATE OR REPLACE FUNCTION lib_shared.vector_clock_compare(
    vc1 JSONB,
    vc2 JSONB
) RETURNS INT AS $$
DECLARE
    key TEXT;
    vc1_val INT;
    vc2_val INT;
    vc1_greater BOOLEAN := FALSE;
    vc2_greater BOOLEAN := FALSE;
BEGIN
    -- Iterate over all keys in both vector clocks
    FOR key IN SELECT DISTINCT jsonb_object_keys FROM (
        SELECT jsonb_object_keys(vc1)
        UNION
        SELECT jsonb_object_keys(vc2)
    ) AS keys
    LOOP
        vc1_val := COALESCE((vc1->>key)::INT, 0);
        vc2_val := COALESCE((vc2->>key)::INT, 0);

        IF vc1_val > vc2_val THEN
            vc1_greater := TRUE;
        ELSIF vc2_val > vc1_val THEN
            vc2_greater := TRUE;
        END IF;
    END LOOP;

    -- Return comparison result
    IF vc1_greater AND NOT vc2_greater THEN
        RETURN 1;  -- vc1 > vc2 (vc1 is newer)
    ELSIF vc2_greater AND NOT vc1_greater THEN
        RETURN -1; -- vc2 > vc1 (vc2 is newer)
    ELSIF vc1_greater AND vc2_greater THEN
        RETURN 0;  -- Concurrent (conflict)
    ELSE
        RETURN 0;  -- Equal or concurrent
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Idempotent event ingestion with CRDT merge
CREATE OR REPLACE FUNCTION lib_shared.ingest_events(batch JSONB)
RETURNS TABLE(inserted_events INT, upserted_entities INT) AS $$
DECLARE
    event JSONB;
    event_count INT := 0;
    entity_count INT := 0;
    existing_vc JSONB;
    new_vc JSONB;
    vc_comparison INT;
BEGIN
    -- Iterate over batch array
    FOR event IN SELECT * FROM jsonb_array_elements(batch)
    LOOP
        -- Insert event (idempotent via UNIQUE constraint on event_ulid)
        INSERT INTO lib_shared.events (
            event_ulid,
            device_id,
            event_type,
            entity_type,
            entity_key,
            payload,
            vector_clock,
            created_at
        )
        VALUES (
            event->>'event_ulid',
            event->>'device_id',
            event->>'event_type',
            event->>'entity_type',
            event->>'entity_key',
            (event->>'payload')::JSONB,
            (event->>'vector_clock')::JSONB,
            (event->>'created_at')::TIMESTAMPTZ
        )
        ON CONFLICT (event_ulid) DO NOTHING;

        IF FOUND THEN
            event_count := event_count + 1;

            -- CRDT merge logic for entity state
            new_vc := (event->>'vector_clock')::JSONB;

            SELECT vector_clock INTO existing_vc
            FROM lib_shared.entities
            WHERE entity_type = event->>'entity_type'
              AND entity_key = event->>'entity_key';

            IF existing_vc IS NULL THEN
                -- New entity, insert
                INSERT INTO lib_shared.entities (
                    entity_type,
                    entity_key,
                    latest_event_ulid,
                    latest_payload,
                    vector_clock,
                    updated_at
                )
                VALUES (
                    event->>'entity_type',
                    event->>'entity_key',
                    event->>'event_ulid',
                    (event->>'payload')::JSONB,
                    new_vc,
                    NOW()
                );
                entity_count := entity_count + 1;
            ELSE
                -- Compare vector clocks
                vc_comparison := lib_shared.vector_clock_compare(new_vc, existing_vc);

                IF vc_comparison = 1 THEN
                    -- New event is newer, update entity
                    UPDATE lib_shared.entities
                    SET latest_event_ulid = event->>'event_ulid',
                        latest_payload = (event->>'payload')::JSONB,
                        vector_clock = new_vc,
                        updated_at = NOW()
                    WHERE entity_type = event->>'entity_type'
                      AND entity_key = event->>'entity_key';
                    entity_count := entity_count + 1;
                ELSIF vc_comparison = 0 THEN
                    -- Concurrent conflict, use device_id tie-breaker
                    IF (event->>'device_id') > (
                        SELECT device_id FROM lib_shared.events
                        WHERE event_ulid = (
                            SELECT latest_event_ulid FROM lib_shared.entities
                            WHERE entity_type = event->>'entity_type'
                              AND entity_key = event->>'entity_key'
                        )
                    ) THEN
                        -- New event wins tie-breaker
                        UPDATE lib_shared.entities
                        SET latest_event_ulid = event->>'event_ulid',
                            latest_payload = (event->>'payload')::JSONB,
                            vector_clock = new_vc,
                            updated_at = NOW()
                        WHERE entity_type = event->>'entity_type'
                          AND entity_key = event->>'entity_key';
                        entity_count := entity_count + 1;
                    END IF;
                END IF;
                -- If vc_comparison = -1, existing is newer, do nothing
            END IF;
        END IF;
    END LOOP;

    RETURN QUERY SELECT event_count, entity_count;
END;
$$ LANGUAGE plpgsql;

-- Cursored pull of events
CREATE OR REPLACE FUNCTION lib_shared.pull_events(after_id BIGINT, limit_n INT)
RETURNS TABLE(
    id BIGINT,
    event_ulid TEXT,
    device_id TEXT,
    event_type TEXT,
    entity_type TEXT,
    entity_key TEXT,
    payload JSONB,
    vector_clock JSONB,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.event_ulid,
        e.device_id,
        e.event_type,
        e.entity_type,
        e.entity_key,
        e.payload,
        e.vector_clock,
        e.created_at
    FROM lib_shared.events e
    WHERE e.id > after_id
    ORDER BY e.id ASC
    LIMIT limit_n;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (service_role only, no public access)
REVOKE ALL ON SCHEMA lib_shared FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA lib_shared FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA lib_shared FROM PUBLIC;

-- Note: Service role key will be used for all operations (no RLS policies)
