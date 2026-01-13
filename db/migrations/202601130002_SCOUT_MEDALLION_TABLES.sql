-- Migration: Create Scout Medallion Layer Tables
-- Version: 202601130002
-- Description: Create scout_dim, scout_fact, scout_gold tables (internal, not exposed)
-- Author: Platform Team
-- Date: 2026-01-13
--
-- These tables are SERVICE-ROLE ONLY - never exposed to anon/authenticated directly.
-- Frontends access them ONLY through scout_api views.

-- ============================================================================
-- PHASE 1: DIMENSION TABLES (scout_dim)
-- ============================================================================

-- -----------------------------------------------------------------------------
-- 1.1 Brands Dimension
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scout_dim.brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_code TEXT NOT NULL UNIQUE,
    brand_name TEXT NOT NULL,
    category TEXT,
    subcategory TEXT,
    manufacturer TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_dim_brands_category ON scout_dim.brands(category);
CREATE INDEX IF NOT EXISTS idx_dim_brands_active ON scout_dim.brands(is_active) WHERE is_active = true;

COMMENT ON TABLE scout_dim.brands IS 'Brand dimension table. Internal - access via scout_api.brand_catalog';

-- -----------------------------------------------------------------------------
-- 1.2 Products Dimension
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scout_dim.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    brand_id UUID REFERENCES scout_dim.brands(id),
    category TEXT,
    subcategory TEXT,
    unit_price NUMERIC(15,2),
    unit_cost NUMERIC(15,2),
    is_active BOOLEAN NOT NULL DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_dim_products_brand ON scout_dim.products(brand_id);
CREATE INDEX IF NOT EXISTS idx_dim_products_category ON scout_dim.products(category);
CREATE INDEX IF NOT EXISTS idx_dim_products_active ON scout_dim.products(is_active) WHERE is_active = true;

COMMENT ON TABLE scout_dim.products IS 'Product dimension table. Internal - access via scout_api.product_catalog';

-- -----------------------------------------------------------------------------
-- 1.3 Stores Dimension
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scout_dim.stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_code TEXT NOT NULL UNIQUE,
    store_name TEXT NOT NULL,
    store_type TEXT NOT NULL DEFAULT 'retail',
    region TEXT,
    city TEXT,
    barangay TEXT,
    address TEXT,
    latitude NUMERIC(10,7),
    longitude NUMERIC(10,7),
    is_active BOOLEAN NOT NULL DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_dim_stores_region ON scout_dim.stores(region);
CREATE INDEX IF NOT EXISTS idx_dim_stores_city ON scout_dim.stores(city);
CREATE INDEX IF NOT EXISTS idx_dim_stores_type ON scout_dim.stores(store_type);
CREATE INDEX IF NOT EXISTS idx_dim_stores_active ON scout_dim.stores(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_dim_stores_geo ON scout_dim.stores(latitude, longitude);

COMMENT ON TABLE scout_dim.stores IS 'Store dimension table. Internal - access via scout_api.store_locations';

-- -----------------------------------------------------------------------------
-- 1.4 Time Dimension (Date hierarchy)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scout_dim.dates (
    date_key DATE PRIMARY KEY,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    week INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    month_name TEXT NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN NOT NULL DEFAULT false,
    fiscal_year INTEGER,
    fiscal_quarter INTEGER
);

COMMENT ON TABLE scout_dim.dates IS 'Date dimension for time-series analysis';

-- ============================================================================
-- PHASE 2: FACT TABLES (scout_fact)
-- ============================================================================

-- -----------------------------------------------------------------------------
-- 2.1 Daily Sales Fact
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scout_fact.daily_sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL REFERENCES scout_dim.dates(date_key),
    store_id UUID NOT NULL REFERENCES scout_dim.stores(id),
    brand_id UUID REFERENCES scout_dim.brands(id),
    product_id UUID REFERENCES scout_dim.products(id),
    units_sold INTEGER NOT NULL DEFAULT 0,
    revenue NUMERIC(15,2) NOT NULL DEFAULT 0,
    cost NUMERIC(15,2) DEFAULT 0,
    transactions INTEGER NOT NULL DEFAULT 0,
    avg_basket_size NUMERIC(10,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_fact_daily_sales_date ON scout_fact.daily_sales(date);
CREATE INDEX IF NOT EXISTS idx_fact_daily_sales_store ON scout_fact.daily_sales(store_id, date);
CREATE INDEX IF NOT EXISTS idx_fact_daily_sales_brand ON scout_fact.daily_sales(brand_id, date);
CREATE UNIQUE INDEX IF NOT EXISTS idx_fact_daily_sales_unique
    ON scout_fact.daily_sales(date, store_id, COALESCE(brand_id, '00000000-0000-0000-0000-000000000000'), COALESCE(product_id, '00000000-0000-0000-0000-000000000000'));

COMMENT ON TABLE scout_fact.daily_sales IS 'Daily sales aggregates. Internal - access via scout_api.daily_sales';

-- -----------------------------------------------------------------------------
-- 2.2 Inventory Snapshots Fact
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scout_fact.inventory_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_date DATE NOT NULL REFERENCES scout_dim.dates(date_key),
    store_id UUID NOT NULL REFERENCES scout_dim.stores(id),
    product_id UUID NOT NULL REFERENCES scout_dim.products(id),
    quantity_on_hand INTEGER NOT NULL DEFAULT 0,
    quantity_reserved INTEGER NOT NULL DEFAULT 0,
    quantity_available INTEGER GENERATED ALWAYS AS (quantity_on_hand - quantity_reserved) STORED,
    days_of_supply NUMERIC(5,1),
    is_out_of_stock BOOLEAN GENERATED ALWAYS AS (quantity_available <= 0) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_fact_inventory_date ON scout_fact.inventory_snapshots(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_fact_inventory_store_product ON scout_fact.inventory_snapshots(store_id, product_id);
CREATE INDEX IF NOT EXISTS idx_fact_inventory_oos ON scout_fact.inventory_snapshots(is_out_of_stock) WHERE is_out_of_stock = true;

COMMENT ON TABLE scout_fact.inventory_snapshots IS 'Daily inventory snapshots by store/product';

-- ============================================================================
-- PHASE 3: GOLD LAYER TABLES (scout_gold)
-- ============================================================================

-- -----------------------------------------------------------------------------
-- 3.1 Sample Metrics (KPI aggregates)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scout_gold.sample_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    code TEXT NOT NULL,
    brand_id UUID REFERENCES scout_dim.brands(id),
    store_id UUID REFERENCES scout_dim.stores(id),
    value NUMERIC(15,4) NOT NULL,
    unit TEXT NOT NULL DEFAULT 'count',
    is_alert BOOLEAN NOT NULL DEFAULT false,
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_gold_metrics_date_code ON scout_gold.sample_metrics(date, code);
CREATE INDEX IF NOT EXISTS idx_gold_metrics_brand ON scout_gold.sample_metrics(brand_id, date);
CREATE INDEX IF NOT EXISTS idx_gold_metrics_store ON scout_gold.sample_metrics(store_id, date);
CREATE INDEX IF NOT EXISTS idx_gold_metrics_alerts ON scout_gold.sample_metrics(is_alert) WHERE is_alert = true;

COMMENT ON TABLE scout_gold.sample_metrics IS 'KPI metrics for dashboards. Internal - access via scout_api.sample_metrics';

-- -----------------------------------------------------------------------------
-- 3.2 Consumer Insights
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scout_gold.consumer_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    segment TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    value NUMERIC(15,4) NOT NULL,
    trend_direction TEXT CHECK (trend_direction IN ('up', 'down', 'stable')),
    confidence_score NUMERIC(5,4),
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_gold_insights_date_segment ON scout_gold.consumer_insights(date, segment);
CREATE INDEX IF NOT EXISTS idx_gold_insights_metric ON scout_gold.consumer_insights(metric_type, date);

COMMENT ON TABLE scout_gold.consumer_insights IS 'Consumer behavior insights. Internal - access via scout_api.consumer_insights';

-- -----------------------------------------------------------------------------
-- 3.3 Brand Performance
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scout_gold.brand_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES scout_dim.brands(id),
    brand_name TEXT NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    revenue NUMERIC(15,2) NOT NULL DEFAULT 0,
    units_sold INTEGER NOT NULL DEFAULT 0,
    market_share_pct NUMERIC(5,2),
    growth_rate_pct NUMERIC(8,2),
    rank_position INTEGER,
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_gold_brand_perf_period ON scout_gold.brand_performance(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_gold_brand_perf_brand ON scout_gold.brand_performance(brand_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_gold_brand_perf_unique
    ON scout_gold.brand_performance(brand_id, period_start, period_end) WHERE NOT is_deleted;

COMMENT ON TABLE scout_gold.brand_performance IS 'Brand performance metrics. Internal - access via scout_api.brand_performance';

-- -----------------------------------------------------------------------------
-- 3.4 Alerts
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scout_gold.alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    title TEXT NOT NULL,
    description TEXT,
    store_id UUID REFERENCES scout_dim.stores(id),
    brand_id UUID REFERENCES scout_dim.brands(id),
    metric_value NUMERIC(15,4),
    threshold_value NUMERIC(15,4),
    is_acknowledged BOOLEAN NOT NULL DEFAULT false,
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by TEXT,
    is_resolved BOOLEAN NOT NULL DEFAULT false,
    resolved_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_gold_alerts_type ON scout_gold.alerts(alert_type, created_at);
CREATE INDEX IF NOT EXISTS idx_gold_alerts_severity ON scout_gold.alerts(severity) WHERE NOT is_resolved;
CREATE INDEX IF NOT EXISTS idx_gold_alerts_store ON scout_gold.alerts(store_id) WHERE NOT is_resolved;
CREATE INDEX IF NOT EXISTS idx_gold_alerts_unresolved ON scout_gold.alerts(is_resolved) WHERE NOT is_resolved;

COMMENT ON TABLE scout_gold.alerts IS 'Active alerts. Internal - access via scout_api.alerts';

-- ============================================================================
-- PHASE 4: UPDATE TRIGGERS
-- ============================================================================

-- Apply updated_at triggers
DO $$
DECLARE
    tbl RECORD;
BEGIN
    FOR tbl IN
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE schemaname IN ('scout_dim', 'scout_fact', 'scout_gold')
    LOOP
        -- Check if table has updated_at column
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = tbl.schemaname
            AND table_name = tbl.tablename
            AND column_name = 'updated_at'
        ) THEN
            EXECUTE format(
                'DROP TRIGGER IF EXISTS set_updated_at ON %I.%I',
                tbl.schemaname, tbl.tablename
            );
            EXECUTE format(
                'CREATE TRIGGER set_updated_at BEFORE UPDATE ON %I.%I FOR EACH ROW EXECUTE FUNCTION core.set_updated_at()',
                tbl.schemaname, tbl.tablename
            );
        END IF;
    END LOOP;
END $$;

-- ============================================================================
-- PHASE 5: POPULATE DATE DIMENSION (2024-2027)
-- ============================================================================

INSERT INTO scout_dim.dates (
    date_key, year, quarter, month, week, day_of_week, day_of_month,
    day_name, month_name, is_weekend, fiscal_year, fiscal_quarter
)
SELECT
    d::date as date_key,
    EXTRACT(year FROM d)::integer as year,
    EXTRACT(quarter FROM d)::integer as quarter,
    EXTRACT(month FROM d)::integer as month,
    EXTRACT(week FROM d)::integer as week,
    EXTRACT(dow FROM d)::integer as day_of_week,
    EXTRACT(day FROM d)::integer as day_of_month,
    to_char(d, 'Day') as day_name,
    to_char(d, 'Month') as month_name,
    EXTRACT(dow FROM d) IN (0, 6) as is_weekend,
    CASE WHEN EXTRACT(month FROM d) >= 7
         THEN EXTRACT(year FROM d)::integer
         ELSE EXTRACT(year FROM d)::integer - 1
    END as fiscal_year,
    CASE WHEN EXTRACT(month FROM d) >= 7
         THEN EXTRACT(quarter FROM d)::integer - 2
         ELSE EXTRACT(quarter FROM d)::integer + 2
    END as fiscal_quarter
FROM generate_series('2024-01-01'::date, '2027-12-31'::date, '1 day'::interval) d
ON CONFLICT (date_key) DO NOTHING;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

COMMENT ON SCHEMA scout_dim IS 'Scout dimension tables. Service-role only.';
COMMENT ON SCHEMA scout_fact IS 'Scout fact tables. Service-role only.';
COMMENT ON SCHEMA scout_gold IS 'Scout gold layer aggregates. Service-role only.';
