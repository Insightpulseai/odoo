-- Migration: Create Domain Schemas and Tables
-- Version: 202512070001
-- Description: Create all domain schemas and core tables for InsightPulseAI
-- Author: Platform Team
-- Date: 2025-12-07

-- ============================================================================
-- PHASE 1: CREATE SCHEMAS
-- ============================================================================

-- Core / Infrastructure
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS saas;
CREATE SCHEMA IF NOT EXISTS logs;
CREATE SCHEMA IF NOT EXISTS mcp;

-- Finance Domain
CREATE SCHEMA IF NOT EXISTS expense;
CREATE SCHEMA IF NOT EXISTS teq;
CREATE SCHEMA IF NOT EXISTS projects;
CREATE SCHEMA IF NOT EXISTS finance;
CREATE SCHEMA IF NOT EXISTS rates;
CREATE SCHEMA IF NOT EXISTS ref;

-- Document Processing
CREATE SCHEMA IF NOT EXISTS doc;

-- Intelligence
CREATE SCHEMA IF NOT EXISTS rag;
CREATE SCHEMA IF NOT EXISTS ai;
CREATE SCHEMA IF NOT EXISTS agents;

-- Retail Domain (Medallion)
CREATE SCHEMA IF NOT EXISTS scout_bronze;
CREATE SCHEMA IF NOT EXISTS scout_silver;
CREATE SCHEMA IF NOT EXISTS scout_gold;
CREATE SCHEMA IF NOT EXISTS scout_dim;
CREATE SCHEMA IF NOT EXISTS scout_fact;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS dim;
CREATE SCHEMA IF NOT EXISTS intel;

-- Shared Caches
CREATE SCHEMA IF NOT EXISTS gold;
CREATE SCHEMA IF NOT EXISTS platinum;

-- ============================================================================
-- PHASE 2: CORE UTILITY FUNCTIONS
-- ============================================================================

-- Tenant context function
CREATE OR REPLACE FUNCTION core.current_tenant_id()
RETURNS uuid AS $$
    SELECT NULLIF(current_setting('app.current_tenant_id', true), '')::uuid;
$$ LANGUAGE sql STABLE;

-- Updated timestamp trigger function
CREATE OR REPLACE FUNCTION core.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PHASE 3: CORE TABLES
-- ============================================================================

-- Tenants table (foundation for all RLS)
CREATE TABLE IF NOT EXISTS core.tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted')),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_tenants_slug ON core.tenants(slug) WHERE deleted_at IS NULL;

-- Employees table (synced from Odoo hr.employee)
CREATE TABLE IF NOT EXISTS core.employees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    odoo_id INTEGER,
    email TEXT NOT NULL,
    name TEXT NOT NULL,
    department TEXT,
    job_title TEXT,
    manager_id UUID REFERENCES core.employees(id),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

ALTER TABLE core.employees ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON core.employees FOR ALL USING (tenant_id = core.current_tenant_id());
CREATE INDEX IF NOT EXISTS idx_employees_tenant ON core.employees(tenant_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_employees_email ON core.employees(tenant_id, email) WHERE deleted_at IS NULL;

-- ============================================================================
-- PHASE 4: EXPENSE DOMAIN TABLES
-- ============================================================================

-- Expense Reports (header level)
CREATE TABLE IF NOT EXISTS expense.expense_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    employee_id UUID NOT NULL REFERENCES core.employees(id),
    report_number TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected', 'paid')),
    total_amount NUMERIC(15,2) NOT NULL DEFAULT 0,
    currency TEXT NOT NULL DEFAULT 'PHP',
    submitted_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    approved_by UUID REFERENCES core.employees(id),
    policy_flagged BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

ALTER TABLE expense.expense_reports ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON expense.expense_reports FOR ALL USING (tenant_id = core.current_tenant_id());
CREATE INDEX IF NOT EXISTS idx_expense_reports_tenant_status ON expense.expense_reports(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_expense_reports_employee ON expense.expense_reports(tenant_id, employee_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_expense_reports_number ON expense.expense_reports(tenant_id, report_number) WHERE deleted_at IS NULL;

-- Expense Lines
CREATE TABLE IF NOT EXISTS expense.expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    expense_report_id UUID NOT NULL REFERENCES expense.expense_reports(id),
    line_seq INTEGER NOT NULL,
    category_code TEXT NOT NULL,
    description TEXT,
    amount NUMERIC(15,2) NOT NULL,
    currency TEXT NOT NULL DEFAULT 'PHP',
    spend_date DATE NOT NULL,
    receipt_document_id UUID,
    policy_violation TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

ALTER TABLE expense.expenses ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON expense.expenses FOR ALL USING (tenant_id = core.current_tenant_id());
CREATE INDEX IF NOT EXISTS idx_expenses_report ON expense.expenses(expense_report_id);
CREATE INDEX IF NOT EXISTS idx_expenses_category_date ON expense.expenses(tenant_id, category_code, spend_date);

-- Cash Advances
CREATE TABLE IF NOT EXISTS expense.cash_advances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    employee_id UUID NOT NULL REFERENCES core.employees(id),
    advance_number TEXT NOT NULL,
    amount NUMERIC(15,2) NOT NULL,
    currency TEXT NOT NULL DEFAULT 'PHP',
    purpose TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'disbursed', 'reconciled', 'cancelled')),
    trip_start_date DATE,
    trip_end_date DATE,
    reconciled_amount NUMERIC(15,2) DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

ALTER TABLE expense.cash_advances ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON expense.cash_advances FOR ALL USING (tenant_id = core.current_tenant_id());
CREATE INDEX IF NOT EXISTS idx_cash_advances_employee ON expense.cash_advances(tenant_id, employee_id);

-- ============================================================================
-- PHASE 5: PROJECTS DOMAIN TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS projects.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    odoo_id INTEGER,
    project_code TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('draft', 'active', 'on_hold', 'completed', 'cancelled')),
    start_date DATE,
    end_date DATE,
    budget_amount NUMERIC(15,2),
    budget_currency TEXT DEFAULT 'PHP',
    project_manager_id UUID REFERENCES core.employees(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

ALTER TABLE projects.projects ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON projects.projects FOR ALL USING (tenant_id = core.current_tenant_id());
CREATE INDEX IF NOT EXISTS idx_projects_tenant_status ON projects.projects(tenant_id, status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_projects_code ON projects.projects(tenant_id, project_code) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS projects.project_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    project_id UUID NOT NULL REFERENCES projects.projects(id),
    employee_id UUID NOT NULL REFERENCES core.employees(id),
    role TEXT NOT NULL,
    allocation_percent NUMERIC(5,2) DEFAULT 100,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE projects.project_members ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON projects.project_members FOR ALL USING (tenant_id = core.current_tenant_id());
CREATE INDEX IF NOT EXISTS idx_project_members_project ON projects.project_members(project_id);

-- ============================================================================
-- PHASE 6: RATES DOMAIN TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS rates.vendor_profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    odoo_partner_id INTEGER,
    vendor_code TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    rating NUMERIC(3,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

ALTER TABLE rates.vendor_profile ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON rates.vendor_profile FOR ALL USING (tenant_id = core.current_tenant_id());
CREATE UNIQUE INDEX IF NOT EXISTS idx_vendor_code ON rates.vendor_profile(tenant_id, vendor_code) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS rates.rate_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    vendor_id UUID NOT NULL REFERENCES rates.vendor_profile(id),
    rate_card_code TEXT NOT NULL,
    name TEXT NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'pending_approval', 'approved', 'expired', 'superseded')),
    approved_by UUID REFERENCES core.employees(id),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

ALTER TABLE rates.rate_cards ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON rates.rate_cards FOR ALL USING (tenant_id = core.current_tenant_id());
CREATE INDEX IF NOT EXISTS idx_rate_cards_vendor ON rates.rate_cards(vendor_id);
CREATE INDEX IF NOT EXISTS idx_rate_cards_effective ON rates.rate_cards(tenant_id, effective_from, effective_to);

-- ============================================================================
-- PHASE 7: DOCUMENT PROCESSING TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS doc.raw_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    source_hash TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size_bytes BIGINT,
    storage_path TEXT NOT NULL,
    uploaded_by UUID REFERENCES core.employees(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE doc.raw_documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON doc.raw_documents FOR ALL USING (tenant_id = core.current_tenant_id());
CREATE INDEX IF NOT EXISTS idx_raw_documents_tenant ON doc.raw_documents(tenant_id, created_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_raw_documents_hash ON doc.raw_documents(tenant_id, source_hash);

CREATE TABLE IF NOT EXISTS doc.parsed_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    raw_document_id UUID NOT NULL REFERENCES doc.raw_documents(id),
    parser_profile TEXT NOT NULL,
    doc_type TEXT NOT NULL,
    parsed_data JSONB NOT NULL,
    confidence_score NUMERIC(5,4),
    status TEXT NOT NULL DEFAULT 'parsed' CHECK (status IN ('parsing', 'parsed', 'failed', 'reviewed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE doc.parsed_documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON doc.parsed_documents FOR ALL USING (tenant_id = core.current_tenant_id());
CREATE INDEX IF NOT EXISTS idx_parsed_documents_raw ON doc.parsed_documents(raw_document_id);
CREATE INDEX IF NOT EXISTS idx_parsed_documents_type_status ON doc.parsed_documents(tenant_id, doc_type, status);

-- ============================================================================
-- PHASE 8: REFERENCE DATA TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS ref.expense_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    policy_code TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    category_code TEXT,
    max_amount NUMERIC(15,2),
    requires_receipt_above NUMERIC(15,2),
    requires_approval_above NUMERIC(15,2),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE ref.expense_policies ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON ref.expense_policies FOR ALL USING (tenant_id = core.current_tenant_id());
CREATE UNIQUE INDEX IF NOT EXISTS idx_expense_policies_code ON ref.expense_policies(tenant_id, policy_code);

-- ============================================================================
-- PHASE 9: LOGS TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS logs.engine_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    engine_slug TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_data JSONB NOT NULL DEFAULT '{}',
    trace_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Partition by month for efficient retention management
CREATE INDEX IF NOT EXISTS idx_engine_events_tenant_created ON logs.engine_events(tenant_id, created_at);
CREATE INDEX IF NOT EXISTS idx_engine_events_engine ON logs.engine_events(engine_slug, created_at);

CREATE TABLE IF NOT EXISTS logs.agent_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    agent_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    input_data JSONB,
    output_data JSONB,
    duration_ms INTEGER,
    status TEXT NOT NULL,
    error_message TEXT,
    trace_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE logs.agent_actions ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON logs.agent_actions FOR ALL USING (tenant_id = core.current_tenant_id());
CREATE INDEX IF NOT EXISTS idx_agent_actions_tenant_agent ON logs.agent_actions(tenant_id, agent_id, created_at);

-- ============================================================================
-- PHASE 10: UPDATE TRIGGERS
-- ============================================================================

-- Apply updated_at triggers to all tables with updated_at column
DO $$
DECLARE
    tbl RECORD;
BEGIN
    FOR tbl IN
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE schemaname IN ('core', 'expense', 'projects', 'rates', 'doc', 'ref')
        AND tablename NOT IN ('tenants')
    LOOP
        EXECUTE format(
            'DROP TRIGGER IF EXISTS set_updated_at ON %I.%I',
            tbl.schemaname, tbl.tablename
        );
        EXECUTE format(
            'CREATE TRIGGER set_updated_at BEFORE UPDATE ON %I.%I FOR EACH ROW EXECUTE FUNCTION core.set_updated_at()',
            tbl.schemaname, tbl.tablename
        );
    END LOOP;
END $$;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

COMMENT ON SCHEMA core IS 'Platform infrastructure: tenants, employees, audit';
COMMENT ON SCHEMA expense IS 'TE-Cheq expense management domain';
COMMENT ON SCHEMA projects IS 'PPM project portfolio management domain';
COMMENT ON SCHEMA rates IS 'SRM supplier rate management domain';
COMMENT ON SCHEMA doc IS 'Document OCR and processing domain';
COMMENT ON SCHEMA ref IS 'Shared reference data';
COMMENT ON SCHEMA logs IS 'Observability and audit logs';
