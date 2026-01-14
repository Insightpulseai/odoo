-- ═══════════════════════════════════════════════════════════════════════════════
-- Odoo Mirror Schema - Supabase Replication Target
-- ═══════════════════════════════════════════════════════════════════════════════
-- Purpose: Mirror selected Odoo tables for analytics, AI, and cross-app integration
-- Source: Odoo PostgreSQL (159.223.75.148:5432/odoo_core)
-- Destination: Supabase PostgreSQL (spdtwktxdalcfigzeqrz)
-- ETL: supabase/etl with logical replication
-- ═══════════════════════════════════════════════════════════════════════════════

-- Create dedicated schema for Odoo mirror
CREATE SCHEMA IF NOT EXISTS odoo_mirror;

-- Grant permissions
GRANT USAGE ON SCHEMA odoo_mirror TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA odoo_mirror TO postgres;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Core Odoo Tables (Auto-created by ETL)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Note: Tables are auto-created by supabase/etl based on Odoo schema
-- This file defines indexes, views, and analytics helpers ONLY

-- ═══════════════════════════════════════════════════════════════════════════════
-- Indexes (Performance)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Account Move (Invoices)
CREATE INDEX IF NOT EXISTS idx_account_move_partner ON odoo_mirror.account_move(partner_id);
CREATE INDEX IF NOT EXISTS idx_account_move_date ON odoo_mirror.account_move(invoice_date);
CREATE INDEX IF NOT EXISTS idx_account_move_type ON odoo_mirror.account_move(move_type);
CREATE INDEX IF NOT EXISTS idx_account_move_state ON odoo_mirror.account_move(state);

-- Account Move Line (Invoice Lines)
CREATE INDEX IF NOT EXISTS idx_account_move_line_move ON odoo_mirror.account_move_line(move_id);
CREATE INDEX IF NOT EXISTS idx_account_move_line_account ON odoo_mirror.account_move_line(account_id);
CREATE INDEX IF NOT EXISTS idx_account_move_line_partner ON odoo_mirror.account_move_line(partner_id);

-- Partner (Customers/Vendors)
CREATE INDEX IF NOT EXISTS idx_res_partner_name ON odoo_mirror.res_partner(name);
CREATE INDEX IF NOT EXISTS idx_res_partner_vat ON odoo_mirror.res_partner(vat);
CREATE INDEX IF NOT EXISTS idx_res_partner_company_type ON odoo_mirror.res_partner(company_type);

-- Project Task
CREATE INDEX IF NOT EXISTS idx_project_task_project ON odoo_mirror.project_task(project_id);
CREATE INDEX IF NOT EXISTS idx_project_task_user ON odoo_mirror.project_task(user_ids);
CREATE INDEX IF NOT EXISTS idx_project_task_stage ON odoo_mirror.project_task(stage_id);
CREATE INDEX IF NOT EXISTS idx_project_task_deadline ON odoo_mirror.project_task(date_deadline);

-- HR Expense
CREATE INDEX IF NOT EXISTS idx_hr_expense_employee ON odoo_mirror.hr_expense(employee_id);
CREATE INDEX IF NOT EXISTS idx_hr_expense_sheet ON odoo_mirror.hr_expense(sheet_id);
CREATE INDEX IF NOT EXISTS idx_hr_expense_date ON odoo_mirror.hr_expense(date);
CREATE INDEX IF NOT EXISTS idx_hr_expense_state ON odoo_mirror.hr_expense(state);

-- HR Expense Sheet
CREATE INDEX IF NOT EXISTS idx_hr_expense_sheet_employee ON odoo_mirror.hr_expense_sheet(employee_id);
CREATE INDEX IF NOT EXISTS idx_hr_expense_sheet_state ON odoo_mirror.hr_expense_sheet(state);
CREATE INDEX IF NOT EXISTS idx_hr_expense_sheet_date ON odoo_mirror.hr_expense_sheet(accounting_date);

-- ═══════════════════════════════════════════════════════════════════════════════
-- Analytics Views (Superset Ready)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Invoice Summary View
CREATE OR REPLACE VIEW odoo_mirror.v_invoice_summary AS
SELECT
    m.id,
    m.name as invoice_number,
    m.invoice_date,
    m.move_type,
    m.state,
    m.amount_total,
    m.amount_residual,
    p.id as partner_id,
    p.name as partner_name,
    p.vat as partner_vat,
    p.company_type as partner_type,
    CASE
        WHEN m.move_type = 'out_invoice' THEN 'Customer Invoice'
        WHEN m.move_type = 'out_refund' THEN 'Customer Credit Note'
        WHEN m.move_type = 'in_invoice' THEN 'Vendor Bill'
        WHEN m.move_type = 'in_refund' THEN 'Vendor Credit Note'
        ELSE m.move_type
    END as move_type_name,
    CASE
        WHEN m.state = 'draft' THEN 'Draft'
        WHEN m.state = 'posted' THEN 'Posted'
        WHEN m.state = 'cancel' THEN 'Cancelled'
        ELSE m.state
    END as state_name
FROM odoo_mirror.account_move m
JOIN odoo_mirror.res_partner p ON m.partner_id = p.id
WHERE m.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund');

COMMENT ON VIEW odoo_mirror.v_invoice_summary IS 'Invoice summary with partner details for Superset dashboards';

-- Expense Summary View
CREATE OR REPLACE VIEW odoo_mirror.v_expense_summary AS
SELECT
    e.id,
    e.name as description,
    e.date,
    e.total_amount,
    e.untaxed_amount,
    e.state,
    emp.id as employee_id,
    emp.name as employee_name,
    s.id as sheet_id,
    s.name as sheet_name,
    s.state as sheet_state,
    CASE
        WHEN e.state = 'draft' THEN 'To Submit'
        WHEN e.state = 'reported' THEN 'Submitted'
        WHEN e.state = 'approved' THEN 'Approved'
        WHEN e.state = 'done' THEN 'Posted'
        WHEN e.state = 'refused' THEN 'Refused'
        ELSE e.state
    END as state_name
FROM odoo_mirror.hr_expense e
LEFT JOIN odoo_mirror.hr_employee emp ON e.employee_id = emp.id
LEFT JOIN odoo_mirror.hr_expense_sheet s ON e.sheet_id = s.id;

COMMENT ON VIEW odoo_mirror.v_expense_summary IS 'Expense summary with employee and sheet details';

-- Project Task Summary View
CREATE OR REPLACE VIEW odoo_mirror.v_task_summary AS
SELECT
    t.id,
    t.name as task_name,
    t.date_deadline,
    t.priority,
    p.id as project_id,
    p.name as project_name,
    s.id as stage_id,
    s.name as stage_name,
    t.user_ids,
    CASE
        WHEN t.priority = '0' THEN 'Low'
        WHEN t.priority = '1' THEN 'Normal'
        WHEN t.priority = '2' THEN 'High'
        WHEN t.priority = '3' THEN 'Urgent'
        ELSE t.priority
    END as priority_name
FROM odoo_mirror.project_task t
LEFT JOIN odoo_mirror.project_project p ON t.project_id = p.id
LEFT JOIN odoo_mirror.project_task_type s ON t.stage_id = s.id;

COMMENT ON VIEW odoo_mirror.v_task_summary IS 'Project task summary with stage and priority details';

-- Revenue by Partner View
CREATE OR REPLACE VIEW odoo_mirror.v_revenue_by_partner AS
SELECT
    p.id as partner_id,
    p.name as partner_name,
    p.vat,
    COUNT(DISTINCT m.id) as invoice_count,
    SUM(CASE WHEN m.move_type = 'out_invoice' THEN m.amount_total ELSE 0 END) as total_invoiced,
    SUM(CASE WHEN m.move_type = 'out_refund' THEN m.amount_total ELSE 0 END) as total_refunded,
    SUM(CASE WHEN m.move_type = 'out_invoice' THEN m.amount_total ELSE 0 END) -
    SUM(CASE WHEN m.move_type = 'out_refund' THEN m.amount_total ELSE 0 END) as net_revenue,
    MAX(m.invoice_date) as last_invoice_date
FROM odoo_mirror.res_partner p
LEFT JOIN odoo_mirror.account_move m ON p.id = m.partner_id
    AND m.move_type IN ('out_invoice', 'out_refund')
    AND m.state = 'posted'
GROUP BY p.id, p.name, p.vat
HAVING SUM(CASE WHEN m.move_type = 'out_invoice' THEN m.amount_total ELSE 0 END) > 0
ORDER BY net_revenue DESC;

COMMENT ON VIEW odoo_mirror.v_revenue_by_partner IS 'Revenue analysis by partner for BI dashboards';

-- Expense by Employee View
CREATE OR REPLACE VIEW odoo_mirror.v_expense_by_employee AS
SELECT
    emp.id as employee_id,
    emp.name as employee_name,
    COUNT(DISTINCT e.id) as expense_count,
    SUM(e.total_amount) as total_expenses,
    SUM(CASE WHEN e.state = 'approved' THEN e.total_amount ELSE 0 END) as approved_expenses,
    SUM(CASE WHEN e.state = 'done' THEN e.total_amount ELSE 0 END) as posted_expenses,
    MAX(e.date) as last_expense_date
FROM odoo_mirror.hr_employee emp
LEFT JOIN odoo_mirror.hr_expense e ON emp.id = e.employee_id
GROUP BY emp.id, emp.name
HAVING COUNT(DISTINCT e.id) > 0
ORDER BY total_expenses DESC;

COMMENT ON VIEW odoo_mirror.v_expense_by_employee IS 'Expense analysis by employee';

-- ═══════════════════════════════════════════════════════════════════════════════
-- RPC Functions (Analytics API)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Get pending expenses for n8n workflows
CREATE OR REPLACE FUNCTION odoo_mirror.get_pending_expenses(
    p_limit int DEFAULT 20
) RETURNS TABLE (
    expense_id int,
    employee_name text,
    description text,
    amount numeric,
    expense_date date,
    state text
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        emp.name,
        e.name,
        e.total_amount,
        e.date,
        e.state
    FROM odoo_mirror.hr_expense e
    LEFT JOIN odoo_mirror.hr_employee emp ON e.employee_id = emp.id
    WHERE e.state IN ('draft', 'reported')
    ORDER BY e.date DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION odoo_mirror.get_pending_expenses IS 'Get pending expenses for n8n approval workflows';

-- Get overdue tasks
CREATE OR REPLACE FUNCTION odoo_mirror.get_overdue_tasks(
    p_limit int DEFAULT 20
) RETURNS TABLE (
    task_id int,
    task_name text,
    project_name text,
    deadline date,
    days_overdue int
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.id,
        t.name,
        p.name,
        t.date_deadline,
        CURRENT_DATE - t.date_deadline as days_overdue
    FROM odoo_mirror.project_task t
    LEFT JOIN odoo_mirror.project_project p ON t.project_id = p.id
    WHERE t.date_deadline < CURRENT_DATE
        AND t.stage_id NOT IN (
            SELECT id FROM odoo_mirror.project_task_type WHERE fold = true
        )
    ORDER BY days_overdue DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION odoo_mirror.get_overdue_tasks IS 'Get overdue project tasks for Mattermost alerts';

-- Get revenue trends
CREATE OR REPLACE FUNCTION odoo_mirror.get_revenue_trends(
    p_months int DEFAULT 12
) RETURNS TABLE (
    month_date date,
    invoice_count bigint,
    total_revenue numeric
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        DATE_TRUNC('month', m.invoice_date)::date as month_date,
        COUNT(DISTINCT m.id) as invoice_count,
        SUM(m.amount_total) as total_revenue
    FROM odoo_mirror.account_move m
    WHERE m.move_type = 'out_invoice'
        AND m.state = 'posted'
        AND m.invoice_date >= CURRENT_DATE - INTERVAL '1 month' * p_months
    GROUP BY DATE_TRUNC('month', m.invoice_date)
    ORDER BY month_date DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION odoo_mirror.get_revenue_trends IS 'Get monthly revenue trends for dashboards';

-- ═══════════════════════════════════════════════════════════════════════════════
-- Security (RLS + Roles)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Grant view access to superset_readonly
GRANT SELECT ON ALL TABLES IN SCHEMA odoo_mirror TO superset_readonly;
GRANT SELECT ON ALL VIEWS IN SCHEMA odoo_mirror TO superset_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA odoo_mirror GRANT SELECT ON TABLES TO superset_readonly;

-- Grant function execution to n8n_service
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA odoo_mirror TO n8n_service;

-- Enable RLS on sensitive tables (optional - configure per security policy)
-- ALTER TABLE odoo_mirror.account_move ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Analytics access only" ON odoo_mirror.account_move
-- FOR SELECT
-- USING (auth.role() IN ('service_role', 'superset_readonly'));

-- ═══════════════════════════════════════════════════════════════════════════════
-- Integration with ipai_memory (AI Agent Memory)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Trigger: Add memory chunk when invoice is created
CREATE OR REPLACE FUNCTION odoo_mirror.on_invoice_insert()
RETURNS TRIGGER AS $$
DECLARE
    v_session_id uuid;
BEGIN
    -- Get or create session for odoo-sync agent
    SELECT id INTO v_session_id
    FROM ipai_memory.sessions
    WHERE agent_id = 'odoo-sync'
        AND started_at > NOW() - INTERVAL '5 minutes'
    ORDER BY started_at DESC
    LIMIT 1;

    IF v_session_id IS NULL THEN
        INSERT INTO ipai_memory.sessions (agent_id, source, topic)
        VALUES ('odoo-sync', 'odoo-mirror-trigger', 'invoice-sync')
        RETURNING id INTO v_session_id;
    END IF;

    -- Add memory chunk
    INSERT INTO ipai_memory.chunks (session_id, topic, content, importance)
    VALUES (
        v_session_id,
        'invoice-created',
        format('New %s: %s for %s (Amount: %s)',
            CASE
                WHEN NEW.move_type = 'out_invoice' THEN 'customer invoice'
                WHEN NEW.move_type = 'in_invoice' THEN 'vendor bill'
                ELSE NEW.move_type
            END,
            NEW.name,
            (SELECT name FROM odoo_mirror.res_partner WHERE id = NEW.partner_id),
            NEW.amount_total
        ),
        4  -- Important invoices
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Enable trigger (optional - uncomment if needed)
-- CREATE TRIGGER invoice_to_memory
-- AFTER INSERT ON odoo_mirror.account_move
-- FOR EACH ROW
-- WHEN (NEW.move_type IN ('out_invoice', 'in_invoice'))
-- EXECUTE FUNCTION odoo_mirror.on_invoice_insert();

COMMENT ON FUNCTION odoo_mirror.on_invoice_insert IS 'Auto-add invoice creation events to AI memory';

-- ═══════════════════════════════════════════════════════════════════════════════
-- Comments (Documentation)
-- ═══════════════════════════════════════════════════════════════════════════════

COMMENT ON SCHEMA odoo_mirror IS 'Mirror of Odoo tables for analytics and AI integration (replicated via supabase/etl)';

-- ═══════════════════════════════════════════════════════════════════════════════
-- Verification
-- ═══════════════════════════════════════════════════════════════════════════════

-- Verify schema created
SELECT
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'odoo_mirror'
ORDER BY tablename;

-- Verify views created
SELECT
    schemaname,
    viewname
FROM pg_views
WHERE schemaname = 'odoo_mirror'
ORDER BY viewname;

-- Verify functions created
SELECT
    routine_schema,
    routine_name,
    routine_type
FROM information_schema.routines
WHERE routine_schema = 'odoo_mirror'
ORDER BY routine_name;
