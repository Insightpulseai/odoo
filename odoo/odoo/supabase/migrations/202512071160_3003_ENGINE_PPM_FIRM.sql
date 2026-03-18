-- 202512071160_3003_ENGINE_PPM_FIRM.sql
-- Family: 3000 - Engines (PPM / Accounting-Firm)
-- Purpose:
--   * Engine for project profitability, capacity & engagement tracking.
-- Safety:
--   * Additive & idempotent, no drops.

BEGIN;

CREATE SCHEMA IF NOT EXISTS ppm;

-- TODO: PPM TABLES
--   * ppm.client
--   * ppm.engagement
--   * ppm.work_log
--   * ppm.billing_schedule
--   * ppm.retainer_config
--   * ppm.erp_mapping

-- TODO: PPM ANALYTIC VIEWS (can also live in analytics/gold schemas later)
--   * ppm.vw_profitability
--   * ppm.vw_capacity_utilization

COMMIT;
