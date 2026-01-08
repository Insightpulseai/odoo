-- =============================================================================
-- Seed: 9005 - Catalog Assets and Tools
-- Purpose: Initial asset registry and tool definitions for ipai_ask_ai
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- Core Odoo Models (odoo.odoo_core.*)
-- -----------------------------------------------------------------------------

INSERT INTO catalog.assets (fqdn, asset_type, system, title, description, owner, tags, uri, metadata)
VALUES
    -- Finance/Accounting Models
    ('odoo.odoo_core.account.move', 'odoo_model', 'odoo', 'Journal Entry / Invoice',
     'Core accounting document: invoices, bills, journal entries, credit notes',
     'finance_team', ARRAY['finance', 'accounting', 'core'],
     '/web#model=account.move&view_type=list',
     '{"fields": ["name", "partner_id", "invoice_date", "amount_total", "state", "move_type"], "key_states": ["draft", "posted", "cancel"]}'::jsonb),

    ('odoo.odoo_core.account.move.line', 'odoo_model', 'odoo', 'Journal Item',
     'Individual line items on journal entries with debit/credit amounts',
     'finance_team', ARRAY['finance', 'accounting', 'detail'],
     '/web#model=account.move.line&view_type=list',
     '{"fields": ["move_id", "account_id", "partner_id", "debit", "credit", "balance", "reconciled"]}'::jsonb),

    ('odoo.odoo_core.account.account', 'odoo_model', 'odoo', 'Chart of Accounts',
     'Account codes for general ledger classification',
     'finance_team', ARRAY['finance', 'accounting', 'master'],
     '/web#model=account.account&view_type=list',
     '{"fields": ["code", "name", "account_type", "reconcile", "deprecated"]}'::jsonb),

    ('odoo.odoo_core.account.payment', 'odoo_model', 'odoo', 'Payment',
     'Customer payments and vendor disbursements',
     'finance_team', ARRAY['finance', 'treasury', 'core'],
     '/web#model=account.payment&view_type=list',
     '{"fields": ["name", "partner_id", "amount", "payment_type", "state", "date"]}'::jsonb),

    -- CRM / Sales Models
    ('odoo.odoo_core.res.partner', 'odoo_model', 'odoo', 'Contact / Partner',
     'Customers, vendors, and contacts master data',
     'operations_team', ARRAY['crm', 'master', 'core'],
     '/web#model=res.partner&view_type=kanban',
     '{"fields": ["name", "email", "phone", "is_company", "customer_rank", "supplier_rank", "country_id"]}'::jsonb),

    ('odoo.odoo_core.sale.order', 'odoo_model', 'odoo', 'Sales Order',
     'Quotations and confirmed sales orders',
     'sales_team', ARRAY['sales', 'revenue', 'core'],
     '/web#model=sale.order&view_type=list',
     '{"fields": ["name", "partner_id", "date_order", "amount_total", "state"], "key_states": ["draft", "sent", "sale", "done", "cancel"]}'::jsonb),

    ('odoo.odoo_core.crm.lead', 'odoo_model', 'odoo', 'Lead / Opportunity',
     'Sales pipeline leads and opportunities',
     'sales_team', ARRAY['crm', 'sales', 'pipeline'],
     '/web#model=crm.lead&view_type=kanban',
     '{"fields": ["name", "partner_id", "expected_revenue", "probability", "stage_id", "user_id"]}'::jsonb),

    -- Purchasing Models
    ('odoo.odoo_core.purchase.order', 'odoo_model', 'odoo', 'Purchase Order',
     'Vendor purchase orders and RFQs',
     'procurement_team', ARRAY['purchasing', 'procurement', 'core'],
     '/web#model=purchase.order&view_type=list',
     '{"fields": ["name", "partner_id", "date_order", "amount_total", "state"], "key_states": ["draft", "sent", "to approve", "purchase", "done", "cancel"]}'::jsonb),

    -- HR / Expense Models
    ('odoo.odoo_core.hr.expense', 'odoo_model', 'odoo', 'Expense',
     'Employee expense claims and reimbursements',
     'hr_team', ARRAY['hr', 'expense', 'reimbursement'],
     '/web#model=hr.expense&view_type=list',
     '{"fields": ["name", "employee_id", "total_amount", "state", "date"], "key_states": ["draft", "reported", "approved", "done", "refused"]}'::jsonb),

    ('odoo.odoo_core.hr.expense.sheet', 'odoo_model', 'odoo', 'Expense Report',
     'Grouped expense submission sheets',
     'hr_team', ARRAY['hr', 'expense', 'approval'],
     '/web#model=hr.expense.sheet&view_type=list',
     '{"fields": ["name", "employee_id", "total_amount", "state", "accounting_date"]}'::jsonb),

    -- Project Models
    ('odoo.odoo_core.project.project', 'odoo_model', 'odoo', 'Project',
     'Project management containers',
     'project_team', ARRAY['project', 'management', 'core'],
     '/web#model=project.project&view_type=kanban',
     '{"fields": ["name", "partner_id", "user_id", "date_start", "date", "stage_id"]}'::jsonb),

    ('odoo.odoo_core.project.task', 'odoo_model', 'odoo', 'Task',
     'Project tasks and work items',
     'project_team', ARRAY['project', 'task', 'work'],
     '/web#model=project.task&view_type=kanban',
     '{"fields": ["name", "project_id", "user_ids", "date_deadline", "stage_id", "priority"]}'::jsonb)

ON CONFLICT (fqdn) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    metadata = EXCLUDED.metadata,
    updated_at = now();


-- -----------------------------------------------------------------------------
-- Scout Medallion Assets (supabase.ipai.scout.*)
-- -----------------------------------------------------------------------------

INSERT INTO catalog.assets (fqdn, asset_type, system, title, description, owner, tags, uri, metadata)
VALUES
    -- Dimensions
    ('supabase.ipai.scout_dim.stores', 'table', 'scout', 'Stores Dimension',
     'Retail store master data with location and attributes',
     'analytics_team', ARRAY['scout', 'dimension', 'retail'],
     NULL,
     '{"columns": ["store_id", "store_name", "region", "city", "format", "open_date", "is_active"]}'::jsonb),

    ('supabase.ipai.scout_dim.products', 'table', 'scout', 'Products Dimension',
     'Product catalog with categories and attributes',
     'analytics_team', ARRAY['scout', 'dimension', 'retail'],
     NULL,
     '{"columns": ["product_id", "product_name", "category", "subcategory", "brand", "unit_price"]}'::jsonb),

    ('supabase.ipai.scout_dim.customers', 'table', 'scout', 'Customers Dimension',
     'Customer master data with segments',
     'analytics_team', ARRAY['scout', 'dimension', 'crm'],
     NULL,
     '{"columns": ["customer_id", "customer_name", "segment", "tier", "acquisition_date"]}'::jsonb),

    -- Facts
    ('supabase.ipai.scout_fact.transactions', 'table', 'scout', 'Transactions Fact',
     'Point-of-sale transaction records',
     'analytics_team', ARRAY['scout', 'fact', 'sales'],
     NULL,
     '{"columns": ["transaction_id", "store_id", "customer_id", "transaction_date", "total_amount", "item_count"]}'::jsonb),

    ('supabase.ipai.scout_fact.daily_sales', 'table', 'scout', 'Daily Sales Fact',
     'Aggregated daily sales by store and product',
     'analytics_team', ARRAY['scout', 'fact', 'aggregation'],
     NULL,
     '{"columns": ["date", "store_id", "product_id", "quantity_sold", "revenue", "cost", "margin"]}'::jsonb),

    -- Gold Views
    ('supabase.ipai.scout_gold.sales_by_store', 'view', 'scout', 'Sales by Store',
     'Store performance summary with KPIs',
     'analytics_team', ARRAY['scout', 'gold', 'kpi'],
     NULL,
     '{"columns": ["store_id", "store_name", "total_revenue", "total_transactions", "avg_basket_size", "yoy_growth"]}'::jsonb),

    ('supabase.ipai.scout_gold.sales_by_product', 'view', 'scout', 'Sales by Product',
     'Product performance with ranking',
     'analytics_team', ARRAY['scout', 'gold', 'kpi'],
     NULL,
     '{"columns": ["product_id", "product_name", "category", "total_quantity", "total_revenue", "margin_pct", "rank"]}'::jsonb),

    ('supabase.ipai.scout_gold.customer_360', 'view', 'scout', 'Customer 360',
     'Customer lifetime value and behavior summary',
     'analytics_team', ARRAY['scout', 'gold', 'crm'],
     NULL,
     '{"columns": ["customer_id", "customer_name", "segment", "total_spend", "order_count", "avg_order_value", "recency_days", "clv"]}'::jsonb)

ON CONFLICT (fqdn) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    metadata = EXCLUDED.metadata,
    updated_at = now();


-- -----------------------------------------------------------------------------
-- Tools for ipai_ask_ai Copilot
-- -----------------------------------------------------------------------------

INSERT INTO catalog.tools (tool_key, tool_type, name, description, parameters, returns, requires_confirmation, allowed_roles, tags)
VALUES
    -- Query Tools (read-only)
    ('catalog.search_assets', 'query', 'Search Catalog',
     'Search for data assets, Odoo models, and analytics views in the catalog',
     '{"type": "object", "properties": {"query": {"type": "string", "description": "Search query"}, "asset_type": {"type": "string", "enum": ["table", "view", "odoo_model", "odoo_action"]}, "system": {"type": "string", "enum": ["odoo", "supabase", "scout"]}}, "required": ["query"]}'::jsonb,
     '{"type": "array", "items": {"type": "object", "properties": {"fqdn": {"type": "string"}, "title": {"type": "string"}, "description": {"type": "string"}}}}'::jsonb,
     false, ARRAY[]::text[], ARRAY['catalog', 'search', 'discovery']),

    ('odoo.search_records', 'query', 'Search Odoo Records',
     'Search for records in any Odoo model by domain filter',
     '{"type": "object", "properties": {"model": {"type": "string", "description": "Odoo model name (e.g., account.move)"}, "domain": {"type": "array", "description": "Odoo domain filter"}, "fields": {"type": "array", "items": {"type": "string"}}, "limit": {"type": "integer", "default": 10}}, "required": ["model"]}'::jsonb,
     '{"type": "array", "items": {"type": "object"}}'::jsonb,
     false, ARRAY[]::text[], ARRAY['odoo', 'search', 'query']),

    ('odoo.read_record', 'query', 'Read Odoo Record',
     'Read a specific Odoo record by ID',
     '{"type": "object", "properties": {"model": {"type": "string"}, "id": {"type": "integer"}, "fields": {"type": "array", "items": {"type": "string"}}}, "required": ["model", "id"]}'::jsonb,
     '{"type": "object"}'::jsonb,
     false, ARRAY[]::text[], ARRAY['odoo', 'read', 'detail']),

    ('scout.query_analytics', 'query', 'Query Scout Analytics',
     'Run analytics queries on Scout gold layer views',
     '{"type": "object", "properties": {"view": {"type": "string", "description": "Gold view name (e.g., sales_by_store)"}, "filters": {"type": "object"}, "group_by": {"type": "array", "items": {"type": "string"}}, "order_by": {"type": "string"}, "limit": {"type": "integer", "default": 100}}, "required": ["view"]}'::jsonb,
     '{"type": "array", "items": {"type": "object"}}'::jsonb,
     false, ARRAY[]::text[], ARRAY['scout', 'analytics', 'query']),

    -- Action Tools (require confirmation)
    ('odoo.create_record', 'action', 'Create Odoo Record',
     'Create a new record in any Odoo model',
     '{"type": "object", "properties": {"model": {"type": "string"}, "values": {"type": "object"}}, "required": ["model", "values"]}'::jsonb,
     '{"type": "object", "properties": {"id": {"type": "integer"}, "display_name": {"type": "string"}}}'::jsonb,
     true, ARRAY['base.group_user'], ARRAY['odoo', 'create', 'write']),

    ('odoo.update_record', 'action', 'Update Odoo Record',
     'Update an existing Odoo record',
     '{"type": "object", "properties": {"model": {"type": "string"}, "id": {"type": "integer"}, "values": {"type": "object"}}, "required": ["model", "id", "values"]}'::jsonb,
     '{"type": "object", "properties": {"success": {"type": "boolean"}}}'::jsonb,
     true, ARRAY['base.group_user'], ARRAY['odoo', 'update', 'write']),

    ('odoo.execute_action', 'action', 'Execute Odoo Action',
     'Execute a server action or method on Odoo records',
     '{"type": "object", "properties": {"model": {"type": "string"}, "method": {"type": "string"}, "ids": {"type": "array", "items": {"type": "integer"}}, "args": {"type": "array"}, "kwargs": {"type": "object"}}, "required": ["model", "method", "ids"]}'::jsonb,
     '{"type": "object"}'::jsonb,
     true, ARRAY['base.group_user'], ARRAY['odoo', 'action', 'execute']),

    ('odoo.post_invoice', 'action', 'Post Invoice',
     'Post a draft invoice or bill to the general ledger',
     '{"type": "object", "properties": {"invoice_id": {"type": "integer"}}, "required": ["invoice_id"]}'::jsonb,
     '{"type": "object", "properties": {"success": {"type": "boolean"}, "move_name": {"type": "string"}}}'::jsonb,
     true, ARRAY['account.group_account_invoice'], ARRAY['odoo', 'accounting', 'post']),

    ('odoo.register_payment', 'action', 'Register Payment',
     'Register a payment for an invoice or bill',
     '{"type": "object", "properties": {"invoice_id": {"type": "integer"}, "amount": {"type": "number"}, "payment_date": {"type": "string", "format": "date"}, "journal_id": {"type": "integer"}}, "required": ["invoice_id"]}'::jsonb,
     '{"type": "object", "properties": {"payment_id": {"type": "integer"}, "payment_name": {"type": "string"}}}'::jsonb,
     true, ARRAY['account.group_account_invoice'], ARRAY['odoo', 'accounting', 'payment']),

    ('odoo.approve_expense', 'action', 'Approve Expense Report',
     'Approve an employee expense report',
     '{"type": "object", "properties": {"expense_sheet_id": {"type": "integer"}}, "required": ["expense_sheet_id"]}'::jsonb,
     '{"type": "object", "properties": {"success": {"type": "boolean"}}}'::jsonb,
     true, ARRAY['hr_expense.group_hr_expense_team_approver'], ARRAY['odoo', 'hr', 'approval']),

    -- Navigation Tools
    ('odoo.open_record', 'action', 'Open Record in Odoo',
     'Generate a deep link to open a record in Odoo',
     '{"type": "object", "properties": {"model": {"type": "string"}, "id": {"type": "integer"}, "view_type": {"type": "string", "enum": ["form", "list", "kanban"], "default": "form"}}, "required": ["model", "id"]}'::jsonb,
     '{"type": "object", "properties": {"url": {"type": "string"}}}'::jsonb,
     false, ARRAY[]::text[], ARRAY['odoo', 'navigate', 'link']),

    ('odoo.open_action', 'action', 'Open Odoo Action',
     'Navigate to an Odoo menu action',
     '{"type": "object", "properties": {"action_xmlid": {"type": "string"}, "context": {"type": "object"}}, "required": ["action_xmlid"]}'::jsonb,
     '{"type": "object", "properties": {"url": {"type": "string"}}}'::jsonb,
     false, ARRAY[]::text[], ARRAY['odoo', 'navigate', 'menu'])

ON CONFLICT (tool_key) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    parameters = EXCLUDED.parameters,
    returns = EXCLUDED.returns,
    requires_confirmation = EXCLUDED.requires_confirmation,
    updated_at = now();


-- -----------------------------------------------------------------------------
-- Tool Bindings (Map tools to execution targets)
-- -----------------------------------------------------------------------------

INSERT INTO catalog.tool_bindings (tool_id, target_type, target_config, priority)
SELECT
    t.id,
    'odoo_rpc',
    '{"model": "ir.model", "method": "search_read", "endpoint": "/web/dataset/call_kw"}'::jsonb,
    0
FROM catalog.tools t WHERE t.tool_key = 'odoo.search_records'
ON CONFLICT DO NOTHING;

INSERT INTO catalog.tool_bindings (tool_id, target_type, target_config, priority)
SELECT
    t.id,
    'odoo_rpc',
    '{"model": "ir.model", "method": "read", "endpoint": "/web/dataset/call_kw"}'::jsonb,
    0
FROM catalog.tools t WHERE t.tool_key = 'odoo.read_record'
ON CONFLICT DO NOTHING;

INSERT INTO catalog.tool_bindings (tool_id, target_type, target_config, priority)
SELECT
    t.id,
    'odoo_rpc',
    '{"model": "ir.model", "method": "create", "endpoint": "/web/dataset/call_kw"}'::jsonb,
    0
FROM catalog.tools t WHERE t.tool_key = 'odoo.create_record'
ON CONFLICT DO NOTHING;

INSERT INTO catalog.tool_bindings (tool_id, target_type, target_config, priority)
SELECT
    t.id,
    'odoo_rpc',
    '{"model": "ir.model", "method": "write", "endpoint": "/web/dataset/call_kw"}'::jsonb,
    0
FROM catalog.tools t WHERE t.tool_key = 'odoo.update_record'
ON CONFLICT DO NOTHING;

INSERT INTO catalog.tool_bindings (tool_id, target_type, target_config, priority)
SELECT
    t.id,
    'odoo_rpc',
    '{"model": "account.move", "method": "action_post", "endpoint": "/web/dataset/call_kw"}'::jsonb,
    0
FROM catalog.tools t WHERE t.tool_key = 'odoo.post_invoice'
ON CONFLICT DO NOTHING;

INSERT INTO catalog.tool_bindings (tool_id, target_type, target_config, priority)
SELECT
    t.id,
    'edge_function',
    '{"function_name": "ipai-copilot", "action": "scout_query"}'::jsonb,
    0
FROM catalog.tools t WHERE t.tool_key = 'scout.query_analytics'
ON CONFLICT DO NOTHING;


-- -----------------------------------------------------------------------------
-- Sample Lineage Edges
-- -----------------------------------------------------------------------------

-- Scout bronze → silver → gold lineage
INSERT INTO catalog.lineage_edges (from_asset_id, to_asset_id, edge_type, job_name)
SELECT
    f.id, t.id, 'derived_from', 'scout_etl_daily'
FROM catalog.assets f, catalog.assets t
WHERE f.fqdn = 'supabase.ipai.scout_fact.transactions'
  AND t.fqdn = 'supabase.ipai.scout_gold.sales_by_store'
ON CONFLICT DO NOTHING;

INSERT INTO catalog.lineage_edges (from_asset_id, to_asset_id, edge_type, job_name)
SELECT
    f.id, t.id, 'derived_from', 'scout_etl_daily'
FROM catalog.assets f, catalog.assets t
WHERE f.fqdn = 'supabase.ipai.scout_fact.daily_sales'
  AND t.fqdn = 'supabase.ipai.scout_gold.sales_by_product'
ON CONFLICT DO NOTHING;

-- Odoo → Scout sync lineage
INSERT INTO catalog.lineage_edges (from_asset_id, to_asset_id, edge_type, job_name)
SELECT
    f.id, t.id, 'writes_to', 'odoo_scout_sync'
FROM catalog.assets f, catalog.assets t
WHERE f.fqdn = 'odoo.odoo_core.sale.order'
  AND t.fqdn = 'supabase.ipai.scout_fact.transactions'
ON CONFLICT DO NOTHING;


COMMIT;

-- =============================================================================
-- End Seed: 9005 - Catalog Assets and Tools
-- =============================================================================
