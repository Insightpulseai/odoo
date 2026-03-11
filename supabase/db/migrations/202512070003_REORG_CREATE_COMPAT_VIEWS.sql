-- Migration: Create Compatibility Views
-- Version: 202512070003
-- Description: Create views in public schema for backward compatibility
-- Author: Platform Team
-- Date: 2025-12-07
--
-- IMPORTANT: Run this AFTER data migration is complete and validated
-- These views allow legacy code to continue working during transition

-- ============================================================================
-- PHASE 1: RENAME LEGACY TABLES (if they exist)
-- ============================================================================

-- Rename legacy expense_reports to _legacy suffix
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'expense_reports'
        AND table_type = 'BASE TABLE'
    ) THEN
        ALTER TABLE public.expense_reports RENAME TO expense_reports_legacy;
        RAISE NOTICE 'Renamed public.expense_reports to expense_reports_legacy';
    END IF;
END $$;

-- Rename legacy expenses to _legacy suffix
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'expenses'
        AND table_type = 'BASE TABLE'
    ) THEN
        ALTER TABLE public.expenses RENAME TO expenses_legacy;
        RAISE NOTICE 'Renamed public.expenses to expenses_legacy';
    END IF;
END $$;

-- Rename legacy cash_advances to _legacy suffix
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'cash_advances'
        AND table_type = 'BASE TABLE'
    ) THEN
        ALTER TABLE public.cash_advances RENAME TO cash_advances_legacy;
        RAISE NOTICE 'Renamed public.cash_advances to cash_advances_legacy';
    END IF;
END $$;

-- Rename legacy projects to _legacy suffix
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'projects'
        AND table_type = 'BASE TABLE'
    ) THEN
        ALTER TABLE public.projects RENAME TO projects_legacy;
        RAISE NOTICE 'Renamed public.projects to projects_legacy';
    END IF;
END $$;

-- Rename legacy project_members to _legacy suffix
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'project_members'
        AND table_type = 'BASE TABLE'
    ) THEN
        ALTER TABLE public.project_members RENAME TO project_members_legacy;
        RAISE NOTICE 'Renamed public.project_members to project_members_legacy';
    END IF;
END $$;

-- ============================================================================
-- PHASE 2: CREATE COMPATIBILITY VIEWS
-- ============================================================================

-- View: public.expense_reports -> expense.expense_reports
CREATE OR REPLACE VIEW public.expense_reports AS
SELECT
    id,
    tenant_id,
    employee_id,
    report_number,
    description,
    status,
    total_amount,
    currency,
    submitted_at,
    approved_at,
    approved_by,
    policy_flagged,
    created_at,
    updated_at,
    deleted_at
FROM expense.expense_reports;

COMMENT ON VIEW public.expense_reports IS 'Compatibility view - use expense.expense_reports directly';

-- View: public.expenses -> expense.expenses
CREATE OR REPLACE VIEW public.expenses AS
SELECT
    id,
    tenant_id,
    expense_report_id,
    line_seq,
    category_code,
    description,
    amount,
    currency,
    spend_date,
    receipt_document_id,
    policy_violation,
    created_at,
    updated_at,
    deleted_at
FROM expense.expenses;

COMMENT ON VIEW public.expenses IS 'Compatibility view - use expense.expenses directly';

-- View: public.cash_advances -> expense.cash_advances
CREATE OR REPLACE VIEW public.cash_advances AS
SELECT
    id,
    tenant_id,
    employee_id,
    advance_number,
    amount,
    currency,
    purpose,
    status,
    trip_start_date,
    trip_end_date,
    reconciled_amount,
    created_at,
    updated_at,
    deleted_at
FROM expense.cash_advances;

COMMENT ON VIEW public.cash_advances IS 'Compatibility view - use expense.cash_advances directly';

-- View: public.projects -> projects.projects
CREATE OR REPLACE VIEW public.projects AS
SELECT
    id,
    tenant_id,
    odoo_id,
    project_code,
    name,
    description,
    status,
    start_date,
    end_date,
    budget_amount,
    budget_currency,
    project_manager_id,
    created_at,
    updated_at,
    deleted_at
FROM projects.projects;

COMMENT ON VIEW public.projects IS 'Compatibility view - use projects.projects directly';

-- View: public.project_members -> projects.project_members
CREATE OR REPLACE VIEW public.project_members AS
SELECT
    id,
    tenant_id,
    project_id,
    employee_id,
    role,
    allocation_percent,
    start_date,
    end_date,
    created_at,
    updated_at
FROM projects.project_members;

COMMENT ON VIEW public.project_members IS 'Compatibility view - use projects.project_members directly';

-- View: public.vendor_profile -> rates.vendor_profile
CREATE OR REPLACE VIEW public.vendor_profile AS
SELECT
    id,
    tenant_id,
    odoo_partner_id,
    vendor_code,
    name,
    category,
    status,
    rating,
    created_at,
    updated_at,
    deleted_at
FROM rates.vendor_profile;

COMMENT ON VIEW public.vendor_profile IS 'Compatibility view - use rates.vendor_profile directly';

-- View: public.rate_cards -> rates.rate_cards
CREATE OR REPLACE VIEW public.rate_cards AS
SELECT
    id,
    tenant_id,
    vendor_id,
    rate_card_code,
    name,
    effective_from,
    effective_to,
    status,
    approved_by,
    approved_at,
    created_at,
    updated_at,
    deleted_at
FROM rates.rate_cards;

COMMENT ON VIEW public.rate_cards IS 'Compatibility view - use rates.rate_cards directly';

-- ============================================================================
-- PHASE 3: CREATE INSTEAD OF TRIGGERS FOR WRITES
-- ============================================================================

-- Trigger function for expense_reports INSERT
CREATE OR REPLACE FUNCTION public.expense_reports_insert_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO expense.expense_reports (
        id, tenant_id, employee_id, report_number, description, status,
        total_amount, currency, submitted_at, approved_at, approved_by,
        policy_flagged, created_at, updated_at
    ) VALUES (
        COALESCE(NEW.id, gen_random_uuid()), NEW.tenant_id, NEW.employee_id,
        NEW.report_number, NEW.description, COALESCE(NEW.status, 'draft'),
        COALESCE(NEW.total_amount, 0), COALESCE(NEW.currency, 'PHP'),
        NEW.submitted_at, NEW.approved_at, NEW.approved_by,
        COALESCE(NEW.policy_flagged, false),
        COALESCE(NEW.created_at, now()), COALESCE(NEW.updated_at, now())
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER expense_reports_insert
    INSTEAD OF INSERT ON public.expense_reports
    FOR EACH ROW EXECUTE FUNCTION public.expense_reports_insert_trigger();

-- Trigger function for expense_reports UPDATE
CREATE OR REPLACE FUNCTION public.expense_reports_update_trigger()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE expense.expense_reports SET
        employee_id = NEW.employee_id,
        report_number = NEW.report_number,
        description = NEW.description,
        status = NEW.status,
        total_amount = NEW.total_amount,
        currency = NEW.currency,
        submitted_at = NEW.submitted_at,
        approved_at = NEW.approved_at,
        approved_by = NEW.approved_by,
        policy_flagged = NEW.policy_flagged,
        updated_at = now(),
        deleted_at = NEW.deleted_at
    WHERE id = OLD.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER expense_reports_update
    INSTEAD OF UPDATE ON public.expense_reports
    FOR EACH ROW EXECUTE FUNCTION public.expense_reports_update_trigger();

-- Trigger function for projects INSERT
CREATE OR REPLACE FUNCTION public.projects_insert_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO projects.projects (
        id, tenant_id, odoo_id, project_code, name, description,
        status, start_date, end_date, budget_amount, budget_currency,
        project_manager_id, created_at, updated_at
    ) VALUES (
        COALESCE(NEW.id, gen_random_uuid()), NEW.tenant_id, NEW.odoo_id,
        NEW.project_code, NEW.name, NEW.description,
        COALESCE(NEW.status, 'active'), NEW.start_date, NEW.end_date,
        NEW.budget_amount, COALESCE(NEW.budget_currency, 'PHP'),
        NEW.project_manager_id,
        COALESCE(NEW.created_at, now()), COALESCE(NEW.updated_at, now())
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER projects_insert
    INSTEAD OF INSERT ON public.projects
    FOR EACH ROW EXECUTE FUNCTION public.projects_insert_trigger();

-- Trigger function for projects UPDATE
CREATE OR REPLACE FUNCTION public.projects_update_trigger()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE projects.projects SET
        odoo_id = NEW.odoo_id,
        project_code = NEW.project_code,
        name = NEW.name,
        description = NEW.description,
        status = NEW.status,
        start_date = NEW.start_date,
        end_date = NEW.end_date,
        budget_amount = NEW.budget_amount,
        budget_currency = NEW.budget_currency,
        project_manager_id = NEW.project_manager_id,
        updated_at = now(),
        deleted_at = NEW.deleted_at
    WHERE id = OLD.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER projects_update
    INSTEAD OF UPDATE ON public.projects
    FOR EACH ROW EXECUTE FUNCTION public.projects_update_trigger();

-- ============================================================================
-- PHASE 4: GRANT PERMISSIONS
-- ============================================================================

-- Grant SELECT on views to authenticated users
GRANT SELECT ON public.expense_reports TO authenticated;
GRANT SELECT ON public.expenses TO authenticated;
GRANT SELECT ON public.cash_advances TO authenticated;
GRANT SELECT ON public.projects TO authenticated;
GRANT SELECT ON public.project_members TO authenticated;
GRANT SELECT ON public.vendor_profile TO authenticated;
GRANT SELECT ON public.rate_cards TO authenticated;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Log the migration
DO $$
BEGIN
    RAISE NOTICE 'Compatibility views created successfully at %', now();
    RAISE NOTICE 'Legacy tables renamed with _legacy suffix';
    RAISE NOTICE 'INSTEAD OF triggers installed for writes through views';
END $$;
