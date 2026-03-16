-- 202512071140_3001_ENGINE_RETAIL_INTEL_SCOUT.sql
-- Family: 3000 - Engines (Retail Intelligence / Scout / SariCoach)
-- Purpose:
--   * Establish Scout/SariCoach schemas for dims, facts, gold views and metadata.
--   * Provide the storage backbone for the Scout dashboard (Trends, Product Mix,
--     Consumer Behavior, Profiling, Competitive, Geo, Data Dictionary).
-- Safety:
--   * Additive and idempotent.

BEGIN;

CREATE SCHEMA IF NOT EXISTS scout_bronze;
CREATE SCHEMA IF NOT EXISTS scout_silver;
CREATE SCHEMA IF NOT EXISTS scout_fact;
CREATE SCHEMA IF NOT EXISTS scout_dim;
CREATE SCHEMA IF NOT EXISTS scout_gold;
CREATE SCHEMA IF NOT EXISTS scout_meta;

-- TODO: DIMENSIONS
--   * scout_dim.stores
--   * scout_dim.brands
--   * scout_dim.products
--   * scout_dim.categories
--   * scout_dim.customers
--   * scout_dim.time
--   * scout_dim.location

-- TODO: FACTS
--   * scout_fact.transactions
--   * scout_fact.store_daily
--   * scout_fact.brand_daily
--   * scout_fact.customer_behavior
--   * scout_fact.geo_daily

-- TODO: META / DICTIONARY
--   * scout_meta.fields
--   * scout_meta.kpis
--   * scout_meta.charts
--   * scout_meta.filters
--   * scout_meta.ai_documents
--   * scout_meta.ai_embeddings

-- Notes for later DDL:
--   * Include tenant_id, store_id, brand_id, sku_id, region, barangay, etc.
--   * Use partitions by date for large fact tables.

COMMIT;
