-- 9002_engines_retail_intel_ph.sql
-- Family: 9002_engines - Retail Intelligence / Scout seed
-- Purpose:
--   * Seed Philippine sari-sari / small-format retail demo data aligned to
--     Scout dashboard pages.
-- Safety:
--   * Demo tenants only.

BEGIN;

-- TODO: INSERT DIMENSION ROWS
--   * scout_dim.stores          -- sari-sari store names + geo hierarchy
--   * scout_dim.brands
--   * scout_dim.products
--   * scout_dim.categories
--   * scout_dim.customers
--   * scout_dim.location

-- TODO: INSERT FACT ROWS
--   * scout_fact.transactions
--   * scout_fact.store_daily
--   * scout_fact.brand_daily
--   * scout_fact.customer_behavior
--   * scout_fact.geo_daily

-- Seed characteristics:
--   * Reflect PH regions (NCR, CALABARZON, Central Visayas, etc.).
--   * Include realistic brand competition and substitution patterns.
--   * Provide enough history to make all Scout charts feel "alive".

COMMIT;
