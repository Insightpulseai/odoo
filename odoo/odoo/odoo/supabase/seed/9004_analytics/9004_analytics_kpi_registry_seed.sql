-- 9004_analytics_kpi_registry_seed.sql
-- Family: 9004_analytics - KPI registry seed
-- Purpose:
--   * Seed KPI metadata for dashboards and AI explanations.
-- Safety:
--   * Demo / reference metadata only.

BEGIN;

-- TODO: INSERT KPI DEFINITIONS
--   * analytics.kpi_registry
--   * scout_meta.kpis
--
-- Example (commented):
-- INSERT INTO analytics.kpi_registry (id, code, name, description, domain)
-- VALUES (gen_random_uuid(), 'SCOUT_DAILY_VOLUME', 'Daily Volume',
--         'Total number of transactions per day across stores', 'retail');

COMMIT;
