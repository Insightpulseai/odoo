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
     false, ARRAY[]::text[], ARRAY['odoo', 'navigate', 'menu']),

    -- Semantic Query Tools
    ('semantic.list_models', 'query', 'List Semantic Models',
     'List all available semantic models with their dimensions and metrics summary',
     '{"type": "object", "properties": {"asset_fqdn": {"type": "string", "description": "Optional asset FQDN to filter"}}, "required": []}'::jsonb,
     '{"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "label": {"type": "string"}, "dimension_count": {"type": "integer"}, "metric_count": {"type": "integer"}}}}'::jsonb,
     false, ARRAY[]::text[], ARRAY['semantic', 'discovery', 'query']),

    ('semantic.get_model_schema', 'query', 'Get Semantic Model Schema',
     'Get the full schema of a semantic model including all dimensions and metrics',
     '{"type": "object", "properties": {"asset_fqdn": {"type": "string", "description": "Asset FQDN"}, "model_name": {"type": "string", "description": "Semantic model name"}}, "required": ["asset_fqdn", "model_name"]}'::jsonb,
     '{"type": "object", "properties": {"model": {"type": "object"}, "dimensions": {"type": "array"}, "metrics": {"type": "array"}}}'::jsonb,
     false, ARRAY[]::text[], ARRAY['semantic', 'schema', 'query']),

    ('semantic.query', 'query', 'Query Semantic Model',
     'Run a semantic query with business-friendly dimensions and metrics. Returns SQL plan for execution.',
     '{"type": "object", "properties": {"asset_fqdn": {"type": "string"}, "model_name": {"type": "string"}, "dimensions": {"type": "array", "items": {"type": "string"}, "description": "Dimension names to group by"}, "metrics": {"type": "array", "items": {"type": "string"}, "description": "Metric names to calculate"}, "filters": {"type": "array", "items": {"type": "object", "properties": {"dimension": {"type": "string"}, "operator": {"type": "string", "enum": ["eq", "ne", "gt", "gte", "lt", "lte", "in", "not_in", "like", "between"]}, "value": {}}}}, "time_grain": {"type": "string", "enum": ["day", "week", "month", "quarter", "year"]}, "time_range": {"type": "object", "properties": {"start": {"type": "string", "format": "date"}, "end": {"type": "string", "format": "date"}}}, "limit": {"type": "integer", "default": 1000}}, "required": ["asset_fqdn", "model_name", "dimensions", "metrics"]}'::jsonb,
     '{"type": "object", "properties": {"ok": {"type": "boolean"}, "plan": {"type": "object", "properties": {"sql_preview": {"type": "string"}, "dimensions": {"type": "array"}, "metrics": {"type": "array"}}}}}'::jsonb,
     false, ARRAY[]::text[], ARRAY['semantic', 'analytics', 'query']),

    ('semantic.suggest_metrics', 'query', 'Suggest Metrics',
     'Given a user question, suggest relevant dimensions and metrics from available semantic models',
     '{"type": "object", "properties": {"question": {"type": "string", "description": "Natural language question"}, "asset_fqdn": {"type": "string", "description": "Optional asset FQDN to scope suggestions"}}, "required": ["question"]}'::jsonb,
     '{"type": "object", "properties": {"suggested_model": {"type": "string"}, "suggested_dimensions": {"type": "array"}, "suggested_metrics": {"type": "array"}, "reasoning": {"type": "string"}}}'::jsonb,
     false, ARRAY[]::text[], ARRAY['semantic', 'ai', 'suggestion']),

    ('semantic.import_osi', 'action', 'Import OSI Definition',
     'Import a semantic model definition in Open Semantics Interface (OSI) format',
     '{"type": "object", "properties": {"payload": {"type": "object", "description": "OSI-formatted semantic model definition"}}, "required": ["payload"]}'::jsonb,
     '{"type": "object", "properties": {"ok": {"type": "boolean"}, "model_id": {"type": "string"}, "stats": {"type": "object", "properties": {"dimensions": {"type": "integer"}, "metrics": {"type": "integer"}}}}}'::jsonb,
     true, ARRAY['base.group_system'], ARRAY['semantic', 'admin', 'import']),

    ('semantic.export_osi', 'query', 'Export OSI Definition',
     'Export a semantic model definition in Open Semantics Interface (OSI) format',
     '{"type": "object", "properties": {"asset_fqdn": {"type": "string"}, "model_name": {"type": "string"}, "format": {"type": "string", "enum": ["json", "yaml", "both"], "default": "json"}}, "required": ["asset_fqdn", "model_name"]}'::jsonb,
     '{"type": "object", "properties": {"ok": {"type": "boolean"}, "json": {"type": "object"}, "yaml": {"type": "string"}}}'::jsonb,
     false, ARRAY[]::text[], ARRAY['semantic', 'export', 'query']),

    -- Context Resolution Tool
    ('context.resolve', 'query', 'Resolve Platform Context',
     'Resolve tenant/account/project context to Odoo entity IDs (db, company, partner, project, analytic account)',
     '{"type": "object", "properties": {"tenant_id": {"type": "string", "format": "uuid", "description": "Tenant UUID"}, "account_id": {"type": "string", "format": "uuid", "description": "Account UUID (optional)"}, "project_id": {"type": "string", "format": "uuid", "description": "Project UUID (optional)"}, "environment_id": {"type": "string", "format": "uuid", "description": "Environment UUID (optional)"}}, "required": ["tenant_id"]}'::jsonb,
     '{"type": "object", "properties": {"ok": {"type": "boolean"}, "tenancy_mode": {"type": "string", "enum": ["multi_db", "multi_company"]}, "odoo_db": {"type": "string"}, "odoo_company_id": {"type": "integer"}, "odoo_partner_id": {"type": "integer"}, "odoo_project_id": {"type": "integer"}, "odoo_analytic_account_id": {"type": "integer"}}}'::jsonb,
     false, ARRAY[]::text[], ARRAY['context', 'odoo', 'resolution']),

    ('context.get_analytic_spine', 'query', 'Get Analytic Cost Spine',
     'Get analytic account details for cost tracking (bridges accounting ↔ projects ↔ timesheets)',
     '{"type": "object", "properties": {"tenant_id": {"type": "string", "format": "uuid"}, "odoo_db": {"type": "string"}, "analytic_id": {"type": "integer"}}, "required": ["tenant_id", "odoo_db", "analytic_id"]}'::jsonb,
     '{"type": "object", "properties": {"name": {"type": "string"}, "code": {"type": "string"}, "balance": {"type": "number"}, "debit": {"type": "number"}, "credit": {"type": "number"}, "plan_name": {"type": "string"}}}'::jsonb,
     false, ARRAY[]::text[], ARRAY['context', 'analytic', 'cost-spine'])

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

-- Semantic tool bindings
INSERT INTO catalog.tool_bindings (tool_id, target_type, target_config, priority)
SELECT
    t.id,
    'edge_function',
    '{"function_name": "semantic-export-osi", "method": "GET"}'::jsonb,
    0
FROM catalog.tools t WHERE t.tool_key = 'semantic.list_models'
ON CONFLICT DO NOTHING;

INSERT INTO catalog.tool_bindings (tool_id, target_type, target_config, priority)
SELECT
    t.id,
    'edge_function',
    '{"function_name": "semantic-export-osi", "method": "GET"}'::jsonb,
    0
FROM catalog.tools t WHERE t.tool_key = 'semantic.get_model_schema'
ON CONFLICT DO NOTHING;

INSERT INTO catalog.tool_bindings (tool_id, target_type, target_config, priority)
SELECT
    t.id,
    'edge_function',
    '{"function_name": "semantic-query", "method": "POST"}'::jsonb,
    0
FROM catalog.tools t WHERE t.tool_key = 'semantic.query'
ON CONFLICT DO NOTHING;

INSERT INTO catalog.tool_bindings (tool_id, target_type, target_config, priority)
SELECT
    t.id,
    'edge_function',
    '{"function_name": "semantic-import-osi", "method": "POST"}'::jsonb,
    0
FROM catalog.tools t WHERE t.tool_key = 'semantic.import_osi'
ON CONFLICT DO NOTHING;

INSERT INTO catalog.tool_bindings (tool_id, target_type, target_config, priority)
SELECT
    t.id,
    'edge_function',
    '{"function_name": "semantic-export-osi", "method": "GET"}'::jsonb,
    0
FROM catalog.tools t WHERE t.tool_key = 'semantic.export_osi'
ON CONFLICT DO NOTHING;

-- Context resolution tool bindings
INSERT INTO catalog.tool_bindings (tool_id, target_type, target_config, priority)
SELECT
    t.id,
    'edge_function',
    '{"function_name": "context-resolve", "method": "POST"}'::jsonb,
    0
FROM catalog.tools t WHERE t.tool_key = 'context.resolve'
ON CONFLICT DO NOTHING;

INSERT INTO catalog.tool_bindings (tool_id, target_type, target_config, priority)
SELECT
    t.id,
    'supabase_table',
    '{"schema": "ops", "table": "analytic_account_cache", "method": "select"}'::jsonb,
    0
FROM catalog.tools t WHERE t.tool_key = 'context.get_analytic_spine'
ON CONFLICT DO NOTHING;


-- -----------------------------------------------------------------------------
-- Semantic Model Assets (model type assets for semantic layer)
-- -----------------------------------------------------------------------------

INSERT INTO catalog.assets (fqdn, asset_type, system, title, description, owner, tags, uri, metadata)
VALUES
    -- Semantic models for Scout gold views
    ('supabase.ipai.scout_gold.sales_by_store.semantic.store_performance', 'model', 'scout',
     'Store Performance Model',
     'Semantic model for store-level KPI analysis with revenue, transactions, and growth metrics',
     'analytics_team', ARRAY['semantic', 'scout', 'kpi', 'store'],
     NULL,
     '{"source_fqdn": "supabase.ipai.scout_gold.sales_by_store", "dimension_count": 5, "metric_count": 6}'::jsonb),

    ('supabase.ipai.scout_gold.sales_by_product.semantic.product_performance', 'model', 'scout',
     'Product Performance Model',
     'Semantic model for product-level analysis with sales volume, revenue, and ranking metrics',
     'analytics_team', ARRAY['semantic', 'scout', 'kpi', 'product'],
     NULL,
     '{"source_fqdn": "supabase.ipai.scout_gold.sales_by_product", "dimension_count": 4, "metric_count": 5}'::jsonb),

    ('supabase.ipai.scout_gold.customer_360.semantic.customer_insights', 'model', 'scout',
     'Customer Insights Model',
     'Semantic model for customer lifetime value, segmentation, and behavior analysis',
     'analytics_team', ARRAY['semantic', 'scout', 'crm', 'clv'],
     NULL,
     '{"source_fqdn": "supabase.ipai.scout_gold.customer_360", "dimension_count": 4, "metric_count": 7}'::jsonb),

    -- Semantic model for Odoo finance
    ('odoo.odoo_core.account.move.semantic.invoice_analytics', 'model', 'odoo',
     'Invoice Analytics Model',
     'Semantic model for invoice and journal entry analysis with AR/AP aging metrics',
     'finance_team', ARRAY['semantic', 'odoo', 'finance', 'invoice'],
     NULL,
     '{"source_fqdn": "odoo.odoo_core.account.move", "dimension_count": 6, "metric_count": 8}'::jsonb),

    ('odoo.odoo_core.sale.order.semantic.sales_pipeline', 'model', 'odoo',
     'Sales Pipeline Model',
     'Semantic model for sales order analysis with conversion and revenue metrics',
     'sales_team', ARRAY['semantic', 'odoo', 'sales', 'pipeline'],
     NULL,
     '{"source_fqdn": "odoo.odoo_core.sale.order", "dimension_count": 5, "metric_count": 6}'::jsonb)

ON CONFLICT (fqdn) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    metadata = EXCLUDED.metadata,
    updated_at = now();


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


-- -----------------------------------------------------------------------------
-- Semantic Model Lineage Edges (Physical → Semantic)
-- -----------------------------------------------------------------------------

-- Scout gold views → Semantic models (derived_from)
INSERT INTO catalog.lineage_edges (from_asset_id, to_asset_id, edge_type, job_name, metadata)
SELECT
    f.id, t.id, 'derived_from', 'semantic_model_definition',
    '{"relationship": "physical_to_semantic", "auto_created": true}'::jsonb
FROM catalog.assets f, catalog.assets t
WHERE f.fqdn = 'supabase.ipai.scout_gold.sales_by_store'
  AND t.fqdn = 'supabase.ipai.scout_gold.sales_by_store.semantic.store_performance'
ON CONFLICT DO NOTHING;

INSERT INTO catalog.lineage_edges (from_asset_id, to_asset_id, edge_type, job_name, metadata)
SELECT
    f.id, t.id, 'derived_from', 'semantic_model_definition',
    '{"relationship": "physical_to_semantic", "auto_created": true}'::jsonb
FROM catalog.assets f, catalog.assets t
WHERE f.fqdn = 'supabase.ipai.scout_gold.sales_by_product'
  AND t.fqdn = 'supabase.ipai.scout_gold.sales_by_product.semantic.product_performance'
ON CONFLICT DO NOTHING;

INSERT INTO catalog.lineage_edges (from_asset_id, to_asset_id, edge_type, job_name, metadata)
SELECT
    f.id, t.id, 'derived_from', 'semantic_model_definition',
    '{"relationship": "physical_to_semantic", "auto_created": true}'::jsonb
FROM catalog.assets f, catalog.assets t
WHERE f.fqdn = 'supabase.ipai.scout_gold.customer_360'
  AND t.fqdn = 'supabase.ipai.scout_gold.customer_360.semantic.customer_insights'
ON CONFLICT DO NOTHING;

-- Odoo models → Semantic models (derived_from)
INSERT INTO catalog.lineage_edges (from_asset_id, to_asset_id, edge_type, job_name, metadata)
SELECT
    f.id, t.id, 'derived_from', 'semantic_model_definition',
    '{"relationship": "physical_to_semantic", "auto_created": true}'::jsonb
FROM catalog.assets f, catalog.assets t
WHERE f.fqdn = 'odoo.odoo_core.account.move'
  AND t.fqdn = 'odoo.odoo_core.account.move.semantic.invoice_analytics'
ON CONFLICT DO NOTHING;

INSERT INTO catalog.lineage_edges (from_asset_id, to_asset_id, edge_type, job_name, metadata)
SELECT
    f.id, t.id, 'derived_from', 'semantic_model_definition',
    '{"relationship": "physical_to_semantic", "auto_created": true}'::jsonb
FROM catalog.assets f, catalog.assets t
WHERE f.fqdn = 'odoo.odoo_core.sale.order'
  AND t.fqdn = 'odoo.odoo_core.sale.order.semantic.sales_pipeline'
ON CONFLICT DO NOTHING;


-- -----------------------------------------------------------------------------
-- Cross-System Lineage (Scout facts feed into Odoo semantic for unified view)
-- -----------------------------------------------------------------------------

-- Scout transactions influence invoice analytics (for reconciliation)
INSERT INTO catalog.lineage_edges (from_asset_id, to_asset_id, edge_type, job_name, metadata)
SELECT
    f.id, t.id, 'depends_on', 'cross_system_analytics',
    '{"relationship": "enrichment", "description": "Scout transaction data enriches invoice analytics"}'::jsonb
FROM catalog.assets f, catalog.assets t
WHERE f.fqdn = 'supabase.ipai.scout_fact.transactions'
  AND t.fqdn = 'odoo.odoo_core.account.move.semantic.invoice_analytics'
ON CONFLICT DO NOTHING;


COMMIT;

-- =============================================================================
-- End Seed: 9005 - Catalog Assets and Tools
-- =============================================================================
