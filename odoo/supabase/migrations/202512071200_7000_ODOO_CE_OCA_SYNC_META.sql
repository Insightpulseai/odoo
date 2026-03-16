-- 202512071200_7000_ODOO_CE_OCA_SYNC_META.sql
-- Family: 7000 - Odoo CE / OCA sync metadata
-- Purpose:
--   * Metadata bridge between Supabase schemas and Odoo 18 CE/OCA modules.
-- Safety:
--   * Additive only.

BEGIN;

CREATE SCHEMA IF NOT EXISTS odoo;
CREATE SCHEMA IF NOT EXISTS oca;
CREATE SCHEMA IF NOT EXISTS odoo_sync;

-- TODO: ODOO MODULE CATALOG
--   * odoo.module_catalog
--   * odoo.module_state

-- TODO: OCA EQUIVALENCE
--   * oca.module_compat

-- TODO: ODOO SYNC MAPS
--   * odoo_sync.model_map       -- supabase schema.table ↔ odoo model
--   * odoo_sync.field_map       -- column ↔ odoo field
--   * odoo_sync.export_jobs
--   * odoo_sync.import_jobs

COMMIT;
