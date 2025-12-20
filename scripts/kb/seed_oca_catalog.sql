-- =============================================================================
-- SEED: OCA (Odoo Community Association) Catalog
-- =============================================================================
-- Populates kb.catalog_sources and kb.catalog_nodes with key OCA
-- repositories for 18.0 branch.
--
-- Strategy:
-- - Repositories organized by functional area
-- - Module-level granularity for precise coverage
-- - Only harvest READMEs and manifests, not full code
--
-- Usage:
--   psql -v tenant_id="'00000000-0000-0000-0000-000000000001'" -f seed_oca_catalog.sql
-- =============================================================================

\set tenant_id '00000000-0000-0000-0000-000000000001'

BEGIN;

-- =============================================================================
-- 1) CREATE SOURCE
-- =============================================================================

INSERT INTO kb.catalog_sources (tenant_id, code, name, base_url, description, priority, config)
VALUES (
    :'tenant_id'::uuid,
    'oca_repos',
    'OCA Community Modules',
    'https://github.com/OCA/',
    'Odoo Community Association repositories - 18.0 branch',
    8,
    '{"org": "OCA", "branch": "18.0", "api": "github"}'::jsonb
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
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'oca_repos'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest)
SELECT
    :'tenant_id'::uuid,
    src.id,
    NULL,
    'space',
    'OCA Community Modules',
    'oca',
    'https://github.com/OCA',
    0,
    false,
    false
FROM src
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    updated_at = now();

-- =============================================================================
-- 3) CREATE FUNCTIONAL AREAS
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'oca_repos'
),
root AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'oca' AND cn.parent_id IS NULL
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, sort_order, is_leaf, should_harvest)
SELECT
    :'tenant_id'::uuid,
    root.source_id,
    root.id,
    'category',
    x.title,
    x.slug,
    x.sort_order,
    false,
    false
FROM root
CROSS JOIN (VALUES
    ('Finance',           'oca-finance',        10),
    ('Human Resources',   'oca-hr',             20),
    ('Sales & CRM',       'oca-sales',          30),
    ('Supply Chain',      'oca-supply-chain',   40),
    ('Purchase',          'oca-purchase',       50),
    ('Website',           'oca-website',        60),
    ('Connectors',        'oca-connectors',     70),
    ('Server & Tools',    'oca-server',         80),
    ('Localization',      'oca-l10n',           90)
) AS x(title, slug, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    updated_at = now();

-- =============================================================================
-- 4) FINANCE REPOSITORIES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'oca_repos'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'oca-finance'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'repo',
    x.title,
    x.slug,
    'https://github.com/OCA/' || x.repo || '/tree/18.0',
    x.sort_order,
    true,
    true,
    2
FROM parent
CROSS JOIN (VALUES
    ('Financial Reporting',      'oca-account-financial',       'account-financial-reporting',   10),
    ('Payment Management',       'oca-account-payment',         'account-payment',               20),
    ('Bank Statement Import',    'oca-bank-statement',          'bank-statement-import',         30),
    ('Account Reconcile',        'oca-account-reconcile',       'account-reconcile',             40),
    ('Credit Control',           'oca-credit-control',          'credit-control',                50)
) AS x(title, slug, repo, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 5) HR REPOSITORIES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'oca_repos'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'oca-hr'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'repo',
    x.title,
    x.slug,
    'https://github.com/OCA/' || x.repo || '/tree/18.0',
    x.sort_order,
    true,
    true,
    2
FROM parent
CROSS JOIN (VALUES
    ('HR Core',                  'oca-hr-core',        'hr',              10),
    ('Expense Management',       'oca-hr-expense',     'hr-expense',      20),
    ('Attendance',               'oca-hr-attendance',  'hr-attendance',   30),
    ('Holidays',                 'oca-hr-holidays',    'hr-holidays',     40),
    ('Payroll',                  'oca-payroll',        'payroll',         50)
) AS x(title, slug, repo, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 6) SALES & CRM REPOSITORIES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'oca_repos'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'oca-sales'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'repo',
    x.title,
    x.slug,
    'https://github.com/OCA/' || x.repo || '/tree/18.0',
    x.sort_order,
    true,
    true,
    2
FROM parent
CROSS JOIN (VALUES
    ('Sale Workflow',            'oca-sale-workflow',     'sale-workflow',      10),
    ('CRM',                      'oca-crm',               'crm',                20),
    ('Contract',                 'oca-contract',          'contract',           30),
    ('Commission',               'oca-commission',        'commission',         40)
) AS x(title, slug, repo, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 7) SUPPLY CHAIN REPOSITORIES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'oca_repos'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'oca-supply-chain'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'repo',
    x.title,
    x.slug,
    'https://github.com/OCA/' || x.repo || '/tree/18.0',
    x.sort_order,
    true,
    true,
    2
FROM parent
CROSS JOIN (VALUES
    ('Stock Logistics Workflow', 'oca-stock-workflow',    'stock-logistics-workflow',      10),
    ('Stock Logistics Warehouse','oca-stock-warehouse',   'stock-logistics-warehouse',     20),
    ('Stock Logistics Barcode',  'oca-stock-barcode',     'stock-logistics-barcode',       30),
    ('Manufacturing',            'oca-manufacture',       'manufacture',                   40),
    ('MRP Multi Level',          'oca-mrp-multi-level',   'mrp-multi-level',               50)
) AS x(title, slug, repo, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 8) PURCHASE REPOSITORIES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'oca_repos'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'oca-purchase'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'repo',
    x.title,
    x.slug,
    'https://github.com/OCA/' || x.repo || '/tree/18.0',
    x.sort_order,
    true,
    true,
    2
FROM parent
CROSS JOIN (VALUES
    ('Purchase Workflow',        'oca-purchase-workflow', 'purchase-workflow',     10),
    ('Supplier Evaluation',      'oca-supplier-eval',     'supplier-evaluation',   20)
) AS x(title, slug, repo, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 9) WEBSITE REPOSITORIES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'oca_repos'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'oca-website'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'repo',
    x.title,
    x.slug,
    'https://github.com/OCA/' || x.repo || '/tree/18.0',
    x.sort_order,
    true,
    true,
    2
FROM parent
CROSS JOIN (VALUES
    ('Website',                  'oca-website-repo',      'website',           10),
    ('eCommerce',                'oca-e-commerce',        'e-commerce',        20)
) AS x(title, slug, repo, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 10) CONNECTOR REPOSITORIES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'oca_repos'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'oca-connectors'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'repo',
    x.title,
    x.slug,
    'https://github.com/OCA/' || x.repo || '/tree/18.0',
    x.sort_order,
    true,
    true,
    2
FROM parent
CROSS JOIN (VALUES
    ('Connector Framework',      'oca-connector',         'connector',         10),
    ('EDI',                      'oca-edi',               'edi',               20),
    ('REST Framework',           'oca-rest',              'rest-framework',    30)
) AS x(title, slug, repo, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 11) SERVER & TOOLS REPOSITORIES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'oca_repos'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'oca-server'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'repo',
    x.title,
    x.slug,
    'https://github.com/OCA/' || x.repo || '/tree/18.0',
    x.sort_order,
    true,
    true,
    2
FROM parent
CROSS JOIN (VALUES
    ('Server Tools',             'oca-server-tools',      'server-tools',      10),
    ('Server UX',                'oca-server-ux',         'server-ux',         20),
    ('Reporting Engine',         'oca-reporting',         'reporting-engine',  30),
    ('Queue Job',                'oca-queue',             'queue',             40)
) AS x(title, slug, repo, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 12) LOCALIZATION - PHILIPPINES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'oca_repos'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'oca-l10n'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'repo',
    x.title,
    x.slug,
    'https://github.com/OCA/' || x.repo || '/tree/18.0',
    x.sort_order,
    true,
    true,
    2
FROM parent
CROSS JOIN (VALUES
    ('Philippines',              'oca-l10n-ph',           'l10n-philippines',  10)
) AS x(title, slug, repo, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 13) QUEUE ALL LEAF NODES FOR HARVEST
-- =============================================================================

INSERT INTO kb.harvest_state (tenant_id, node_id, status, queued_at)
SELECT cn.tenant_id, cn.id, 'queued', now()
FROM kb.catalog_nodes cn
JOIN kb.catalog_sources cs ON cs.id = cn.source_id
WHERE cs.code = 'oca_repos'
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

SELECT 'OCA Catalog Sources:' AS info;
SELECT code, name, priority FROM kb.catalog_sources WHERE tenant_id = :'tenant_id'::uuid AND code = 'oca_repos';

SELECT 'OCA Node Counts by Kind:' AS info;
SELECT cn.kind, count(*)
FROM kb.catalog_nodes cn
JOIN kb.catalog_sources cs ON cs.id = cn.source_id
WHERE cn.tenant_id = :'tenant_id'::uuid AND cs.code = 'oca_repos'
GROUP BY cn.kind ORDER BY cn.kind;

SELECT 'OCA Harvest Queue:' AS info;
SELECT hs.status, count(*)
FROM kb.harvest_state hs
JOIN kb.catalog_nodes cn ON cn.id = hs.node_id
JOIN kb.catalog_sources cs ON cs.id = cn.source_id
WHERE hs.tenant_id = :'tenant_id'::uuid AND cs.code = 'oca_repos'
GROUP BY hs.status;

SELECT 'OCA Coverage Stats:' AS info;
SELECT * FROM kb.get_source_coverage('oca_repos');
