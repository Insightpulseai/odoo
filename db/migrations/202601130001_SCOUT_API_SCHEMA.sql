-- Migration: Create Scout API Schema (Exposed Layer)
-- Version: 202601130001
-- Description: Create scout_api schema with read-only views for frontends
-- Author: Platform Team
-- Date: 2026-01-13
--
-- PRINCIPLE: Only expose the "contract" schema
-- - scout_api: Views only, exposed to anon/authenticated
-- - ipai, scout_bronze/silver/gold: Service-role only, never exposed

-- ============================================================================
-- PHASE 1: CREATE API SCHEMA
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS scout_api;

COMMENT ON SCHEMA scout_api IS 'API layer for Scout/Ops Control Room frontends. Read-only views only. This is the ONLY schema exposed to anon/authenticated roles.';

-- ============================================================================
-- PHASE 2: REVOKE DEFAULT PUBLIC ACCESS
-- ============================================================================

-- Ensure internal schemas are not accessible by anon/authenticated
REVOKE ALL ON SCHEMA scout_bronze FROM anon, authenticated;
REVOKE ALL ON SCHEMA scout_silver FROM anon, authenticated;
REVOKE ALL ON SCHEMA scout_gold FROM anon, authenticated;
REVOKE ALL ON SCHEMA scout_dim FROM anon, authenticated;
REVOKE ALL ON SCHEMA scout_fact FROM anon, authenticated;

-- Grant usage on API schema to authenticated users
GRANT USAGE ON SCHEMA scout_api TO anon, authenticated;

-- ============================================================================
-- PHASE 3: CREATE API VIEWS OVER GOLD LAYER
-- ============================================================================

-- -----------------------------------------------------------------------------
-- 3.1 Sample Metrics View (for Scout Dashboard KPIs)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW scout_api.sample_metrics AS
SELECT
    id,
    date,
    code,
    brand_id,
    store_id,
    value,
    unit,
    is_alert,
    created_at
FROM scout_gold.sample_metrics
WHERE NOT COALESCE(is_deleted, false);

COMMENT ON VIEW scout_api.sample_metrics IS 'Read-only metrics for Scout dashboards. Source: scout_gold.sample_metrics';

-- -----------------------------------------------------------------------------
-- 3.2 Consumer Insights View
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW scout_api.consumer_insights AS
SELECT
    id,
    date,
    segment,
    metric_type,
    value,
    trend_direction,
    confidence_score,
    created_at
FROM scout_gold.consumer_insights
WHERE NOT COALESCE(is_deleted, false);

COMMENT ON VIEW scout_api.consumer_insights IS 'Consumer behavior insights. Source: scout_gold.consumer_insights';

-- -----------------------------------------------------------------------------
-- 3.3 Brand Performance View
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW scout_api.brand_performance AS
SELECT
    id,
    brand_id,
    brand_name,
    period_start,
    period_end,
    revenue,
    units_sold,
    market_share_pct,
    growth_rate_pct,
    rank_position,
    created_at
FROM scout_gold.brand_performance
WHERE NOT COALESCE(is_deleted, false);

COMMENT ON VIEW scout_api.brand_performance IS 'Brand performance metrics. Source: scout_gold.brand_performance';

-- -----------------------------------------------------------------------------
-- 3.4 Store Locations View
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW scout_api.store_locations AS
SELECT
    id,
    store_code,
    store_name,
    store_type,
    region,
    city,
    barangay,
    latitude,
    longitude,
    is_active,
    created_at
FROM scout_dim.stores
WHERE is_active = true;

COMMENT ON VIEW scout_api.store_locations IS 'Active store locations for mapping. Source: scout_dim.stores';

-- -----------------------------------------------------------------------------
-- 3.5 Brand Catalog View
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW scout_api.brand_catalog AS
SELECT
    id,
    brand_code,
    brand_name,
    category,
    subcategory,
    manufacturer,
    is_active,
    created_at
FROM scout_dim.brands
WHERE is_active = true;

COMMENT ON VIEW scout_api.brand_catalog IS 'Active brand catalog. Source: scout_dim.brands';

-- -----------------------------------------------------------------------------
-- 3.6 Product Catalog View
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW scout_api.product_catalog AS
SELECT
    id,
    sku,
    product_name,
    brand_id,
    category,
    unit_price,
    unit_cost,
    is_active,
    created_at
FROM scout_dim.products
WHERE is_active = true;

COMMENT ON VIEW scout_api.product_catalog IS 'Active product catalog. Source: scout_dim.products';

-- -----------------------------------------------------------------------------
-- 3.7 Daily Sales Aggregates View
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW scout_api.daily_sales AS
SELECT
    id,
    date,
    store_id,
    brand_id,
    product_id,
    units_sold,
    revenue,
    transactions,
    avg_basket_size,
    created_at
FROM scout_fact.daily_sales;

COMMENT ON VIEW scout_api.daily_sales IS 'Daily sales aggregates. Source: scout_fact.daily_sales';

-- -----------------------------------------------------------------------------
-- 3.8 Alerts View
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW scout_api.alerts AS
SELECT
    id,
    alert_type,
    severity,
    title,
    description,
    store_id,
    brand_id,
    metric_value,
    threshold_value,
    is_acknowledged,
    acknowledged_at,
    acknowledged_by,
    created_at
FROM scout_gold.alerts
WHERE NOT COALESCE(is_resolved, false);

COMMENT ON VIEW scout_api.alerts IS 'Active alerts for dashboards. Source: scout_gold.alerts';

-- ============================================================================
-- PHASE 4: GRANT SELECT ON ALL API VIEWS
-- ============================================================================

-- Grant SELECT on all views in scout_api to authenticated users
GRANT SELECT ON ALL TABLES IN SCHEMA scout_api TO authenticated;

-- Grant SELECT to anon for public dashboards (optional, remove if not needed)
GRANT SELECT ON scout_api.brand_catalog TO anon;
GRANT SELECT ON scout_api.product_catalog TO anon;
GRANT SELECT ON scout_api.store_locations TO anon;

-- Future views automatically get SELECT for authenticated
ALTER DEFAULT PRIVILEGES IN SCHEMA scout_api
    GRANT SELECT ON TABLES TO authenticated;

-- ============================================================================
-- PHASE 5: ROW LEVEL SECURITY ON VIEWS
-- ============================================================================

-- Note: RLS on views in PostgreSQL works through the underlying tables.
-- Since these are views over gold/dim/fact tables, we rely on those tables'
-- RLS policies. For additional view-level control, use security_invoker views.

-- Enable security_invoker on views (PostgreSQL 15+)
-- This ensures the view runs with the caller's permissions, not definer's

ALTER VIEW scout_api.sample_metrics SET (security_invoker = on);
ALTER VIEW scout_api.consumer_insights SET (security_invoker = on);
ALTER VIEW scout_api.brand_performance SET (security_invoker = on);
ALTER VIEW scout_api.store_locations SET (security_invoker = on);
ALTER VIEW scout_api.brand_catalog SET (security_invoker = on);
ALTER VIEW scout_api.product_catalog SET (security_invoker = on);
ALTER VIEW scout_api.daily_sales SET (security_invoker = on);
ALTER VIEW scout_api.alerts SET (security_invoker = on);

-- ============================================================================
-- PHASE 6: HELPER FUNCTIONS FOR API
-- ============================================================================

-- Function to get current user's accessible store IDs (for RLS)
CREATE OR REPLACE FUNCTION scout_api.get_user_store_ids()
RETURNS SETOF uuid AS $$
BEGIN
    -- Return all stores for now; customize based on user roles
    RETURN QUERY SELECT id FROM scout_dim.stores WHERE is_active = true;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION scout_api.get_user_store_ids() TO authenticated;

-- Function to get current user's accessible brand IDs (for RLS)
CREATE OR REPLACE FUNCTION scout_api.get_user_brand_ids()
RETURNS SETOF uuid AS $$
BEGIN
    -- Return all brands for now; customize based on user roles
    RETURN QUERY SELECT id FROM scout_dim.brands WHERE is_active = true;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION scout_api.get_user_brand_ids() TO authenticated;

-- ============================================================================
-- PHASE 7: API METADATA VIEW
-- ============================================================================

-- Expose API schema metadata for documentation/introspection
CREATE OR REPLACE VIEW scout_api._meta AS
SELECT
    'scout_api' as schema_name,
    '1.0.0' as api_version,
    now() as generated_at,
    jsonb_build_object(
        'views', (
            SELECT jsonb_agg(table_name ORDER BY table_name)
            FROM information_schema.views
            WHERE table_schema = 'scout_api'
            AND table_name NOT LIKE '\_%'
        ),
        'description', 'Scout/Ops Control Room API layer. Read-only views over Gold layer.',
        'contact', 'platform@insightpulseai.net'
    ) as metadata;

GRANT SELECT ON scout_api._meta TO authenticated, anon;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Verification query (run manually to verify setup):
-- SELECT * FROM scout_api._meta;
-- SELECT table_name FROM information_schema.views WHERE table_schema = 'scout_api';
