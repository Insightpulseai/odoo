-- =============================================================================
-- Supabase Preview Branch Seed File
-- =============================================================================
-- This file is executed automatically when Supabase creates a preview branch.
-- It consolidates all seed data for a complete test environment.
--
-- Order matters: core data first, then domain-specific data
-- =============================================================================

-- Announce seed start
DO $$
BEGIN
    RAISE NOTICE 'Starting Supabase preview branch seeding...';
    RAISE NOTICE 'Timestamp: %', NOW();
END $$;

-- =============================================================================
-- CORE SEEDS (9000-series: tenants, roles, users)
-- =============================================================================

-- Core tenants, roles, and users
\ir seed/9000_core/9000_core_tenants_roles_users.sql

-- =============================================================================
-- ERP SEEDS (9001-series: Odoo integration data)
-- =============================================================================

-- ERP projects and billing rates
\ir seed/9001_erp/9001_erp_projects_rates_demo.sql

-- Finance BIR templates
\ir seed/9001_erp/9001_erp_finance_bir_templates.sql

-- =============================================================================
-- ENGINE SEEDS (9002-series: processing engines)
-- =============================================================================

-- Retail intelligence (PH market)
\ir seed/9002_engines/9002_engines_retail_intel_ph.sql

-- PPM demo data
\ir seed/9002_engines/9002_engines_ppm_demo.sql

-- TE-Cheq demo flows
\ir seed/9002_engines/9002_engines_te_cheq_demo_flows.sql

-- Document OCR samples
\ir seed/9002_engines/9002_engines_doc_ocr_sample_docs.sql

-- =============================================================================
-- AI/RAG SEEDS (9003-series: AI agent data)
-- =============================================================================

-- Marketing canvas documents
\ir seed/9003_ai_rag/9003_ai_rag_marketing_canvas_docs.sql

-- Agent registry
\ir seed/9003_ai_rag/9003_ai_rag_agent_registry_seed.sql

-- =============================================================================
-- ANALYTICS SEEDS (9004-series: BI/analytics)
-- =============================================================================

-- KPI registry
\ir seed/9004_analytics/9004_analytics_kpi_registry_seed.sql

-- Superset dashboard definitions
\ir seed/9004_analytics/9004_analytics_superset_dashboard_seed.sql

-- =============================================================================
-- CATALOG SEEDS (9005-9006 series: asset catalogs)
-- =============================================================================

-- Asset and tools catalog
\ir seed/9005_catalog/9005_catalog_assets_tools.sql

-- Scout SUQI semantic data
\ir seed/9006_catalog/9006_scout_suqi_semantic.sql

-- =============================================================================
-- SKILLS SEEDS (9007-9008 series: certifications)
-- =============================================================================

-- Skills certification
\ir seed/9007_skills/9007_skills_certification_seed.sql

-- Draw.io certification
\ir seed/9008_drawio_skills/9008_drawio_certification_seed.sql

-- Draw.io assessment tasks
\ir seed/9008_drawio_skills/9008_drawio_assessment_tasks.sql

-- =============================================================================
-- FEATURE SEEDS (SaaS features)
-- =============================================================================

-- SaaS feature flags
\ir seed/001_saas_feature_seed.sql

-- =============================================================================
-- LEGACY SEEDS (from seeds/ directory)
-- =============================================================================

-- HR organizational structure
\ir seeds/001_hr_seed.sql

-- Finance categories, budgets, expense rules
\ir seeds/002_finance_seed.sql

-- Odoo data dictionary (PPM fields)
\ir seeds/003_odoo_dict_seed.sql

-- =============================================================================
-- SEED COMPLETE
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Preview branch seeding complete!';
    RAISE NOTICE 'Timestamp: %', NOW();
END $$;
