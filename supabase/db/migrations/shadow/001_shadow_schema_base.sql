-- =============================================================================
-- ODOO SHADOW SCHEMA - Base Infrastructure
-- =============================================================================
-- Purpose: Set up shadow schema infrastructure for Odoo -> Supabase sync
-- Date: 2026-01-20
--
-- This migration creates:
-- 1. odoo_shadow schema (read-only mirror of Odoo data)
-- 2. Shadow metadata registry
-- 3. Sync tracking infrastructure
-- =============================================================================

-- Create shadow schema
CREATE SCHEMA IF NOT EXISTS odoo_shadow;

COMMENT ON SCHEMA odoo_shadow IS
    'Read-only shadow of Odoo CE data. Source of truth remains Odoo PostgreSQL.';

-- =============================================================================
-- Shadow Metadata Registry
-- =============================================================================

CREATE TABLE IF NOT EXISTS odoo_shadow_meta (
    id bigserial PRIMARY KEY,
    table_name text NOT NULL UNIQUE,
    odoo_model text NOT NULL,
    odoo_module text,
    field_count integer,
    last_sync_at timestamptz,
    last_sync_duration_ms integer,
    row_count bigint,
    sync_errors integer DEFAULT 0,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

COMMENT ON TABLE odoo_shadow_meta IS
    'Registry of shadow tables with sync metadata';

CREATE INDEX IF NOT EXISTS idx_shadow_meta_last_sync
    ON odoo_shadow_meta (last_sync_at DESC);

-- =============================================================================
-- Sync Watermarks (for incremental ETL)
-- =============================================================================

CREATE TABLE IF NOT EXISTS odoo_shadow_watermark (
    id bigserial PRIMARY KEY,
    table_name text NOT NULL UNIQUE,
    last_write_date timestamptz NOT NULL,
    last_id bigint,
    rows_synced bigint DEFAULT 0,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

COMMENT ON TABLE odoo_shadow_watermark IS
    'Watermarks for incremental sync - tracks last synced write_date per table';

CREATE INDEX IF NOT EXISTS idx_shadow_watermark_write_date
    ON odoo_shadow_watermark (last_write_date DESC);

-- =============================================================================
-- Sync Audit Log
-- =============================================================================

CREATE TABLE IF NOT EXISTS odoo_shadow_sync_log (
    id bigserial PRIMARY KEY,
    sync_run_id uuid DEFAULT gen_random_uuid(),
    table_name text NOT NULL,
    started_at timestamptz NOT NULL DEFAULT now(),
    completed_at timestamptz,
    rows_inserted integer DEFAULT 0,
    rows_updated integer DEFAULT 0,
    rows_deleted integer DEFAULT 0,
    duration_ms integer,
    status text DEFAULT 'running', -- running, success, error
    error_message text,
    metadata jsonb
);

COMMENT ON TABLE odoo_shadow_sync_log IS
    'Audit log of ETL sync runs for observability';

CREATE INDEX IF NOT EXISTS idx_shadow_sync_log_table
    ON odoo_shadow_sync_log (table_name, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_shadow_sync_log_status
    ON odoo_shadow_sync_log (status) WHERE status != 'success';

-- =============================================================================
-- Helper Functions
-- =============================================================================

-- Function to update watermark after successful sync
CREATE OR REPLACE FUNCTION update_shadow_watermark(
    p_table_name text,
    p_write_date timestamptz,
    p_last_id bigint DEFAULT NULL,
    p_rows_synced bigint DEFAULT 0
) RETURNS void AS $$
BEGIN
    INSERT INTO odoo_shadow_watermark (table_name, last_write_date, last_id, rows_synced, updated_at)
    VALUES (p_table_name, p_write_date, p_last_id, p_rows_synced, now())
    ON CONFLICT (table_name) DO UPDATE SET
        last_write_date = EXCLUDED.last_write_date,
        last_id = COALESCE(EXCLUDED.last_id, odoo_shadow_watermark.last_id),
        rows_synced = odoo_shadow_watermark.rows_synced + EXCLUDED.rows_synced,
        updated_at = now();
END;
$$ LANGUAGE plpgsql;

-- Function to get last sync watermark for a table
CREATE OR REPLACE FUNCTION get_shadow_watermark(p_table_name text)
RETURNS timestamptz AS $$
DECLARE
    v_watermark timestamptz;
BEGIN
    SELECT last_write_date INTO v_watermark
    FROM odoo_shadow_watermark
    WHERE table_name = p_table_name;

    -- Default to epoch if no watermark exists (full sync)
    RETURN COALESCE(v_watermark, '1970-01-01'::timestamptz);
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Grants (adjust for your Supabase roles)
-- =============================================================================

-- Read-only access for anon/authenticated (adjust as needed)
-- GRANT USAGE ON SCHEMA odoo_shadow TO anon, authenticated;
-- GRANT SELECT ON ALL TABLES IN SCHEMA odoo_shadow TO anon, authenticated;

-- Full access for service role (ETL)
-- GRANT ALL ON SCHEMA odoo_shadow TO service_role;
-- GRANT ALL ON ALL TABLES IN SCHEMA odoo_shadow TO service_role;
