-- Finance Tasks Schema
-- Expense management, approvals, and financial workflows

-- ============================================================================
-- EXPENSE CATEGORIES
-- ============================================================================
CREATE TABLE IF NOT EXISTS finance_expense_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    description TEXT,
    gl_account TEXT, -- General ledger account
    requires_receipt BOOLEAN DEFAULT true,
    max_amount DECIMAL(12,2), -- Max per expense
    requires_preapproval_above DECIMAL(12,2), -- Threshold for preapproval
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- EXPENSE CLAIMS
-- ============================================================================
CREATE TABLE IF NOT EXISTS finance_expense_claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_number TEXT UNIQUE NOT NULL,
    employee_id UUID REFERENCES hr_employees(id),
    department_id UUID REFERENCES hr_departments(id),
    -- Claim details
    title TEXT NOT NULL,
    description TEXT,
    claim_date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    currency TEXT DEFAULT 'USD',
    -- Status workflow
    status TEXT DEFAULT 'draft' CHECK (status IN (
        'draft', 'submitted', 'pending_approval', 'approved',
        'rejected', 'paid', 'cancelled'
    )),
    -- Approval tracking
    submitted_at TIMESTAMPTZ,
    current_approver_id UUID REFERENCES hr_employees(id),
    approved_at TIMESTAMPTZ,
    approved_by UUID REFERENCES hr_employees(id),
    rejected_at TIMESTAMPTZ,
    rejected_by UUID REFERENCES hr_employees(id),
    rejection_reason TEXT,
    -- Payment
    paid_at TIMESTAMPTZ,
    payment_reference TEXT,
    payment_method TEXT CHECK (payment_method IN ('bank_transfer', 'check', 'payroll')),
    -- Cost allocation
    cost_center TEXT,
    project_id UUID,
    -- Audit
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- EXPENSE LINE ITEMS
-- ============================================================================
CREATE TABLE IF NOT EXISTS finance_expense_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID REFERENCES finance_expense_claims(id) ON DELETE CASCADE,
    category_id UUID REFERENCES finance_expense_categories(id),
    -- Line details
    description TEXT NOT NULL,
    expense_date DATE NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    exchange_rate DECIMAL(10,6) DEFAULT 1,
    amount_local DECIMAL(12,2), -- Amount in company currency
    -- Receipt
    has_receipt BOOLEAN DEFAULT false,
    receipt_url TEXT,
    receipt_filename TEXT,
    -- OCR extracted data
    ocr_vendor TEXT,
    ocr_amount DECIMAL(12,2),
    ocr_date DATE,
    ocr_confidence DECIMAL(5,2),
    ocr_processed_at TIMESTAMPTZ,
    -- Validation
    is_valid BOOLEAN DEFAULT true,
    validation_notes TEXT,
    -- Audit
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- APPROVAL WORKFLOW RULES
-- ============================================================================
CREATE TABLE IF NOT EXISTS finance_approval_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    rule_type TEXT NOT NULL CHECK (rule_type IN ('expense', 'purchase_order', 'invoice', 'budget')),
    -- Conditions
    min_amount DECIMAL(12,2) DEFAULT 0,
    max_amount DECIMAL(12,2),
    category_ids UUID[], -- Specific categories
    department_ids UUID[], -- Specific departments
    -- Approval chain
    approval_level INT NOT NULL DEFAULT 1,
    approver_type TEXT NOT NULL CHECK (approver_type IN ('manager', 'department_head', 'finance', 'executive', 'specific_user')),
    specific_approver_id UUID REFERENCES hr_employees(id),
    -- Settings
    auto_approve BOOLEAN DEFAULT false,
    requires_all_approvers BOOLEAN DEFAULT false,
    escalation_days INT DEFAULT 3,
    is_active BOOLEAN DEFAULT true,
    priority INT DEFAULT 100, -- Lower = higher priority
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- APPROVAL HISTORY
-- ============================================================================
CREATE TABLE IF NOT EXISTS finance_approval_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type TEXT NOT NULL CHECK (entity_type IN ('expense_claim', 'purchase_order', 'invoice', 'budget_request')),
    entity_id UUID NOT NULL,
    -- Approval details
    approval_level INT NOT NULL,
    approver_id UUID REFERENCES hr_employees(id),
    action TEXT NOT NULL CHECK (action IN ('approved', 'rejected', 'delegated', 'escalated', 'auto_approved')),
    comments TEXT,
    -- Timestamps
    requested_at TIMESTAMPTZ NOT NULL,
    actioned_at TIMESTAMPTZ DEFAULT now(),
    -- Delegation
    delegated_from_id UUID REFERENCES hr_employees(id),
    delegated_to_id UUID REFERENCES hr_employees(id)
);

-- ============================================================================
-- BUDGET ALLOCATIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS finance_budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    fiscal_year INT NOT NULL,
    fiscal_quarter TEXT CHECK (fiscal_quarter IN ('Q1', 'Q2', 'Q3', 'Q4', 'ANNUAL')),
    department_id UUID REFERENCES hr_departments(id),
    cost_center TEXT,
    -- Amounts
    allocated_amount DECIMAL(14,2) NOT NULL,
    committed_amount DECIMAL(14,2) DEFAULT 0, -- Approved but not spent
    spent_amount DECIMAL(14,2) DEFAULT 0, -- Actually spent
    remaining_amount DECIMAL(14,2) GENERATED ALWAYS AS (allocated_amount - committed_amount - spent_amount) STORED,
    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('draft', 'active', 'frozen', 'closed')),
    -- Alerts
    warning_threshold_pct INT DEFAULT 80,
    critical_threshold_pct INT DEFAULT 95,
    -- Audit
    created_by UUID REFERENCES hr_employees(id),
    approved_by UUID REFERENCES hr_employees(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- FINANCE TASKS (Workflow tasks for finance team)
-- ============================================================================
CREATE TABLE IF NOT EXISTS finance_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_number TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    task_type TEXT NOT NULL CHECK (task_type IN (
        'expense_review', 'expense_approval', 'payment_processing',
        'invoice_matching', 'budget_review', 'month_end_close',
        'reconciliation', 'audit_request', 'report_generation', 'other'
    )),
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'on_hold', 'completed', 'cancelled')),
    -- Assignment
    assigned_to UUID REFERENCES hr_employees(id),
    assigned_by UUID REFERENCES hr_employees(id),
    -- Related entity
    related_entity_type TEXT,
    related_entity_id UUID,
    -- Dates
    due_date DATE,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    -- SLA
    sla_hours INT,
    sla_breached BOOLEAN DEFAULT false,
    -- Notes
    notes TEXT,
    resolution_notes TEXT,
    -- Audit
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- FINANCE AUDIT LOG
-- ============================================================================
CREATE TABLE IF NOT EXISTS finance_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    action TEXT NOT NULL,
    changed_by UUID REFERENCES auth.users(id),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    timestamp TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX idx_expense_claims_employee ON finance_expense_claims(employee_id);
CREATE INDEX idx_expense_claims_status ON finance_expense_claims(status);
CREATE INDEX idx_expense_claims_approver ON finance_expense_claims(current_approver_id);
CREATE INDEX idx_expense_lines_claim ON finance_expense_lines(claim_id);
CREATE INDEX idx_approval_history_entity ON finance_approval_history(entity_type, entity_id);
CREATE INDEX idx_finance_tasks_assignee ON finance_tasks(assigned_to);
CREATE INDEX idx_finance_tasks_status ON finance_tasks(status);
CREATE INDEX idx_finance_tasks_due ON finance_tasks(due_date);
CREATE INDEX idx_budgets_department ON finance_budgets(department_id);
CREATE INDEX idx_budgets_year ON finance_budgets(fiscal_year);

-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================
ALTER TABLE finance_expense_claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_expense_lines ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_budgets ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_tasks ENABLE ROW LEVEL SECURITY;

-- Employees can view their own expenses
CREATE POLICY "Employees can view own expenses"
    ON finance_expense_claims FOR SELECT
    USING (
        employee_id IN (SELECT id FROM hr_employees WHERE user_id = auth.uid())
        OR current_approver_id IN (SELECT id FROM hr_employees WHERE user_id = auth.uid())
        OR auth.jwt()->>'role' IN ('finance', 'hr_admin', 'admin')
    );

-- Finance team can view all tasks
CREATE POLICY "Finance can view all tasks"
    ON finance_tasks FOR SELECT
    USING (
        assigned_to IN (SELECT id FROM hr_employees WHERE user_id = auth.uid())
        OR auth.jwt()->>'role' IN ('finance', 'admin')
    );

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Generate claim number
CREATE OR REPLACE FUNCTION generate_claim_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.claim_number := 'EXP-' || to_char(now(), 'YYYYMM') || '-' ||
                        lpad(nextval('expense_claim_seq')::text, 5, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE SEQUENCE IF NOT EXISTS expense_claim_seq START 1;

CREATE TRIGGER expense_claim_number_trigger
BEFORE INSERT ON finance_expense_claims
FOR EACH ROW EXECUTE FUNCTION generate_claim_number();

-- Generate task number
CREATE OR REPLACE FUNCTION generate_task_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.task_number := 'FIN-' || to_char(now(), 'YYYYMMDD') || '-' ||
                       lpad(nextval('finance_task_seq')::text, 4, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE SEQUENCE IF NOT EXISTS finance_task_seq START 1;

CREATE TRIGGER finance_task_number_trigger
BEFORE INSERT ON finance_tasks
FOR EACH ROW EXECUTE FUNCTION generate_task_number();

-- Update claim total when lines change
CREATE OR REPLACE FUNCTION update_claim_total()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE finance_expense_claims
    SET total_amount = (
        SELECT COALESCE(SUM(amount_local), 0)
        FROM finance_expense_lines
        WHERE claim_id = COALESCE(NEW.claim_id, OLD.claim_id)
    ),
    updated_at = now()
    WHERE id = COALESCE(NEW.claim_id, OLD.claim_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER expense_line_total_trigger
AFTER INSERT OR UPDATE OR DELETE ON finance_expense_lines
FOR EACH ROW EXECUTE FUNCTION update_claim_total();
