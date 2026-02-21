-- ==========================================================================
-- Supabase Integration Event Bus
-- Shared table for Odoo ↔ Plane ↔ Shelf.nu async event passing
-- ==========================================================================
-- Deploy: supabase db push (or paste in Supabase SQL Editor)
-- Project: spdtwktxdalcfigzeqrz
-- ==========================================================================

CREATE TABLE IF NOT EXISTS public.integration_events (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at      timestamptz DEFAULT now() NOT NULL,
    processed_at    timestamptz,

    -- Source system
    source          text NOT NULL CHECK (source IN ('odoo', 'plane', 'shelf')),

    -- Event routing
    event_type      text NOT NULL,
    -- e.g. 'task.created', 'asset.upsert', 'work_item.updated'

    -- Target (optional — NULL = broadcast to all consumers)
    target          text CHECK (target IS NULL OR target IN ('odoo', 'plane', 'shelf')),

    -- Organization scoping
    organization_id text,

    -- Payload (JSON blob)
    payload         jsonb NOT NULL DEFAULT '{}'::jsonb,

    -- Processing state
    status          text NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'dead_letter')),
    error_message   text,
    retry_count     int NOT NULL DEFAULT 0,
    max_retries     int NOT NULL DEFAULT 3
);

-- Indexes for consumer polling
CREATE INDEX IF NOT EXISTS idx_integration_events_status_source
    ON public.integration_events (status, source)
    WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_integration_events_target
    ON public.integration_events (target, status)
    WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_integration_events_created
    ON public.integration_events (created_at DESC);

-- Row Level Security
ALTER TABLE public.integration_events ENABLE ROW LEVEL SECURITY;

-- Service role can do everything
CREATE POLICY "service_role_full_access" ON public.integration_events
    FOR ALL
    USING (auth.role() = 'service_role');

-- ==========================================================================
-- Mapping tables for cross-system ID resolution
-- ==========================================================================

CREATE TABLE IF NOT EXISTS public.integration_id_map (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at      timestamptz DEFAULT now() NOT NULL,
    updated_at      timestamptz DEFAULT now() NOT NULL,

    -- System A
    system_a        text NOT NULL CHECK (system_a IN ('odoo', 'plane', 'shelf')),
    entity_type_a   text NOT NULL,  -- e.g. 'project.task', 'work_item', 'Asset'
    entity_id_a     text NOT NULL,

    -- System B
    system_b        text NOT NULL CHECK (system_b IN ('odoo', 'plane', 'shelf')),
    entity_type_b   text NOT NULL,
    entity_id_b     text NOT NULL,

    -- Metadata
    metadata        jsonb DEFAULT '{}'::jsonb,

    UNIQUE (system_a, entity_type_a, entity_id_a, system_b, entity_type_b)
);

CREATE INDEX IF NOT EXISTS idx_id_map_lookup_a
    ON public.integration_id_map (system_a, entity_type_a, entity_id_a);

CREATE INDEX IF NOT EXISTS idx_id_map_lookup_b
    ON public.integration_id_map (system_b, entity_type_b, entity_id_b);

ALTER TABLE public.integration_id_map ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_full_access_map" ON public.integration_id_map
    FOR ALL
    USING (auth.role() = 'service_role');

-- ==========================================================================
-- Helper function: claim next pending event for processing
-- ==========================================================================
CREATE OR REPLACE FUNCTION public.claim_integration_event(
    p_target text,
    p_batch_size int DEFAULT 10
)
RETURNS SETOF public.integration_events
LANGUAGE sql
AS $$
    UPDATE public.integration_events
    SET status = 'processing', processed_at = now()
    WHERE id IN (
        SELECT id FROM public.integration_events
        WHERE status = 'pending'
          AND (target IS NULL OR target = p_target)
        ORDER BY created_at
        LIMIT p_batch_size
        FOR UPDATE SKIP LOCKED
    )
    RETURNING *;
$$;
