-- =============================================================================
-- Seed: 9006 - Scout SUQI Semantic Contract
-- Purpose: Dashboard semantic model with data dictionary + Odoo/UC mappings
-- Account: tbwa_smp
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- Analytic Accounting Core Anchors (Cost Spine)
-- These bridge accounting ↔ projects ↔ timesheets ↔ profitability
-- -----------------------------------------------------------------------------

INSERT INTO catalog.assets (fqdn, asset_type, system, title, description, owner, tags, uri, metadata)
VALUES
    ('odoo.odoo_core.account.analytic.account', 'odoo_model', 'odoo', 'Analytic Account',
     'Cost center / project accounting spine. Bridges accounting ↔ projects ↔ timesheets ↔ profitability.',
     'finance_team', ARRAY['finance', 'analytic', 'cost-spine', 'core'],
     '/web#model=account.analytic.account&view_type=list',
     '{"fields": ["name", "code", "plan_id", "company_id", "partner_id", "active", "balance", "debit", "credit"], "key_role": "cost_spine"}'::jsonb),

    ('odoo.odoo_core.account.analytic.line', 'odoo_model', 'odoo', 'Analytic Line',
     'Cost/revenue line items linked to analytic accounts. Timesheets, expenses, journal items.',
     'finance_team', ARRAY['finance', 'analytic', 'detail'],
     '/web#model=account.analytic.line&view_type=list',
     '{"fields": ["name", "account_id", "date", "amount", "unit_amount", "product_id", "partner_id", "company_id"]}'::jsonb),

    ('odoo.odoo_core.account.analytic.plan', 'odoo_model', 'odoo', 'Analytic Plan',
     'Grouping of analytic accounts (cost centers, projects, departments)',
     'finance_team', ARRAY['finance', 'analytic', 'master'],
     '/web#model=account.analytic.plan&view_type=list',
     '{"fields": ["name", "description", "parent_id", "company_id"]}'::jsonb)

ON CONFLICT (fqdn) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    metadata = EXCLUDED.metadata,
    updated_at = now();


-- -----------------------------------------------------------------------------
-- Scout SUQI Dashboard Asset (Gold Layer)
-- Primary semantic model for TBWA SMP Scout analytics
-- -----------------------------------------------------------------------------

INSERT INTO catalog.assets (fqdn, asset_type, system, title, description, owner, tags, uri, metadata)
VALUES
    -- Main dashboard asset
    ('scout.tbwa_smp.scout_suqi_dashboard', 'dashboard', 'scout', 'Scout SUQI Dashboard',
     'Sari-sari store analytics: transaction trends, product mix, consumer behavior, competitive analysis',
     'analytics_team', ARRAY['scout', 'dashboard', 'tbwa', 'retail'],
     NULL,
     '{
        "version": "1.0",
        "account": "tbwa_smp",
        "page_count": 7,
        "tab_count": 25,
        "kpi_count": 24,
        "visual_count": 17,
        "pages": ["transaction_trends", "product_mix_sku", "consumer_behavior", "consumer_profiling", "competitive_analysis", "geographical_intelligence", "scout_dashboard_transactions"]
     }'::jsonb),

    -- Underlying gold tables
    ('scout.tbwa_smp.gold.transaction', 'table', 'scout', 'Scout Transaction',
     'Gold layer transaction fact table with enriched behavioral/demographic fields',
     'analytics_team', ARRAY['scout', 'gold', 'fact', 'transaction'],
     NULL,
     '{"grain": "transaction", "field_count": 26}'::jsonb),

    ('scout.tbwa_smp.gold.transaction_line_item', 'table', 'scout', 'Scout Transaction Line Item',
     'Line item detail for multi-SKU transactions',
     'analytics_team', ARRAY['scout', 'gold', 'fact', 'detail'],
     NULL,
     '{"grain": "line_item"}'::jsonb),

    ('scout.tbwa_smp.gold.customer_profile', 'table', 'scout', 'Scout Customer Profile',
     'Enriched customer demographics and behavioral traits',
     'analytics_team', ARRAY['scout', 'gold', 'dimension', 'customer'],
     NULL,
     '{"grain": "customer"}'::jsonb),

    ('scout.tbwa_smp.gold.store_master', 'table', 'scout', 'Scout Store Master',
     'Sari-sari store master data with location and attributes',
     'analytics_team', ARRAY['scout', 'gold', 'dimension', 'store'],
     NULL,
     '{"grain": "store"}'::jsonb),

    ('scout.tbwa_smp.gold.sku_master', 'table', 'scout', 'Scout SKU Master',
     'Product SKU master with brand and category hierarchy',
     'analytics_team', ARRAY['scout', 'gold', 'dimension', 'product'],
     NULL,
     '{"grain": "sku"}'::jsonb)

ON CONFLICT (fqdn) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    metadata = EXCLUDED.metadata,
    updated_at = now();


-- -----------------------------------------------------------------------------
-- Scout SUQI Semantic Model (Metric Layer)
-- Business-friendly dimensions and metrics for dashboard
-- -----------------------------------------------------------------------------

INSERT INTO catalog.semantic_models (asset_id, model_name, label, description, source_table, source_schema, time_dimension, default_grain, status)
SELECT
    a.id,
    'scout_transactions',
    'Scout Transaction Analytics',
    'Semantic model for sari-sari store transaction analysis with behavioral enrichment',
    'transaction',
    'gold',
    'timestamp',
    'day',
    'active'
FROM catalog.assets a
WHERE a.fqdn = 'scout.tbwa_smp.gold.transaction'
ON CONFLICT DO NOTHING;


-- -----------------------------------------------------------------------------
-- Scout SUQI Dimensions
-- -----------------------------------------------------------------------------

INSERT INTO catalog.semantic_dimensions (model_id, dim_name, label, description, expression, data_type, is_primary_key, is_foreign_key)
SELECT
    m.id,
    d.dim_name,
    d.label,
    d.description,
    d.expression,
    d.data_type,
    d.is_pk,
    d.is_fk
FROM catalog.semantic_models m
CROSS JOIN (VALUES
    -- Identifiers
    ('id', 'Transaction ID', 'Unique transaction identifier', 'id', 'string', true, false),
    ('store_id', 'Store ID', 'Store unique identifier', 'store_id', 'string', false, true),

    -- Time dimensions
    ('timestamp', 'Transaction Time', 'UTC datetime of transaction', 'timestamp', 'timestamp', false, false),
    ('time_of_day', 'Time of Day', 'Morning/Afternoon/Evening/Night', 'time_of_day', 'string', false, false),

    -- Location hierarchy (PH geo)
    ('barangay', 'Barangay', 'Philippine barangay', 'location.barangay', 'string', false, false),
    ('city', 'City', 'Philippine city', 'location.city', 'string', false, false),
    ('province', 'Province', 'Philippine province', 'location.province', 'string', false, false),
    ('region', 'Region', 'Philippine region', 'location.region', 'string', false, false),

    -- Product hierarchy
    ('product_category', 'Product Category', 'High-level category (Snack, Tobacco, etc.)', 'product_category', 'string', false, false),
    ('brand_name', 'Brand Name', 'Brand of purchased SKU', 'brand_name', 'string', false, false),
    ('sku', 'SKU', 'Product SKU/variant', 'sku', 'string', false, true),

    -- Behavioral (enriched)
    ('request_mode', 'Request Mode', 'Verbal/Pointing/Indirect', 'request_mode', 'string', false, false),
    ('request_type', 'Request Type', 'Branded/Unbranded/Point/Indirect', 'request_type', 'string', false, false),
    ('suggestion_accepted', 'Suggestion Accepted', 'Customer accepted storeowner suggestion', 'suggestion_accepted', 'boolean', false, false),

    -- Demographics (enriched)
    ('gender', 'Gender', 'Male/Female/Unknown', 'gender', 'string', false, false),
    ('age_bracket', 'Age Bracket', '18-24/25-34/35-44/45-54/55+/Unknown', 'age_bracket', 'string', false, false)
) AS d(dim_name, label, description, expression, data_type, is_pk, is_fk)
WHERE m.model_name = 'scout_transactions'
ON CONFLICT DO NOTHING;


-- -----------------------------------------------------------------------------
-- Scout SUQI Metrics
-- -----------------------------------------------------------------------------

INSERT INTO catalog.semantic_metrics (model_id, metric_name, label, description, expression, metric_type, aggregation, format_string)
SELECT
    m.id,
    met.metric_name,
    met.label,
    met.description,
    met.expression,
    met.metric_type,
    met.aggregation,
    met.format_string
FROM catalog.semantic_models m
CROSS JOIN (VALUES
    -- Volume metrics
    ('transaction_count', 'Transaction Count', 'Number of transactions', 'COUNT(*)', 'simple', 'count', '#,##0'),
    ('daily_volume', 'Daily Volume', 'Transactions per day', 'COUNT(*)', 'simple', 'count', '#,##0'),

    -- Revenue metrics
    ('revenue_sum', 'Total Revenue', 'Sum of transaction values (PHP)', 'SUM(peso_value)', 'simple', 'sum', '₱#,##0.00'),
    ('daily_revenue', 'Daily Revenue', 'Revenue per day (PHP)', 'SUM(peso_value)', 'simple', 'sum', '₱#,##0.00'),
    ('avg_transaction_value', 'Avg Transaction Value', 'Average peso value per transaction', 'AVG(peso_value)', 'simple', 'average', '₱#,##0.00'),

    -- Basket metrics
    ('basket_size_avg', 'Avg Basket Size', 'Average SKUs per transaction', 'AVG(basket_size)', 'simple', 'average', '#,##0.0'),
    ('units_sum', 'Total Units', 'Sum of units sold', 'SUM(units_per_transaction)', 'simple', 'sum', '#,##0'),

    -- Duration metrics
    ('duration_avg', 'Avg Duration', 'Average transaction duration (seconds)', 'AVG(duration_seconds)', 'simple', 'average', '#,##0'),

    -- Behavioral metrics
    ('conversion_rate', 'Conversion Rate', 'Visit to purchase conversion', 'COUNT(CASE WHEN purchased THEN 1 END)::float / COUNT(*)', 'derived', 'ratio', '0.0%'),
    ('suggestion_accept_rate', 'Suggestion Accept Rate', 'Rate of accepted suggestions', 'AVG(CASE WHEN suggestion_accepted THEN 1 ELSE 0 END)', 'simple', 'average', '0.0%'),
    ('brand_loyalty_rate', 'Brand Loyalty Rate', 'Repeat purchase rate for same brand', 'COUNT(DISTINCT CASE WHEN repeat_brand THEN customer_id END)::float / COUNT(DISTINCT customer_id)', 'derived', 'ratio', '0.0%'),

    -- Product metrics
    ('sku_count', 'Active SKUs', 'Distinct SKU count', 'COUNT(DISTINCT sku)', 'simple', 'count_distinct', '#,##0'),
    ('category_diversity', 'Category Diversity', 'Percentage of categories represented', 'COUNT(DISTINCT product_category)::float / (SELECT COUNT(*) FROM category_master)', 'derived', 'ratio', '0.0%'),

    -- Substitution metrics
    ('substitution_rate', 'Substitution Rate', 'Rate of product substitutions', 'AVG(CASE WHEN substitution_event.occurred THEN 1 ELSE 0 END)', 'simple', 'average', '0.0%')
) AS met(metric_name, label, description, expression, metric_type, aggregation, format_string)
WHERE m.model_name = 'scout_transactions'
ON CONFLICT DO NOTHING;


-- -----------------------------------------------------------------------------
-- Odoo Mapping Metadata (for sync/enrichment)
-- -----------------------------------------------------------------------------

-- Insert mapping as catalog.assets metadata extension
UPDATE catalog.assets
SET metadata = metadata || '{
    "odoo_mappings": {
        "pos.order": {
            "id": "name",
            "timestamp": "create_date",
            "peso_value": "amount_total"
        },
        "pos.order.line": {
            "units_per_transaction": "qty",
            "sku": "product_id.default_code"
        },
        "pos.config": {
            "store_id": "store_code"
        },
        "product.product": {
            "sku": "default_code",
            "brand_name": "product_brand_id.name"
        },
        "product.category": {
            "product_category": "name"
        }
    },
    "oca_modules_required": ["product_brand", "base_address_extended", "l10n_ph"],
    "enrichment_required_fields": ["time_of_day", "request_mode", "request_type", "suggestion_accepted", "gender", "age_bracket", "substitution_event"]
}'::jsonb
WHERE fqdn = 'scout.tbwa_smp.gold.transaction';


-- -----------------------------------------------------------------------------
-- Data Dictionary Fields as Catalog Metadata
-- -----------------------------------------------------------------------------

INSERT INTO catalog.assets (fqdn, asset_type, system, title, description, owner, tags, uri, metadata)
VALUES
    ('scout.tbwa_smp.data_dictionary', 'documentation', 'scout', 'Scout Transaction Data Dictionary',
     'Field definitions for Scout transaction schema with Odoo/UC mappings',
     'analytics_team', ARRAY['scout', 'documentation', 'schema'],
     NULL,
     '{
        "version": "1.0",
        "total_fields": 26,
        "total_required": 26,
        "total_enum_fields": 9,
        "fields": [
            {"field_id": "id", "data_type": "string", "required": true, "unique": true, "odoo_model": "pos.order", "odoo_field": "name", "uc_column": "transaction_id"},
            {"field_id": "store_id", "data_type": "string", "required": true, "odoo_model": "pos.config", "odoo_field": "store_code", "uc_column": "store_id"},
            {"field_id": "timestamp", "data_type": "datetime", "required": true, "odoo_model": "pos.order", "odoo_field": "create_date", "uc_column": "timestamp"},
            {"field_id": "time_of_day", "data_type": "enum", "required": true, "enum_values": ["morning","afternoon","evening","night"], "enrichment_required": true},
            {"field_id": "location", "data_type": "object", "required": true, "sub_fields": ["barangay","city","province","region"]},
            {"field_id": "product_category", "data_type": "string", "required": true, "odoo_model": "product.category", "odoo_field": "name"},
            {"field_id": "brand_name", "data_type": "string", "required": true, "odoo_model": "product.brand", "odoo_field": "name"},
            {"field_id": "sku", "data_type": "string", "required": true, "odoo_model": "product.product", "odoo_field": "default_code"},
            {"field_id": "units_per_transaction", "data_type": "integer", "required": true, "odoo_model": "pos.order.line", "odoo_field": "qty"},
            {"field_id": "peso_value", "data_type": "float", "required": true, "currency": "PHP", "odoo_model": "pos.order", "odoo_field": "amount_total"},
            {"field_id": "basket_size", "data_type": "integer", "required": true, "enrichment_required": true},
            {"field_id": "combo_basket", "data_type": "array", "required": true, "enrichment_required": true},
            {"field_id": "request_mode", "data_type": "enum", "required": true, "enum_values": ["verbal","pointing","indirect"], "enrichment_required": true},
            {"field_id": "request_type", "data_type": "enum", "required": true, "enum_values": ["branded","unbranded","point","indirect"], "enrichment_required": true},
            {"field_id": "suggestion_accepted", "data_type": "boolean", "required": true, "enrichment_required": true},
            {"field_id": "gender", "data_type": "enum", "required": true, "enum_values": ["male","female","unknown"], "enrichment_required": true},
            {"field_id": "age_bracket", "data_type": "enum", "required": true, "enum_values": ["18-24","25-34","35-44","45-54","55+","unknown"], "enrichment_required": true},
            {"field_id": "substitution_event", "data_type": "object", "required": true, "enrichment_required": true}
        ],
        "extended_fields": ["duration_seconds", "payment_method", "customer_type", "store_type", "handshake_score", "campaign_influenced", "economic_class", "is_tbwa_client"]
     }'::jsonb)

ON CONFLICT (fqdn) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    metadata = EXCLUDED.metadata,
    updated_at = now();


-- -----------------------------------------------------------------------------
-- Lineage: Gold tables → Semantic model
-- -----------------------------------------------------------------------------

INSERT INTO catalog.lineage_edges (from_asset_id, to_asset_id, edge_type, job_name, metadata)
SELECT
    f.id, t.id, 'derived_from', 'semantic_model_definition',
    '{"relationship": "physical_to_semantic"}'::jsonb
FROM catalog.assets f, catalog.assets t
WHERE f.fqdn = 'scout.tbwa_smp.gold.transaction'
  AND t.fqdn = 'scout.tbwa_smp.scout_suqi_dashboard'
ON CONFLICT DO NOTHING;

-- Odoo POS → Scout gold (sync lineage)
INSERT INTO catalog.lineage_edges (from_asset_id, to_asset_id, edge_type, job_name, metadata)
SELECT
    f.id, t.id, 'writes_to', 'scout_pos_sync',
    '{"sync_type": "incremental", "enrichment": "behavioral_demographic"}'::jsonb
FROM catalog.assets f, catalog.assets t
WHERE f.fqdn = 'odoo.odoo_core.pos.order'
  AND t.fqdn = 'scout.tbwa_smp.gold.transaction'
ON CONFLICT DO NOTHING;


-- -----------------------------------------------------------------------------
-- OCA Module Tier Recommendations
-- -----------------------------------------------------------------------------

INSERT INTO catalog.assets (fqdn, asset_type, system, title, description, owner, tags, uri, metadata)
VALUES
    ('oca.tier_a.recommended', 'documentation', 'oca', 'OCA Tier A - Must Have',
     'OCA modules almost always worth installing',
     'platform_team', ARRAY['oca', 'modules', 'tier_a'],
     NULL,
     '{
        "tier": "A",
        "description": "Almost always worth it",
        "modules": [
            {"repo": "server-ux", "module": "base_tier_validation", "purpose": "Multi-level approvals"},
            {"repo": "reporting-engine", "module": "report_xlsx", "purpose": "XLSX reporting"},
            {"repo": "server-tools", "module": "auditlog", "purpose": "Audit logging"}
        ]
     }'::jsonb),

    ('oca.tier_b.selective', 'documentation', 'oca', 'OCA Tier B - Selective',
     'OCA modules to install only if business process needs it',
     'platform_team', ARRAY['oca', 'modules', 'tier_b'],
     NULL,
     '{
        "tier": "B",
        "description": "Only if business process needs it",
        "modules": [
            {"repo": "helpdesk", "module": "helpdesk_mgmt", "purpose": "ServiceNow-like ticketing"},
            {"repo": "contract", "module": "contract", "purpose": "Subscription/contract management"},
            {"repo": "social", "module": "marketing_*", "purpose": "Marketing extensions"},
            {"repo": "sale-workflow", "module": "*", "purpose": "Pick modules surgically, not repo-wide"},
            {"repo": "purchase-workflow", "module": "*", "purpose": "Pick modules surgically"},
            {"repo": "project", "module": "*", "purpose": "Pick modules surgically"}
        ],
        "warning": "Prevents OCA sprawl - pick surgical modules, not entire repos"
     }'::jsonb)

ON CONFLICT (fqdn) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    metadata = EXCLUDED.metadata,
    updated_at = now();


COMMIT;

-- =============================================================================
-- End Seed: 9006 - Scout SUQI Semantic Contract
-- =============================================================================
