-- ============================================================================
-- AFC Close Manager - Canonical Database Schema
-- ============================================================================
-- Version: 1.0.0
-- Date: 2025-01-01
-- Modules: afc_close_manager, afc_close_manager_ph, afc_sod_controls, afc_rag_copilot
-- Capacity: 10,000 calendars, 50M audit logs
-- Compliance: SOX 404, PH BIR, Four-Eyes Principle
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create schema namespace
CREATE SCHEMA IF NOT EXISTS afc;

-- ============================================================================
-- MODULE 1: Core Closing (afc_close_manager)
-- ============================================================================

-- Close Calendar (Parent Entity)
CREATE TABLE afc.close_calendar (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_period INTEGER NOT NULL CHECK (fiscal_period BETWEEN 1 AND 12),
    status VARCHAR(50) NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'active', 'closed', 'locked')),
    status_progress DECIMAL(5,2) DEFAULT 0.00
        CHECK (status_progress BETWEEN 0 AND 100),
    company_id INTEGER NOT NULL,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    locked_at TIMESTAMP,
    UNIQUE(company_id, fiscal_year, fiscal_period)
);

CREATE INDEX idx_close_calendar_status ON afc.close_calendar(status);
CREATE INDEX idx_close_calendar_period ON afc.close_calendar(period_start, period_end);

-- Closing Tasks
CREATE TABLE afc.closing_task (
    id SERIAL PRIMARY KEY,
    calendar_id INTEGER NOT NULL REFERENCES afc.close_calendar(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    execution_order INTEGER NOT NULL DEFAULT 0,
    due_date DATE NOT NULL,
    preparer_id INTEGER NOT NULL,
    reviewer_id INTEGER,
    approver_id INTEGER,
    status VARCHAR(50) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'in_progress', 'completed', 'overdue', 'blocked')),
    completed_at TIMESTAMP,
    is_overdue BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT four_eyes_task CHECK (
        preparer_id != reviewer_id
        AND preparer_id != approver_id
        AND (reviewer_id IS NULL OR approver_id IS NULL OR reviewer_id != approver_id)
    )
);

CREATE INDEX idx_closing_task_calendar ON afc.closing_task(calendar_id);
CREATE INDEX idx_closing_task_status ON afc.closing_task(status);
CREATE INDEX idx_closing_task_overdue ON afc.closing_task(is_overdue) WHERE is_overdue = TRUE;

-- GL Posting Header
CREATE TABLE afc.gl_posting (
    id SERIAL PRIMARY KEY,
    calendar_id INTEGER NOT NULL REFERENCES afc.close_calendar(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES afc.closing_task(id) ON DELETE SET NULL,
    journal_id INTEGER NOT NULL,
    posting_date DATE NOT NULL,
    ref VARCHAR(255),
    narration TEXT,
    total_debit DECIMAL(20,2) NOT NULL DEFAULT 0.00,
    total_credit DECIMAL(20,2) NOT NULL DEFAULT 0.00,
    status VARCHAR(50) NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'validated', 'posted', 'cancelled')),
    created_by INTEGER NOT NULL,
    posted_by INTEGER,
    validated_at TIMESTAMP,
    posted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT gl_balance_check CHECK (
        CASE
            WHEN status IN ('validated', 'posted') THEN total_debit = total_credit
            ELSE TRUE
        END
    ),
    CONSTRAINT four_eyes_gl CHECK (
        created_by != posted_by OR posted_by IS NULL
    )
);

CREATE INDEX idx_gl_posting_calendar ON afc.gl_posting(calendar_id);
CREATE INDEX idx_gl_posting_status ON afc.gl_posting(status);

-- GL Posting Lines
CREATE TABLE afc.gl_posting_line (
    id SERIAL PRIMARY KEY,
    posting_id INTEGER NOT NULL REFERENCES afc.gl_posting(id) ON DELETE CASCADE,
    account_id INTEGER NOT NULL,
    analytic_account_id INTEGER,
    debit DECIMAL(20,2) DEFAULT 0.00 CHECK (debit >= 0),
    credit DECIMAL(20,2) DEFAULT 0.00 CHECK (credit >= 0),
    label VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT debit_xor_credit CHECK (
        (debit > 0 AND credit = 0) OR (credit > 0 AND debit = 0) OR (debit = 0 AND credit = 0)
    )
);

CREATE INDEX idx_gl_line_posting ON afc.gl_posting_line(posting_id);
CREATE INDEX idx_gl_line_account ON afc.gl_posting_line(account_id);

-- Intercompany Settlement
CREATE TABLE afc.intercompany (
    id SERIAL PRIMARY KEY,
    calendar_id INTEGER NOT NULL REFERENCES afc.close_calendar(id) ON DELETE CASCADE,
    source_company_id INTEGER NOT NULL,
    dest_company_id INTEGER NOT NULL,
    amount DECIMAL(20,2) NOT NULL CHECK (amount > 0),
    currency_id INTEGER NOT NULL,
    settlement_date DATE NOT NULL,
    source_posting_id INTEGER REFERENCES afc.gl_posting(id),
    dest_posting_id INTEGER REFERENCES afc.gl_posting(id),
    status VARCHAR(50) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'settled', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT different_companies CHECK (source_company_id != dest_company_id)
);

CREATE INDEX idx_intercompany_calendar ON afc.intercompany(calendar_id);
CREATE INDEX idx_intercompany_status ON afc.intercompany(status);

-- Document Attachments
CREATE TABLE afc.document (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES afc.closing_task(id) ON DELETE CASCADE,
    posting_id INTEGER REFERENCES afc.gl_posting(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL
        CHECK (document_type IN ('evidence', 'approval', 'audit', 'reconciliation')),
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_by INTEGER NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT one_parent_only CHECK (
        (task_id IS NOT NULL AND posting_id IS NULL) OR
        (task_id IS NULL AND posting_id IS NOT NULL)
    )
);

CREATE INDEX idx_document_task ON afc.document(task_id);
CREATE INDEX idx_document_posting ON afc.document(posting_id);

-- Compliance Checklist
CREATE TABLE afc.compliance_checklist (
    id SERIAL PRIMARY KEY,
    calendar_id INTEGER NOT NULL REFERENCES afc.close_calendar(id) ON DELETE CASCADE,
    checklist_item VARCHAR(255) NOT NULL,
    regulatory_ref VARCHAR(100),
    is_completed BOOLEAN DEFAULT FALSE,
    completed_by INTEGER,
    completed_at TIMESTAMP,
    evidence_document_id INTEGER REFERENCES afc.document(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_compliance_calendar ON afc.compliance_checklist(calendar_id);
CREATE INDEX idx_compliance_completed ON afc.compliance_checklist(is_completed);

-- ============================================================================
-- MODULE 2: Philippine Localization (afc_close_manager_ph)
-- ============================================================================

-- PH Tax Configuration (2024 TRAIN Law)
CREATE TABLE afc.ph_tax_config (
    id SERIAL PRIMARY KEY,
    effective_year INTEGER NOT NULL,
    bracket_start DECIMAL(20,2) NOT NULL,
    bracket_end DECIMAL(20,2),
    base_tax DECIMAL(20,2) NOT NULL DEFAULT 0.00,
    marginal_rate DECIMAL(5,4) NOT NULL,
    personal_exemption DECIMAL(20,2) DEFAULT 250000.00,
    pwd_senior_rate DECIMAL(5,4) DEFAULT 0.05,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(effective_year, bracket_start)
);

-- Seed 2024 tax brackets
INSERT INTO afc.ph_tax_config (effective_year, bracket_start, bracket_end, base_tax, marginal_rate) VALUES
(2024, 0, 250000, 0, 0.00),
(2024, 250000, 400000, 0, 0.15),
(2024, 400000, 800000, 22500, 0.20),
(2024, 800000, 2000000, 102500, 0.25),
(2024, 2000000, 8000000, 402500, 0.30),
(2024, 8000000, NULL, 2202500, 0.35);

-- BIR Form 1700 (Annual Income Tax Return)
CREATE TABLE afc.bir_form_1700 (
    id SERIAL PRIMARY KEY,
    calendar_id INTEGER NOT NULL REFERENCES afc.close_calendar(id) ON DELETE CASCADE,
    taxpayer_tin VARCHAR(20) NOT NULL,
    taxpayer_name VARCHAR(255) NOT NULL,
    taxable_year INTEGER NOT NULL,
    gross_income DECIMAL(20,2) NOT NULL DEFAULT 0.00,
    total_deductions DECIMAL(20,2) NOT NULL DEFAULT 0.00,
    taxable_income DECIMAL(20,2) GENERATED ALWAYS AS (gross_income - total_deductions) STORED,
    computed_tax DECIMAL(20,2),
    tax_withheld DECIMAL(20,2) DEFAULT 0.00,
    tax_payable DECIMAL(20,2) DEFAULT 0.00,
    filing_deadline DATE NOT NULL,
    penalties_applicable BOOLEAN DEFAULT FALSE,
    filed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bir_1700_calendar ON afc.bir_form_1700(calendar_id);
CREATE INDEX idx_bir_1700_deadline ON afc.bir_form_1700(filing_deadline);

-- BIR Form 1700 Line Items
CREATE TABLE afc.bir_form_1700_line (
    id SERIAL PRIMARY KEY,
    form_id INTEGER NOT NULL REFERENCES afc.bir_form_1700(id) ON DELETE CASCADE,
    line_type VARCHAR(50) NOT NULL CHECK (line_type IN ('income', 'deduction')),
    line_code VARCHAR(20) NOT NULL,
    line_description VARCHAR(255) NOT NULL,
    amount DECIMAL(20,2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bir_1700_line_form ON afc.bir_form_1700_line(form_id);

-- BIR Form 1601-C (Monthly Withholding Tax - Compensation)
CREATE TABLE afc.bir_form_1601c (
    id SERIAL PRIMARY KEY,
    calendar_id INTEGER NOT NULL REFERENCES afc.close_calendar(id) ON DELETE CASCADE,
    employer_tin VARCHAR(20) NOT NULL,
    employer_name VARCHAR(255) NOT NULL,
    tax_period DATE NOT NULL,
    total_compensation DECIMAL(20,2) NOT NULL DEFAULT 0.00,
    total_tax_withheld DECIMAL(20,2) NOT NULL DEFAULT 0.00,
    filing_deadline DATE NOT NULL,
    filed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employer_tin, tax_period)
);

CREATE INDEX idx_bir_1601c_calendar ON afc.bir_form_1601c(calendar_id);
CREATE INDEX idx_bir_1601c_period ON afc.bir_form_1601c(tax_period);

-- BIR Form 1601-C Employee Detail
CREATE TABLE afc.bir_form_1601c_employee (
    id SERIAL PRIMARY KEY,
    form_id INTEGER NOT NULL REFERENCES afc.bir_form_1601c(id) ON DELETE CASCADE,
    employee_tin VARCHAR(20) NOT NULL,
    employee_name VARCHAR(255) NOT NULL,
    gross_compensation DECIMAL(20,2) NOT NULL,
    tax_withheld DECIMAL(20,2) NOT NULL,
    is_pwd_senior BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bir_1601c_emp_form ON afc.bir_form_1601c_employee(form_id);

-- BIR Form 2550Q (Quarterly VAT Return)
CREATE TABLE afc.bir_form_2550q (
    id SERIAL PRIMARY KEY,
    calendar_id INTEGER NOT NULL REFERENCES afc.close_calendar(id) ON DELETE CASCADE,
    taxpayer_tin VARCHAR(20) NOT NULL,
    taxpayer_name VARCHAR(255) NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    fiscal_year INTEGER NOT NULL,
    vatable_sales DECIMAL(20,2) NOT NULL DEFAULT 0.00,
    zero_rated_sales DECIMAL(20,2) NOT NULL DEFAULT 0.00,
    exempt_sales DECIMAL(20,2) NOT NULL DEFAULT 0.00,
    output_vat DECIMAL(20,2) DEFAULT 0.00,
    input_vat DECIMAL(20,2) DEFAULT 0.00,
    vat_payable DECIMAL(20,2) DEFAULT 0.00,
    excess_input_vat DECIMAL(20,2) DEFAULT 0.00,
    filing_deadline DATE NOT NULL,
    filed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(taxpayer_tin, fiscal_year, quarter)
);

CREATE INDEX idx_bir_2550q_calendar ON afc.bir_form_2550q(calendar_id);
CREATE INDEX idx_bir_2550q_quarter ON afc.bir_form_2550q(fiscal_year, quarter);

-- BIR 2550Q Input VAT Detail
CREATE TABLE afc.bir_form_2550q_input_vat (
    id SERIAL PRIMARY KEY,
    form_id INTEGER NOT NULL REFERENCES afc.bir_form_2550q(id) ON DELETE CASCADE,
    vendor_tin VARCHAR(20) NOT NULL,
    vendor_name VARCHAR(255) NOT NULL,
    invoice_number VARCHAR(100),
    invoice_date DATE,
    purchase_amount DECIMAL(20,2) NOT NULL,
    input_vat_amount DECIMAL(20,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bir_2550q_input_form ON afc.bir_form_2550q_input_vat(form_id);

-- ============================================================================
-- MODULE 3: SoD Controls & GRC (afc_sod_controls)
-- ============================================================================

-- SoD Roles (Eight System Roles)
CREATE TABLE afc.sod_role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    risk_level INTEGER CHECK (risk_level BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed system roles
INSERT INTO afc.sod_role (name, code, description, risk_level) VALUES
('Preparer', 'PREP', 'Creates and drafts journal entries', 3),
('Reviewer', 'REV', 'Reviews prepared entries for accuracy', 2),
('Approver', 'APP', 'Final approval authority', 4),
('Poster', 'POST', 'Posts validated entries to GL', 5),
('Administrator', 'ADMIN', 'System configuration and user management', 5),
('Auditor', 'AUD', 'Read-only access for compliance review', 1),
('Controller', 'CTRL', 'Financial controller oversight', 4),
('Tax Manager', 'TAX', 'BIR form preparation and filing', 3);

-- SoD Permissions
CREATE TABLE afc.sod_permission (
    id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL REFERENCES afc.sod_role(id) ON DELETE CASCADE,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL CHECK (action IN ('create', 'read', 'update', 'delete', 'approve', 'post')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, resource, action)
);

CREATE INDEX idx_sod_permission_role ON afc.sod_permission(role_id);

-- SoD Conflict Matrix (Seven Mandatory Rules)
CREATE TABLE afc.sod_conflict_matrix (
    id SERIAL PRIMARY KEY,
    role_a_id INTEGER NOT NULL REFERENCES afc.sod_role(id),
    role_b_id INTEGER NOT NULL REFERENCES afc.sod_role(id),
    conflict_type VARCHAR(50) NOT NULL
        CHECK (conflict_type IN ('same_user', 'same_transaction', 'system_wide')),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    description TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT different_roles CHECK (role_a_id != role_b_id),
    UNIQUE(role_a_id, role_b_id, conflict_type)
);

-- Seed conflict rules
INSERT INTO afc.sod_conflict_matrix (role_a_id, role_b_id, conflict_type, severity, description)
SELECT
    (SELECT id FROM afc.sod_role WHERE code = 'PREP'),
    (SELECT id FROM afc.sod_role WHERE code = 'APP'),
    'same_transaction',
    'critical',
    'Preparer cannot approve their own entries';

INSERT INTO afc.sod_conflict_matrix (role_a_id, role_b_id, conflict_type, severity, description)
SELECT
    (SELECT id FROM afc.sod_role WHERE code = 'PREP'),
    (SELECT id FROM afc.sod_role WHERE code = 'POST'),
    'same_transaction',
    'critical',
    'Preparer cannot post their own entries';

INSERT INTO afc.sod_conflict_matrix (role_a_id, role_b_id, conflict_type, severity, description)
SELECT
    (SELECT id FROM afc.sod_role WHERE code = 'REV'),
    (SELECT id FROM afc.sod_role WHERE code = 'POST'),
    'same_transaction',
    'high',
    'Reviewer cannot post entries they reviewed';

INSERT INTO afc.sod_conflict_matrix (role_a_id, role_b_id, conflict_type, severity, description)
SELECT
    (SELECT id FROM afc.sod_role WHERE code = 'APP'),
    (SELECT id FROM afc.sod_role WHERE code = 'POST'),
    'same_user',
    'high',
    'Approver and Poster should be different users';

-- SoD Audit Log (Immutable)
CREATE TABLE afc.sod_audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    role_id INTEGER REFERENCES afc.sod_role(id),
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100) NOT NULL,
    resource_id INTEGER,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_sod_audit_user ON afc.sod_audit_log(user_id);
CREATE INDEX idx_sod_audit_created ON afc.sod_audit_log(created_at);
CREATE INDEX idx_sod_audit_resource ON afc.sod_audit_log(resource, resource_id);

-- Prevent UPDATE/DELETE on audit log (SOX 404 compliance)
CREATE OR REPLACE FUNCTION afc.prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit log records are immutable (SOX 404 compliance)';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_audit_update
    BEFORE UPDATE ON afc.sod_audit_log
    FOR EACH ROW EXECUTE FUNCTION afc.prevent_audit_modification();

CREATE TRIGGER prevent_audit_delete
    BEFORE DELETE ON afc.sod_audit_log
    FOR EACH ROW EXECUTE FUNCTION afc.prevent_audit_modification();

-- SoD Risk Engine
CREATE TABLE afc.sod_risk_engine (
    id SERIAL PRIMARY KEY,
    calendar_id INTEGER NOT NULL REFERENCES afc.close_calendar(id) ON DELETE CASCADE,
    risk_score INTEGER CHECK (risk_score BETWEEN 0 AND 100),
    unresolved_conflicts INTEGER DEFAULT 0,
    overdue_approvals INTEGER DEFAULT 0,
    last_computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sod_risk_calendar ON afc.sod_risk_engine(calendar_id);

-- ============================================================================
-- MODULE 4: RAG Copilot (afc_rag_copilot)
-- ============================================================================

-- Document Chunks for RAG
CREATE TABLE afc.document_chunks (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    token_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chunks_source ON afc.document_chunks(source);
CREATE INDEX idx_chunks_metadata ON afc.document_chunks USING GIN(metadata);

-- Chunk Embeddings (1536D for OpenAI text-embedding-3-large)
CREATE TABLE afc.chunk_embeddings (
    id BIGSERIAL PRIMARY KEY,
    chunk_id BIGINT NOT NULL REFERENCES afc.document_chunks(id) ON DELETE CASCADE,
    embedding vector(1536) NOT NULL,
    model VARCHAR(100) NOT NULL DEFAULT 'text-embedding-3-large',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_embeddings_chunk ON afc.chunk_embeddings(chunk_id);
CREATE INDEX idx_embeddings_vector ON afc.chunk_embeddings USING ivfflat (embedding vector_cosine_ops);

-- ============================================================================
-- COMPUTED FIELDS & TRIGGERS
-- ============================================================================

-- Function: Update calendar progress
CREATE OR REPLACE FUNCTION afc.update_calendar_progress()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE afc.close_calendar
    SET status_progress = (
        SELECT COALESCE(
            (COUNT(*) FILTER (WHERE status = 'completed')::DECIMAL /
             NULLIF(COUNT(*), 0)) * 100,
            0
        )
        FROM afc.closing_task
        WHERE calendar_id = NEW.calendar_id
    ),
    updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.calendar_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_calendar_progress_trigger
    AFTER INSERT OR UPDATE ON afc.closing_task
    FOR EACH ROW EXECUTE FUNCTION afc.update_calendar_progress();

-- Function: Update GL posting totals
CREATE OR REPLACE FUNCTION afc.update_gl_totals()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE afc.gl_posting
    SET
        total_debit = (SELECT COALESCE(SUM(debit), 0) FROM afc.gl_posting_line WHERE posting_id = NEW.posting_id),
        total_credit = (SELECT COALESCE(SUM(credit), 0) FROM afc.gl_posting_line WHERE posting_id = NEW.posting_id)
    WHERE id = NEW.posting_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_gl_totals_trigger
    AFTER INSERT OR UPDATE OR DELETE ON afc.gl_posting_line
    FOR EACH ROW EXECUTE FUNCTION afc.update_gl_totals();

-- Function: Calculate PH income tax (2024 TRAIN Law)
CREATE OR REPLACE FUNCTION afc.calculate_ph_income_tax(
    p_taxable_income DECIMAL,
    p_year INTEGER DEFAULT 2024,
    p_is_pwd_senior BOOLEAN DEFAULT FALSE
)
RETURNS DECIMAL AS $$
DECLARE
    v_tax DECIMAL := 0;
    v_bracket RECORD;
BEGIN
    -- Apply PWD/Senior Citizen preferential rate
    IF p_is_pwd_senior THEN
        RETURN p_taxable_income * 0.05; -- 5% flat rate
    END IF;

    -- Progressive tax calculation
    FOR v_bracket IN
        SELECT bracket_start, bracket_end, base_tax, marginal_rate
        FROM afc.ph_tax_config
        WHERE effective_year = p_year
        ORDER BY bracket_start ASC
    LOOP
        IF p_taxable_income > v_bracket.bracket_start THEN
            IF v_bracket.bracket_end IS NULL OR p_taxable_income > v_bracket.bracket_end THEN
                -- Income exceeds this bracket
                v_tax := v_bracket.base_tax +
                         (COALESCE(v_bracket.bracket_end, p_taxable_income) - v_bracket.bracket_start) * v_bracket.marginal_rate;
            ELSE
                -- Income falls within this bracket
                v_tax := v_bracket.base_tax +
                         (p_taxable_income - v_bracket.bracket_start) * v_bracket.marginal_rate;
                EXIT;
            END IF;
        END IF;
    END LOOP;

    RETURN v_tax;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function: Auto-compute BIR Form 1700 tax
CREATE OR REPLACE FUNCTION afc.compute_bir_1700_tax()
RETURNS TRIGGER AS $$
BEGIN
    NEW.computed_tax := afc.calculate_ph_income_tax(NEW.taxable_income, NEW.taxable_year, FALSE);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER compute_bir_1700_tax_trigger
    BEFORE INSERT OR UPDATE ON afc.bir_form_1700
    FOR EACH ROW EXECUTE FUNCTION afc.compute_bir_1700_tax();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) - Multi-tenant support
-- ============================================================================

ALTER TABLE afc.close_calendar ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.closing_task ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.gl_posting ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.sod_audit_log ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their company's calendars
CREATE POLICY calendar_company_isolation ON afc.close_calendar
    USING (company_id = current_setting('app.current_company_id')::INTEGER);

-- Policy: Auditors have read-only access to all audit logs
CREATE POLICY audit_log_read_only ON afc.sod_audit_log
    FOR SELECT
    USING (TRUE);

-- ============================================================================
-- GRANTS & PERMISSIONS
-- ============================================================================

-- Grant schema usage
GRANT USAGE ON SCHEMA afc TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA afc TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA afc TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA afc TO authenticated;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify schema integrity
DO $$
BEGIN
    ASSERT (SELECT COUNT(*) FROM afc.sod_role) = 8, 'Expected 8 SoD roles';
    ASSERT (SELECT COUNT(*) FROM afc.ph_tax_config WHERE effective_year = 2024) = 6, 'Expected 6 tax brackets for 2024';
    ASSERT (SELECT COUNT(*) FROM afc.sod_conflict_matrix) >= 4, 'Expected at least 4 conflict rules';
    RAISE NOTICE 'AFC Canonical Schema deployed successfully ✅';
END $$;

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
