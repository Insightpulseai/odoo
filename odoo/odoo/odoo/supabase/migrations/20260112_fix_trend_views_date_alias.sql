-- 20260112_fix_trend_views_date_alias.sql
-- Purpose: Add legacy "date" column aliases so existing dashboards stop breaking.
-- Context: Frontend selects `date` column from views but v5.2 data model uses `tx_date`.
--          This migration adds backward-compatible aliases.
-- Safety: Idempotent (CREATE SCHEMA/TABLE IF NOT EXISTS, CREATE OR REPLACE VIEW)
-- Schema Drift: Ensures scout schema and gold_transactions table exist in repo migrations.

BEGIN;

-- =============================================================================
-- 0) Ensure scout schema exists (schema drift fix)
-- =============================================================================
CREATE SCHEMA IF NOT EXISTS scout;

COMMENT ON SCHEMA scout IS 'Scout retail analytics - unified namespace for gold layer views';

-- =============================================================================
-- 0.1) Ensure gold_transactions table exists (schema drift fix)
-- Based on Scout SUQI semantic model from catalog seed
-- =============================================================================
CREATE TABLE IF NOT EXISTS scout.gold_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id TEXT,

    -- Time
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    time_of_day TEXT CHECK (time_of_day IN ('morning', 'afternoon', 'evening', 'night')),

    -- Location (Philippine geo hierarchy)
    location_barangay TEXT,
    location_city TEXT,
    location_province TEXT,
    location_region TEXT,

    -- Product
    product_category TEXT,
    brand_name TEXT,
    sku TEXT,

    -- Transaction metrics
    units_per_transaction INTEGER DEFAULT 1,
    peso_value NUMERIC(15,2) DEFAULT 0,
    basket_size INTEGER DEFAULT 1,
    duration_seconds INTEGER,

    -- Behavioral (enriched)
    request_mode TEXT CHECK (request_mode IN ('verbal', 'pointing', 'indirect')),
    request_type TEXT CHECK (request_type IN ('branded', 'unbranded', 'point', 'indirect')),
    suggestion_accepted BOOLEAN DEFAULT false,

    -- Demographics (enriched)
    gender TEXT CHECK (gender IN ('male', 'female', 'unknown')),
    age_bracket TEXT CHECK (age_bracket IN ('18-24', '25-34', '35-44', '45-54', '55+', 'unknown')),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_scout_gold_tx_timestamp ON scout.gold_transactions (timestamp);
CREATE INDEX IF NOT EXISTS idx_scout_gold_tx_brand ON scout.gold_transactions (brand_name);
CREATE INDEX IF NOT EXISTS idx_scout_gold_tx_category ON scout.gold_transactions (product_category);
CREATE INDEX IF NOT EXISTS idx_scout_gold_tx_region ON scout.gold_transactions (location_region);

COMMENT ON TABLE scout.gold_transactions IS 'Scout gold layer - enriched transaction facts for dashboard analytics';

-- =============================================================================
-- 1) Transaction trends view with date alias
-- =============================================================================
CREATE OR REPLACE VIEW scout.v_tx_trends AS
SELECT
    t.id,
    -- canonical
    (t.timestamp AT TIME ZONE 'Asia/Manila')::date AS tx_date,
    -- backwards-compatible alias for existing charts
    (t.timestamp AT TIME ZONE 'Asia/Manila')::date AS date,
    t.brand_name,
    t.product_category,
    t.peso_value,
    t.basket_size,
    t.location_region,
    t.location_province,
    t.location_city
FROM scout.gold_transactions t;

COMMENT ON VIEW scout.v_tx_trends IS 'Transaction trends with tx_date (canonical) and date (legacy alias)';

-- =============================================================================
-- 2) Brand performance by date
-- =============================================================================
CREATE OR REPLACE VIEW scout.v_brand_performance_tx_date AS
SELECT
    (t.timestamp AT TIME ZONE 'Asia/Manila')::date AS tx_date,
    (t.timestamp AT TIME ZONE 'Asia/Manila')::date AS date,
    t.brand_name,
    COUNT(*)                              AS tx_count,
    SUM(t.peso_value)                     AS revenue,
    AVG(t.basket_size)::numeric(10,2)     AS avg_basket_size
FROM scout.gold_transactions t
GROUP BY 1, 2, 3;

COMMENT ON VIEW scout.v_brand_performance_tx_date IS 'Brand performance metrics aggregated by date';

-- =============================================================================
-- 3) Product mix by date
-- =============================================================================
CREATE OR REPLACE VIEW scout.v_product_mix_tx_date AS
SELECT
    (t.timestamp AT TIME ZONE 'Asia/Manila')::date AS tx_date,
    (t.timestamp AT TIME ZONE 'Asia/Manila')::date AS date,
    t.product_category,
    t.brand_name,
    COUNT(*)          AS tx_count,
    SUM(t.peso_value) AS revenue
FROM scout.gold_transactions t
GROUP BY 1, 2, 3, 4;

COMMENT ON VIEW scout.v_product_mix_tx_date IS 'Product mix metrics aggregated by date and category';

-- =============================================================================
-- 4) Geo regions by date
-- =============================================================================
CREATE OR REPLACE VIEW scout.v_geo_regions_tx_date AS
SELECT
    (t.timestamp AT TIME ZONE 'Asia/Manila')::date AS tx_date,
    (t.timestamp AT TIME ZONE 'Asia/Manila')::date AS date,
    t.location_region,
    t.location_province,
    t.location_city,
    COUNT(*)          AS tx_count,
    SUM(t.peso_value) AS revenue
FROM scout.gold_transactions t
GROUP BY 1, 2, 3, 4, 5;

COMMENT ON VIEW scout.v_geo_regions_tx_date IS 'Geographic metrics aggregated by date and location hierarchy';

COMMIT;

-- =============================================================================
-- End Migration: 20260112_fix_trend_views_date_alias.sql
-- =============================================================================
