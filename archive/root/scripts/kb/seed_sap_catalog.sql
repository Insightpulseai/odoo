-- =============================================================================
-- SEED: SAP Help Portal Catalog
-- =============================================================================
-- Populates kb.catalog_sources and kb.catalog_nodes with strategic SAP
-- Help Portal content for parity analysis.
--
-- Strategy:
-- - Use portfolio/category/product hierarchy
-- - Only harvest pages that are:
--   1. Referenced by a journey/runbook
--   2. Appear in search demand (rag.search_logs)
--   3. In target set (Finance, HR, Supply Chain)
--
-- This prevents weeks of embedding low-value product docs.
--
-- Usage:
--   psql -v tenant_id="'00000000-0000-0000-0000-000000000001'" -f seed_sap_catalog.sql
-- =============================================================================

\set tenant_id '00000000-0000-0000-0000-000000000001'

BEGIN;

-- =============================================================================
-- 1) CREATE SOURCE
-- =============================================================================

INSERT INTO kb.catalog_sources (tenant_id, code, name, base_url, description, priority, config)
VALUES (
    :'tenant_id'::uuid,
    'sap_help',
    'SAP Help Portal',
    'https://help.sap.com/',
    'SAP documentation for parity analysis - Strategic areas only',
    5,
    '{"scope": "parity_analysis", "products": ["s4hana", "concur", "ariba", "successfactors"]}'::jsonb
)
ON CONFLICT (tenant_id, code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    updated_at = now();

-- =============================================================================
-- 2) CREATE ROOT NODE
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'sap_help'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest)
SELECT
    :'tenant_id'::uuid,
    src.id,
    NULL,
    'portfolio',
    'SAP Help Portal',
    'sap-help',
    'https://help.sap.com/',
    0,
    false,
    false
FROM src
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    updated_at = now();

-- =============================================================================
-- 3) CREATE PRODUCT CATEGORIES (Index nodes - not harvested directly)
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'sap_help'
),
root AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'sap-help' AND cn.parent_id IS NULL
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest)
SELECT
    :'tenant_id'::uuid,
    root.source_id,
    root.id,
    'category',
    x.title,
    x.slug,
    x.url,
    x.sort_order,
    false,
    false  -- Categories are index nodes, not harvested
FROM root
CROSS JOIN (VALUES
    ('S/4HANA',            's4hana',          'https://help.sap.com/docs/SAP_S4HANA_CLOUD',           10),
    ('Concur',             'concur',          'https://help.sap.com/docs/SAP_CONCUR',                 20),
    ('Ariba',              'ariba',           'https://help.sap.com/docs/SAP_ARIBA',                  30),
    ('SuccessFactors',     'successfactors',  'https://help.sap.com/docs/SAP_SUCCESSFACTORS_PLATFORM', 40),
    ('Business ByDesign',  'bydesign',        'https://help.sap.com/docs/SAP_BUSINESS_BYDESIGN',      50),
    ('Analytics Cloud',    'sac',             'https://help.sap.com/docs/SAP_ANALYTICS_CLOUD',        60)
) AS x(title, slug, url, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    updated_at = now();

-- =============================================================================
-- 4) S/4HANA - FINANCE MODULES (Harvest these)
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'sap_help'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 's4hana'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth, meta)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'product',
    x.title,
    x.slug,
    x.url,
    x.sort_order,
    true,
    true,  -- Harvest these for parity analysis
    3,
    '{"parity_target": "odoo_accounting"}'::jsonb
FROM parent
CROSS JOIN (VALUES
    ('General Ledger',           's4-gl',        'https://help.sap.com/docs/SAP_S4HANA_CLOUD/gl',           10),
    ('Accounts Payable',         's4-ap',        'https://help.sap.com/docs/SAP_S4HANA_CLOUD/ap',           20),
    ('Accounts Receivable',      's4-ar',        'https://help.sap.com/docs/SAP_S4HANA_CLOUD/ar',           30),
    ('Asset Accounting',         's4-aa',        'https://help.sap.com/docs/SAP_S4HANA_CLOUD/aa',           40),
    ('Financial Closing',        's4-close',     'https://help.sap.com/docs/SAP_S4HANA_CLOUD/close',        50),
    ('Cash Management',          's4-cash',      'https://help.sap.com/docs/SAP_S4HANA_CLOUD/cash',         60)
) AS x(title, slug, url, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 5) S/4HANA - SUPPLY CHAIN MODULES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'sap_help'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 's4hana'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth, meta)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'product',
    x.title,
    x.slug,
    x.url,
    x.sort_order,
    true,
    true,
    3,
    '{"parity_target": "odoo_inventory"}'::jsonb
FROM parent
CROSS JOIN (VALUES
    ('Inventory Management',     's4-im',        'https://help.sap.com/docs/SAP_S4HANA_CLOUD/im',           110),
    ('Warehouse Management',     's4-wm',        'https://help.sap.com/docs/SAP_S4HANA_CLOUD/wm',           120),
    ('Production Planning',      's4-pp',        'https://help.sap.com/docs/SAP_S4HANA_CLOUD/pp',           130),
    ('Quality Management',       's4-qm',        'https://help.sap.com/docs/SAP_S4HANA_CLOUD/qm',           140),
    ('Procurement',              's4-mm',        'https://help.sap.com/docs/SAP_S4HANA_CLOUD/mm',           150)
) AS x(title, slug, url, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 6) S/4HANA - SALES MODULES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'sap_help'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 's4hana'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth, meta)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'product',
    x.title,
    x.slug,
    x.url,
    x.sort_order,
    true,
    true,
    3,
    '{"parity_target": "odoo_sales"}'::jsonb
FROM parent
CROSS JOIN (VALUES
    ('Sales Order Management',   's4-sd',        'https://help.sap.com/docs/SAP_S4HANA_CLOUD/sd',           200),
    ('Pricing',                  's4-pricing',   'https://help.sap.com/docs/SAP_S4HANA_CLOUD/pricing',      210),
    ('Billing',                  's4-billing',   'https://help.sap.com/docs/SAP_S4HANA_CLOUD/billing',      220)
) AS x(title, slug, url, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 7) CONCUR - EXPENSE MANAGEMENT
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'sap_help'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'concur'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth, meta)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'product',
    x.title,
    x.slug,
    x.url,
    x.sort_order,
    true,
    true,
    4,
    '{"parity_target": "odoo_expenses"}'::jsonb
FROM parent
CROSS JOIN (VALUES
    ('Expense Reports',          'concur-expense',   'https://help.sap.com/docs/SAP_CONCUR/expense',        10),
    ('Travel Booking',           'concur-travel',    'https://help.sap.com/docs/SAP_CONCUR/travel',         20),
    ('Invoice Processing',       'concur-invoice',   'https://help.sap.com/docs/SAP_CONCUR/invoice',        30),
    ('Receipts',                 'concur-receipts',  'https://help.sap.com/docs/SAP_CONCUR/receipts',       40),
    ('Workflows',                'concur-workflows', 'https://help.sap.com/docs/SAP_CONCUR/workflows',      50)
) AS x(title, slug, url, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 8) ARIBA - PROCUREMENT
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'sap_help'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'ariba'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth, meta)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'product',
    x.title,
    x.slug,
    x.url,
    x.sort_order,
    true,
    true,
    4,
    '{"parity_target": "odoo_purchase"}'::jsonb
FROM parent
CROSS JOIN (VALUES
    ('Sourcing',                 'ariba-sourcing',   'https://help.sap.com/docs/SAP_ARIBA/sourcing',        10),
    ('Contracts',                'ariba-contracts',  'https://help.sap.com/docs/SAP_ARIBA/contracts',       20),
    ('Buying',                   'ariba-buying',     'https://help.sap.com/docs/SAP_ARIBA/buying',          30),
    ('Invoicing',                'ariba-invoicing',  'https://help.sap.com/docs/SAP_ARIBA/invoicing',       40),
    ('Supplier Management',      'ariba-suppliers',  'https://help.sap.com/docs/SAP_ARIBA/suppliers',       50)
) AS x(title, slug, url, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 9) SUCCESSFACTORS - HR
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'sap_help'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'successfactors'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth, meta)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'product',
    x.title,
    x.slug,
    x.url,
    x.sort_order,
    true,
    true,
    4,
    '{"parity_target": "odoo_hr"}'::jsonb
FROM parent
CROSS JOIN (VALUES
    ('Employee Central',         'sf-ec',            'https://help.sap.com/docs/SAP_SUCCESSFACTORS/ec',       10),
    ('Recruiting',               'sf-recruiting',    'https://help.sap.com/docs/SAP_SUCCESSFACTORS/rms',      20),
    ('Onboarding',               'sf-onboarding',    'https://help.sap.com/docs/SAP_SUCCESSFACTORS/onb',      30),
    ('Performance & Goals',      'sf-pmgm',          'https://help.sap.com/docs/SAP_SUCCESSFACTORS/pmgm',     40),
    ('Compensation',             'sf-comp',          'https://help.sap.com/docs/SAP_SUCCESSFACTORS/comp',     50),
    ('Learning',                 'sf-lms',           'https://help.sap.com/docs/SAP_SUCCESSFACTORS/lms',      60),
    ('Time Tracking',            'sf-time',          'https://help.sap.com/docs/SAP_SUCCESSFACTORS/time',     70),
    ('Payroll',                  'sf-payroll',       'https://help.sap.com/docs/SAP_SUCCESSFACTORS/payroll',  80)
) AS x(title, slug, url, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 10) QUEUE STRATEGIC NODES FOR HARVEST
-- =============================================================================

INSERT INTO kb.harvest_state (tenant_id, node_id, status, queued_at)
SELECT cn.tenant_id, cn.id, 'queued', now()
FROM kb.catalog_nodes cn
JOIN kb.catalog_sources cs ON cs.id = cn.source_id
WHERE cs.code = 'sap_help'
  AND cn.tenant_id = :'tenant_id'::uuid
  AND cn.is_leaf = true
  AND cn.should_harvest = true
ON CONFLICT (tenant_id, node_id) DO UPDATE SET
    status = 'queued',
    queued_at = now(),
    updated_at = now();

COMMIT;

-- =============================================================================
-- VERIFY
-- =============================================================================

SELECT 'SAP Catalog Sources:' AS info;
SELECT code, name, priority FROM kb.catalog_sources WHERE tenant_id = :'tenant_id'::uuid AND code = 'sap_help';

SELECT 'SAP Node Counts by Kind:' AS info;
SELECT cn.kind, count(*)
FROM kb.catalog_nodes cn
JOIN kb.catalog_sources cs ON cs.id = cn.source_id
WHERE cn.tenant_id = :'tenant_id'::uuid AND cs.code = 'sap_help'
GROUP BY cn.kind ORDER BY cn.kind;

SELECT 'SAP Harvest Queue:' AS info;
SELECT hs.status, count(*)
FROM kb.harvest_state hs
JOIN kb.catalog_nodes cn ON cn.id = hs.node_id
JOIN kb.catalog_sources cs ON cs.id = cn.source_id
WHERE hs.tenant_id = :'tenant_id'::uuid AND cs.code = 'sap_help'
GROUP BY hs.status;

SELECT 'SAP Coverage Stats:' AS info;
SELECT * FROM kb.get_source_coverage('sap_help');

SELECT 'Parity Targets:' AS info;
SELECT cn.slug, cn.title, cn.meta->>'parity_target' as parity_target
FROM kb.catalog_nodes cn
JOIN kb.catalog_sources cs ON cs.id = cn.source_id
WHERE cs.code = 'sap_help' AND cn.is_leaf = true
ORDER BY cn.meta->>'parity_target', cn.slug;
