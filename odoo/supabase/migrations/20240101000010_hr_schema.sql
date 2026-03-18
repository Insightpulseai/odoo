-- HR Schema for InsightPulse
-- Full employee management with org structure

-- Departments
CREATE TABLE IF NOT EXISTS hr_departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    code TEXT UNIQUE,
    parent_id UUID REFERENCES hr_departments(id),
    manager_id UUID, -- References hr_employees
    cost_center TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Job Positions
CREATE TABLE IF NOT EXISTS hr_job_positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    code TEXT UNIQUE,
    department_id UUID REFERENCES hr_departments(id),
    description TEXT,
    requirements TEXT,
    min_salary DECIMAL(12,2),
    max_salary DECIMAL(12,2),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Employees
CREATE TABLE IF NOT EXISTS hr_employees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    employee_number TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    mobile TEXT,
    -- Employment
    department_id UUID REFERENCES hr_departments(id),
    job_position_id UUID REFERENCES hr_job_positions(id),
    manager_id UUID REFERENCES hr_employees(id),
    employment_type TEXT DEFAULT 'full_time' CHECK (employment_type IN ('full_time', 'part_time', 'contract', 'intern')),
    hire_date DATE NOT NULL,
    termination_date DATE,
    -- Personal
    date_of_birth DATE,
    gender TEXT CHECK (gender IN ('male', 'female', 'other', 'prefer_not_to_say')),
    marital_status TEXT CHECK (marital_status IN ('single', 'married', 'divorced', 'widowed')),
    nationality TEXT,
    -- Address
    street TEXT,
    city TEXT,
    state TEXT,
    postal_code TEXT,
    country TEXT DEFAULT 'US',
    -- Emergency Contact
    emergency_contact_name TEXT,
    emergency_contact_phone TEXT,
    emergency_contact_relationship TEXT,
    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'on_leave', 'terminated', 'suspended')),
    is_manager BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Add manager_id FK to departments
ALTER TABLE hr_departments
    ADD CONSTRAINT fk_department_manager
    FOREIGN KEY (manager_id) REFERENCES hr_employees(id);

-- Employee Skills
CREATE TABLE IF NOT EXISTS hr_employee_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES hr_employees(id) ON DELETE CASCADE,
    skill_name TEXT NOT NULL,
    skill_level TEXT CHECK (skill_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
    years_experience INT,
    certified BOOLEAN DEFAULT false,
    certification_date DATE,
    certification_expiry DATE,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(employee_id, skill_name)
);

-- Employee Documents
CREATE TABLE IF NOT EXISTS hr_employee_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES hr_employees(id) ON DELETE CASCADE,
    document_type TEXT NOT NULL CHECK (document_type IN (
        'resume', 'contract', 'id_proof', 'address_proof',
        'education', 'certification', 'performance_review', 'other'
    )),
    name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INT,
    mime_type TEXT,
    expiry_date DATE,
    is_verified BOOLEAN DEFAULT false,
    verified_by UUID REFERENCES hr_employees(id),
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Time Off Types
CREATE TABLE IF NOT EXISTS hr_leave_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    color TEXT DEFAULT '#3b82f6',
    requires_approval BOOLEAN DEFAULT true,
    max_days_per_year INT,
    carry_forward_allowed BOOLEAN DEFAULT false,
    max_carry_forward_days INT DEFAULT 0,
    is_paid BOOLEAN DEFAULT true,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Employee Leave Balances
CREATE TABLE IF NOT EXISTS hr_leave_balances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES hr_employees(id) ON DELETE CASCADE,
    leave_type_id UUID REFERENCES hr_leave_types(id),
    year INT NOT NULL,
    allocated_days DECIMAL(5,2) DEFAULT 0,
    used_days DECIMAL(5,2) DEFAULT 0,
    carried_forward DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(employee_id, leave_type_id, year)
);

-- Leave Requests
CREATE TABLE IF NOT EXISTS hr_leave_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES hr_employees(id) ON DELETE CASCADE,
    leave_type_id UUID REFERENCES hr_leave_types(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days_requested DECIMAL(5,2) NOT NULL,
    reason TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled')),
    approved_by UUID REFERENCES hr_employees(id),
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Attendance Records
CREATE TABLE IF NOT EXISTS hr_attendance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES hr_employees(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    check_in TIMESTAMPTZ,
    check_out TIMESTAMPTZ,
    worked_hours DECIMAL(5,2),
    overtime_hours DECIMAL(5,2) DEFAULT 0,
    status TEXT DEFAULT 'present' CHECK (status IN ('present', 'absent', 'half_day', 'work_from_home', 'on_leave')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(employee_id, date)
);

-- Payroll Periods
CREATE TABLE IF NOT EXISTS hr_payroll_periods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    pay_date DATE NOT NULL,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'processing', 'approved', 'paid', 'cancelled')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Employee Salaries
CREATE TABLE IF NOT EXISTS hr_salaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES hr_employees(id) ON DELETE CASCADE,
    effective_date DATE NOT NULL,
    base_salary DECIMAL(12,2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    pay_frequency TEXT DEFAULT 'monthly' CHECK (pay_frequency IN ('weekly', 'bi_weekly', 'monthly', 'annually')),
    -- Allowances
    housing_allowance DECIMAL(12,2) DEFAULT 0,
    transport_allowance DECIMAL(12,2) DEFAULT 0,
    meal_allowance DECIMAL(12,2) DEFAULT 0,
    other_allowances DECIMAL(12,2) DEFAULT 0,
    -- Deductions
    tax_rate DECIMAL(5,2) DEFAULT 0,
    insurance_deduction DECIMAL(12,2) DEFAULT 0,
    retirement_contribution DECIMAL(12,2) DEFAULT 0,
    other_deductions DECIMAL(12,2) DEFAULT 0,
    -- Bank details
    bank_name TEXT,
    bank_account_number TEXT,
    bank_routing_number TEXT,
    is_current BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Performance Reviews
CREATE TABLE IF NOT EXISTS hr_performance_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES hr_employees(id) ON DELETE CASCADE,
    reviewer_id UUID REFERENCES hr_employees(id),
    review_period_start DATE NOT NULL,
    review_period_end DATE NOT NULL,
    overall_rating INT CHECK (overall_rating BETWEEN 1 AND 5),
    goals_achieved INT CHECK (goals_achieved BETWEEN 0 AND 100),
    strengths TEXT,
    areas_for_improvement TEXT,
    goals_for_next_period TEXT,
    employee_comments TEXT,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'acknowledged', 'completed')),
    submitted_at TIMESTAMPTZ,
    acknowledged_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Training Records
CREATE TABLE IF NOT EXISTS hr_training_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES hr_employees(id) ON DELETE CASCADE,
    training_name TEXT NOT NULL,
    training_type TEXT CHECK (training_type IN ('internal', 'external', 'online', 'certification')),
    provider TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    duration_hours INT,
    cost DECIMAL(10,2),
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled')),
    certificate_url TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- HR Audit Log
CREATE TABLE IF NOT EXISTS hr_audit_log (
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

-- Indexes
CREATE INDEX idx_hr_employees_department ON hr_employees(department_id);
CREATE INDEX idx_hr_employees_manager ON hr_employees(manager_id);
CREATE INDEX idx_hr_employees_status ON hr_employees(status);
CREATE INDEX idx_hr_employees_email ON hr_employees(email);
CREATE INDEX idx_hr_leave_requests_employee ON hr_leave_requests(employee_id);
CREATE INDEX idx_hr_leave_requests_status ON hr_leave_requests(status);
CREATE INDEX idx_hr_attendance_employee_date ON hr_attendance(employee_id, date);
CREATE INDEX idx_hr_salaries_employee ON hr_salaries(employee_id);

-- Row Level Security
ALTER TABLE hr_employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE hr_leave_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE hr_attendance ENABLE ROW LEVEL SECURITY;
ALTER TABLE hr_salaries ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Employees can view own profile"
    ON hr_employees FOR SELECT
    USING (user_id = auth.uid() OR auth.jwt()->>'role' IN ('hr_admin', 'admin'));

CREATE POLICY "Managers can view team"
    ON hr_employees FOR SELECT
    USING (
        manager_id IN (SELECT id FROM hr_employees WHERE user_id = auth.uid())
        OR auth.jwt()->>'role' IN ('hr_admin', 'admin')
    );

CREATE POLICY "Employees can view own leave requests"
    ON hr_leave_requests FOR SELECT
    USING (
        employee_id IN (SELECT id FROM hr_employees WHERE user_id = auth.uid())
        OR auth.jwt()->>'role' IN ('hr_admin', 'admin')
    );

CREATE POLICY "Employees can view own attendance"
    ON hr_attendance FOR SELECT
    USING (
        employee_id IN (SELECT id FROM hr_employees WHERE user_id = auth.uid())
        OR auth.jwt()->>'role' IN ('hr_admin', 'admin')
    );

CREATE POLICY "Only HR can view salaries"
    ON hr_salaries FOR SELECT
    USING (auth.jwt()->>'role' IN ('hr_admin', 'admin', 'finance'));
