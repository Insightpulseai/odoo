-- =============================================================================
-- SEED: Odoo Documentation Catalog
-- =============================================================================
-- Populates kb.catalog_sources and kb.catalog_nodes with the complete
-- Odoo 18.0 documentation hierarchy.
--
-- Usage:
--   psql -v tenant_id="'00000000-0000-0000-0000-000000000001'" -f seed_odoo_catalog.sql
--
-- Or in Supabase:
--   Replace :tenant_id with your actual tenant UUID
-- =============================================================================

-- Use a default tenant for development
\set tenant_id '00000000-0000-0000-0000-000000000001'

BEGIN;

-- =============================================================================
-- 1) CREATE SOURCE
-- =============================================================================

INSERT INTO kb.catalog_sources (tenant_id, code, name, base_url, description, priority, config)
VALUES (
    :'tenant_id'::uuid,
    'odoo_docs',
    'Odoo Documentation',
    'https://www.odoo.com/documentation/18.0/',
    'Official Odoo 18.0 documentation - User guides, Developer reference, Contributing guidelines',
    10,
    '{"version": "18.0", "language": "en"}'::jsonb
)
ON CONFLICT (tenant_id, code) DO UPDATE SET
    name = EXCLUDED.name,
    base_url = EXCLUDED.base_url,
    description = EXCLUDED.description,
    updated_at = now();

-- =============================================================================
-- 2) CREATE ROOT NODE
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'odoo_docs'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest)
SELECT
    :'tenant_id'::uuid,
    src.id,
    NULL,
    'space',
    'Odoo Documentation',
    'odoo-docs',
    'https://www.odoo.com/documentation/18.0/',
    0,
    false,
    false
FROM src
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    updated_at = now();

-- =============================================================================
-- 3) CREATE TOP-LEVEL SECTIONS
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'odoo_docs'
),
root AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'odoo-docs' AND cn.parent_id IS NULL
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest)
SELECT
    :'tenant_id'::uuid,
    root.source_id,
    root.id,
    'section',
    x.title,
    x.slug,
    x.url,
    x.sort_order,
    false,
    false
FROM root
CROSS JOIN (VALUES
    ('User Docs',       'user-docs',     'https://www.odoo.com/documentation/18.0/applications.html', 10),
    ('Developer',       'developer',     'https://www.odoo.com/documentation/18.0/developer.html',    20),
    ('Contributing',    'contributing',  'https://www.odoo.com/documentation/18.0/contributing.html', 30),
    ('Install/Maintain','install',       'https://www.odoo.com/documentation/18.0/administration.html', 40)
) AS x(title, slug, url, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    updated_at = now();

-- =============================================================================
-- 4) USER DOCS - APP CATEGORIES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'odoo_docs'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'user-docs'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'app',
    x.title,
    x.slug,
    'https://www.odoo.com/documentation/18.0/applications/' || x.url_path,
    x.sort_order,
    false,
    false
FROM parent
CROSS JOIN (VALUES
    ('Odoo Essentials',   'essentials',     'essentials.html',                    10),
    ('Finance',           'finance',        'finance.html',                       20),
    ('Sales',             'sales',          'sales.html',                         30),
    ('Websites',          'websites',       'websites.html',                      40),
    ('Supply Chain',      'supply-chain',   'inventory_and_mrp.html',             50),
    ('Human Resources',   'hr',             'hr.html',                            60),
    ('Marketing',         'marketing',      'marketing.html',                     70),
    ('Services',          'services',       'services.html',                      80),
    ('Productivity',      'productivity',   'productivity.html',                  90),
    ('Studio',            'studio',         'productivity/studio.html',          100),
    ('General Settings',  'settings',       'general.html',                      110)
) AS x(title, slug, url_path, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    updated_at = now();

-- =============================================================================
-- 5) FINANCE - MODULES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'odoo_docs'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'finance'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'page',
    x.title,
    x.slug,
    'https://www.odoo.com/documentation/18.0/applications/finance/' || x.url_path,
    x.sort_order,
    true,
    true,
    5
FROM parent
CROSS JOIN (VALUES
    ('Accounting',       'accounting',   'accounting.html',                 10),
    ('Invoicing',        'invoicing',    'accounting/customer_invoices.html', 20),
    ('Expenses',         'expenses',     'expenses.html',                   30),
    ('Documents',        'documents',    'documents.html',                  40),
    ('Sign',             'sign',         'sign.html',                       50)
) AS x(title, slug, url_path, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 6) SALES - MODULES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'odoo_docs'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'sales'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'page',
    x.title,
    x.slug,
    'https://www.odoo.com/documentation/18.0/applications/sales/' || x.url_path,
    x.sort_order,
    true,
    true,
    5
FROM parent
CROSS JOIN (VALUES
    ('CRM',              'crm',           'crm.html',                        10),
    ('Sales',            'sales-app',     'sales.html',                      20),
    ('Point of Sale',    'pos',           'point_of_sale.html',              30),
    ('Subscriptions',    'subscriptions', 'subscriptions.html',              40),
    ('Rental',           'rental',        'rental.html',                     50)
) AS x(title, slug, url_path, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 7) SUPPLY CHAIN - MODULES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'odoo_docs'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'supply-chain'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'page',
    x.title,
    x.slug,
    'https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/' || x.url_path,
    x.sort_order,
    true,
    true,
    5
FROM parent
CROSS JOIN (VALUES
    ('Inventory',        'inventory',     'inventory.html',                  10),
    ('Manufacturing',    'manufacturing', 'manufacturing.html',              20),
    ('Purchase',         'purchase',      'purchase.html',                   30),
    ('Barcode',          'barcode',       'barcode.html',                    40),
    ('Quality',          'quality',       'quality.html',                    50),
    ('Maintenance',      'maintenance',   'maintenance.html',                60),
    ('PLM',              'plm',           'plm.html',                        70)
) AS x(title, slug, url_path, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 8) HUMAN RESOURCES - MODULES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'odoo_docs'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'hr'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'page',
    x.title,
    x.slug,
    'https://www.odoo.com/documentation/18.0/applications/hr/' || x.url_path,
    x.sort_order,
    true,
    true,
    4
FROM parent
CROSS JOIN (VALUES
    ('Employees',        'employees',     'employees.html',                  10),
    ('Recruitment',      'recruitment',   'recruitment.html',                20),
    ('Time Off',         'time-off',      'time_off.html',                   30),
    ('Payroll',          'payroll',       'payroll.html',                    40),
    ('Attendances',      'attendances',   'attendances.html',                50),
    ('Referrals',        'referrals',     'referrals.html',                  60),
    ('Fleet',            'fleet',         'fleet.html',                      70)
) AS x(title, slug, url_path, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 9) WEBSITES - MODULES
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'odoo_docs'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'websites'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'page',
    x.title,
    x.slug,
    'https://www.odoo.com/documentation/18.0/applications/websites/' || x.url_path,
    x.sort_order,
    true,
    true,
    5
FROM parent
CROSS JOIN (VALUES
    ('Website',          'website',       'website.html',                    10),
    ('eCommerce',        'ecommerce',     'ecommerce.html',                  20),
    ('eLearning',        'elearning',     'elearning.html',                  30),
    ('Forum',            'forum',         'forum.html',                      40),
    ('Blog',             'blog',          'blog.html',                       50),
    ('Live Chat',        'livechat',      'livechat.html',                   60)
) AS x(title, slug, url_path, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 10) INSTALL/MAINTAIN - HOSTING & ADMIN
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'odoo_docs'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'install'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'page',
    x.title,
    x.slug,
    'https://www.odoo.com/documentation/18.0/administration/' || x.url_path,
    x.sort_order,
    true,
    true,
    4
FROM parent
CROSS JOIN (VALUES
    ('Odoo Online',              'odoo-online',        'odoo_online.html',          10),
    ('Odoo.sh',                  'odoo-sh',            'odoo_sh.html',              20),
    ('On-Premise',               'on-premise',         'on_premise.html',           30),
    ('Upgrade',                  'upgrade',            'upgrade.html',              40),
    ('Neutralized Database',     'neutralized',        'neutralized_database.html', 50),
    ('Database Management',      'db-management',      'maintain.html',             60),
    ('Standard Support',         'support-std',        'maintain/enterprise_support.html', 70),
    ('Mobile Apps',              'mobile',             'mobile.html',               80),
    ('Odoo.com Account',         'odoo-account',       'odoo_accounts.html',        90)
) AS x(title, slug, url_path, sort_order)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 11) DEVELOPER SECTION
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'odoo_docs'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'developer'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'page',
    x.title,
    x.slug,
    'https://www.odoo.com/documentation/18.0/developer/' || x.url_path,
    x.sort_order,
    true,
    true,
    x.depth
FROM parent
CROSS JOIN (VALUES
    ('Tutorials',        'tutorials',     'tutorials.html',                  10, 8),
    ('How-to Guides',    'howtos',        'howtos.html',                     20, 6),
    ('Reference',        'reference',     'reference.html',                  30, 8),
    ('External API',     'external-api',  'reference/external_api.html',     40, 5)
) AS x(title, slug, url_path, sort_order, depth)
ON CONFLICT (tenant_id, source_id, slug) DO UPDATE SET
    title = EXCLUDED.title,
    external_url = EXCLUDED.external_url,
    is_leaf = true,
    should_harvest = true,
    updated_at = now();

-- =============================================================================
-- 12) CONTRIBUTING SECTION
-- =============================================================================

WITH src AS (
    SELECT id FROM kb.catalog_sources
    WHERE tenant_id = :'tenant_id'::uuid AND code = 'odoo_docs'
),
parent AS (
    SELECT cn.id, cn.source_id
    FROM kb.catalog_nodes cn
    JOIN src ON src.id = cn.source_id
    WHERE cn.slug = 'contributing'
)
INSERT INTO kb.catalog_nodes (tenant_id, source_id, parent_id, kind, title, slug, external_url, sort_order, is_leaf, should_harvest, crawl_depth)
SELECT
    :'tenant_id'::uuid,
    parent.source_id,
    parent.id,
    'page',
    x.title,
    x.slug,
    'https://www.odoo.com/documentation/18.0/contributing/' || x.url_path,
    x.sort_order,
    true,
    true,
    4
FROM parent
CROSS JOIN (VALUES
    ('Coding Guidelines',     'coding',          'development.html',         10),
    ('Documentation',         'documentation',   'documentation.html',       20),
    ('Content Guidelines',    'content',         'content.html',             30)
) AS x(title, slug, url_path, sort_order)
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
WHERE cs.code = 'odoo_docs'
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

SELECT 'Catalog Sources:' AS info;
SELECT code, name, priority FROM kb.catalog_sources WHERE tenant_id = :'tenant_id'::uuid;

SELECT 'Node Counts by Kind:' AS info;
SELECT kind, count(*) FROM kb.catalog_nodes
WHERE tenant_id = :'tenant_id'::uuid
GROUP BY kind ORDER BY kind;

SELECT 'Harvest Queue:' AS info;
SELECT status, count(*) FROM kb.harvest_state
WHERE tenant_id = :'tenant_id'::uuid
GROUP BY status;

SELECT 'Coverage Stats:' AS info;
SELECT * FROM kb.get_source_coverage('odoo_docs');
